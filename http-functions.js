import { ok, serverError } from 'wix-http-functions';
import { getSecret } from 'wix-secrets-backend';
import { fetch } from 'wix-fetch';

export async function post_extractCalendar(request) {
  try {
    const body = await request.body.json();
    const apiKey = await getSecret('GEMINI_API_KEY');

    // Use Gemini 3.8 Flash with High thinking effort
    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=${apiKey}`;

    const parts = [];

    // Pass inlineData ONLY for Gemini-supported binary multimodal MIME types (PDF and images)
    const mime = (body.mimeType || '').toLowerCase();
    if (body.fileBase64 && (mime === 'application/pdf' || mime.startsWith('image/'))) {
      parts.push({
        inlineData: {
          mimeType: body.mimeType,
          data: body.fileBase64
        }
      });
    }

    // Add prompt and extracted/pasted text
    const textSnippet = body.text ? "\n\nDocument / Pasted Content:\n" + body.text.substring(0, 60000) : "";
    parts.push({
      text: (body.prompt || "Extract calendar events as JSON.") + textSnippet
    });

    const response = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: parts }],
        generationConfig: {
          responseMimeType: "application/json",
          temperature: 0.1,
          thinkingConfig: {
            thinkingLevel: "HIGH"
          }
        }
      })
    });

    const data = await response.json();

    // If gemini-3.8-flash High succeeded, return directly
    if (response.ok && !data.error && data.candidates && data.candidates[0]) {
      return ok({
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: data
      });
    }

    // Fast fallback to gemini-2.5-flash / gemini-1.5-flash if 3.8 has a temporary spike
    const fallbackUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
    const fallbackRes = await fetch(fallbackUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: parts }],
        generationConfig: {
          responseMimeType: "application/json"
        }
      })
    });

    const fallbackData = await fallbackRes.json();
    if (fallbackRes.ok && !fallbackData.error && fallbackData.candidates && fallbackData.candidates[0]) {
      return ok({
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: fallbackData
      });
    }

    return serverError({
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: { error: data.error || fallbackData.error || { message: `Status ${response.status}` } }
    });
  } catch (err) {
    return serverError({
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: { error: err.message }
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
