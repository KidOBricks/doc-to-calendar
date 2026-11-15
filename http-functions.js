import { ok, serverError } from 'wix-http-functions';
import { getSecret } from 'wix-secrets-backend';
import { fetch } from 'wix-fetch';

/*
 * doc-to-calendar extraction backend (Wix Velo HTTP function).
 *
 * POST /_functions/extractCalendar
 * Body: {
 *   prompt: string,                       // extraction instructions built by the web app
 *   text?: string,                        // extracted / pasted text
 *   files?: [{ mimeType, data, label? }], // base64 PDFs / images (overview + detail crops)
 *   fileBase64?: string, mimeType?: string // legacy single-file fields (still accepted)
 * }
 * Response: { events: [...], model, attempts, candidates } on success.
 */

// Model cascade, tried in order. gemini-2.5-flash was removed: it is deprecated and only
// served to legacy users, so the previous fallback failed every time 3.8 was overloaded.
const MODEL_CASCADE = [
  { model: 'gemini-3.8-flash', thinkingLevel: 'HIGH', retries: 1 },
  { model: 'gemini-3.7-flash', thinkingLevel: 'MEDIUM', retries: 0 },
  { model: 'gemini-3.5-flash-lite', thinkingLevel: 'LOW', retries: 0 }
];

const TOTAL_BUDGET_MS = 55000;       // overall time we allow ourselves across all attempts
const MAX_ATTEMPT_MS = 45000;        // cap for a single model call
const MAX_INLINE_BYTES = 18 * 1024 * 1024; // Gemini inline request limit is 20 MB
const RETRYABLE_STATUS = new Set([429, 500, 502, 503, 504]);

const CORS_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*'
};

const DEFAULT_PROMPT = 'Extract every calendar event, deadline, exam, meeting, class, flight, holiday and milestone as JSON {"events": [...]}.';

// Structured output schema: guarantees parseable JSON with the fields the web app expects.
const EVENT_SCHEMA = {
  type: 'OBJECT',
  properties: {
    events: {
      type: 'ARRAY',
      items: {
        type: 'OBJECT',
        properties: {
          name: { type: 'STRING', description: 'Concise event name without category tags or course-code prefix' },
          date: { type: 'STRING', description: 'Start date, YYYY-MM-DD' },
          endDate: { type: 'STRING', nullable: true, description: 'Last day (inclusive) for multi-day events, YYYY-MM-DD, else null' },
          startTime: { type: 'STRING', nullable: true, description: 'HH:MM 24h, or null when no time is given' },
          endTime: { type: 'STRING', nullable: true, description: 'HH:MM 24h, or null' },
          isAllDay: { type: 'BOOLEAN' },
          category: { type: 'STRING', enum: ['DDL', 'MEET', 'EVT', 'FLIGHT', 'HOL', 'MILE'] },
          location: { type: 'STRING' },
          description: { type: 'STRING' }
        },
        required: ['name', 'date', 'isAllDay', 'category']
      }
    }
  },
  required: ['events']
};

function buildParts(body) {
  const parts = [];
  const files = Array.isArray(body.files) && body.files.length
    ? body.files
    : (body.fileBase64 ? [{ mimeType: body.mimeType, data: body.fileBase64 }] : []);

  let totalBytes = 0;
  for (const f of files) {
    const mime = String((f && f.mimeType) || '').toLowerCase();
    // Only PDFs and images can be sent as inlineData.
    if (!f || !f.data || !(mime === 'application/pdf' || mime.startsWith('image/'))) continue;
    totalBytes += Math.ceil(f.data.length * 0.75);
    if (totalBytes > MAX_INLINE_BYTES) break;
    if (f.label) parts.push({ text: String(f.label) });
    parts.push({ inlineData: { mimeType: mime, data: f.data } });
  }

  const textSnippet = body.text
    ? '\n\nDocument / pasted text content (may contain extraction or OCR errors; attached files are the source of truth):\n' + String(body.text).substring(0, 120000)
    : '';
  parts.push({ text: (body.prompt || DEFAULT_PROMPT) + textSnippet });
  return parts;
}

function buildGenerationConfig(cfg, full) {
  const gc = { responseMimeType: 'application/json', maxOutputTokens: 65536 };
  if (full) {
    gc.responseSchema = EVENT_SCHEMA;
    gc.mediaResolution = 'MEDIA_RESOLUTION_HIGH'; // read small text in screenshots / photos
    if (cfg.thinkingLevel) gc.thinkingConfig = { thinkingLevel: cfg.thinkingLevel };
  }
  return gc;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function callGemini(apiKey, model, payload, timeoutMs) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
  const request = fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-goog-api-key': apiKey },
    body: JSON.stringify(payload)
  }).then(async res => {
    let data = {};
    try { data = await res.json(); } catch (e) { data = {}; }
    return { status: res.status, ok: res.ok, data };
  }).catch(err => ({ status: 0, ok: false, data: { error: { message: 'Network error: ' + err.message } } }));

  const timeout = sleep(timeoutMs).then(() => ({
    status: 0, ok: false, timedOut: true,
    data: { error: { message: `Timed out after ${Math.round(timeoutMs / 1000)}s` } }
  }));
  return Promise.race([request, timeout]);
}

// Pulls the answer text out of a generateContent response (skipping thought parts).
function extractText(data) {
  const cand = data && data.candidates && data.candidates[0];
  const parts = (cand && cand.content && cand.content.parts) || [];
  return parts.filter(p => p && typeof p.text === 'string' && !p.thought).map(p => p.text).join('').trim();
}

function parseEvents(text) {
  if (!text) return null;
  const clean = text.replace(/```json/gi, '').replace(/```/g, '').trim();
  let parsed;
  try {
    parsed = JSON.parse(clean);
  } catch (e) {
    const start = clean.indexOf('{');
    const end = clean.lastIndexOf('}');
    if (start === -1 || end <= start) return null;
    try { parsed = JSON.parse(clean.slice(start, end + 1)); } catch (e2) { return null; }
  }
  const events = Array.isArray(parsed) ? parsed : (parsed && parsed.events);
  return Array.isArray(events) ? events : null;
}

export async function post_extractCalendar(request) {
  const startedAt = Date.now();
  const attempts = [];
  try {
    const body = await request.body.json();
    const apiKey = await getSecret('GEMINI_API_KEY');
    const parts = buildParts(body);

    for (const cfg of MODEL_CASCADE) {
      let full = true;           // first try with schema + high media resolution + thinking
      let retriesLeft = cfg.retries;

      while (true) {
        const remaining = TOTAL_BUDGET_MS - (Date.now() - startedAt);
        if (remaining < 4000) break;

        const payload = { contents: [{ role: 'user', parts }], generationConfig: buildGenerationConfig(cfg, full) };
        const t0 = Date.now();
        const res = await callGemini(apiKey, cfg.model, payload, Math.min(MAX_ATTEMPT_MS, remaining));
        const attempt = { model: cfg.model, full, status: res.status, ms: Date.now() - t0 };

        if (res.ok && !res.data.error) {
          const cand = res.data.candidates && res.data.candidates[0];
          const events = parseEvents(extractText(res.data));
          if (events) {
            attempt.events = events.length;
            attempts.push(attempt);
            return ok({
              headers: CORS_HEADERS,
              body: {
                events,
                model: res.data.modelVersion || cfg.model,
                attempts,
                // Gemini-shaped payload kept for older cached copies of the web app.
                candidates: [{ content: { parts: [{ text: JSON.stringify({ events }) }] } }]
              }
            });
          }
          attempt.error = `Unparseable response (finishReason: ${(cand && cand.finishReason) || 'none'})`;
          attempts.push(attempt);
          break; // try the next model
        }

        attempt.error = (res.data && res.data.error && res.data.error.message) || `HTTP ${res.status}`;
        attempts.push(attempt);

        if (res.status === 400 && full) {
          full = false; // model rejected an optional field -> retry with a minimal config
          continue;
        }
        if (RETRYABLE_STATUS.has(res.status) && retriesLeft > 0) {
          retriesLeft--;
          await sleep(1200);
          continue;
        }
        break; // timeout, 403/404, or retries exhausted -> next model
      }
    }

    return serverError({
      headers: CORS_HEADERS,
      body: {
        error: { message: 'All Gemini models failed: ' + attempts.map(a => `${a.model} -> ${a.error}`).join(' | ') },
        attempts
      }
    });
  } catch (err) {
    return serverError({
      headers: CORS_HEADERS,
      body: { error: { message: err.message }, attempts }
    });
  }
}

export function options_extractCalendar(request) {
  return ok({
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
