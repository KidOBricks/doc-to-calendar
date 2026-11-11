import { ok, serverError } from 'wix-http-functions';
import { getSecret } from 'wix-secrets-backend';
import { fetch } from 'wix-fetch';

export async function post_extractCalendar(request) {
  try {
    const body = await request.body.json();
    const apiKey = await getSecret('GEMINI_API_KEY');

    // Build multimodal parts: attach base64 file data if available
    const parts = [];
    if (body.fileBase64 && body.mimeType) {
      parts.push({
        inlineData: {
          mimeType: body.mimeType,
          data: body.fileBase64
        }
      });
    }

    const docText = body.text ? `\n\nDocument Content:\n${body.text.substring(0, 30000)}` : '';
    parts.push({ text: (body.prompt || 'Extract all calendar events into a JSON array of objects.') + docText });

    // Primary Call: Gemini 3.8 Flash
    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=${apiKey}`;

    const response = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: parts }],
        generationConfig: {
          responseMimeType: "application/json",
          temperature: 0.1
        }
      })
    });

    const data = await response.json();

    if (response.ok && !data.error && data.candidates && data.candidates[0]) {
      return ok({
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: data
      });
    }

    // Fallback: If generateContent requested Interactions API
    if (data.error && (data.error.code === 404 || (data.error.message && data.error.message.includes('Interactions')))) {
      const interactionsUrl = `https://generativelanguage.googleapis.com/v1beta/interactions?key=${apiKey}`;
      const intResponse = await fetch(interactionsUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Api-Revision': '2026-05-20'
        },
        body: JSON.stringify({
          model: 'gemini-3.8-flash',
          input: body.prompt + docText,
          generation_config: {
            temperature: 0.1
          }
        })
      });

      const intData = await intResponse.json();
      if (intResponse.ok && !intData.error) {
        return ok({
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          },
          body: intData
        });
      }
    }

    return serverError({
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: { error: data.error || { message: `Gemini status ${response.status}` } }
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
