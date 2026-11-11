import { ok, serverError } from 'wix-http-functions';
import { getSecret } from 'wix-secrets-backend';
import { fetch } from 'wix-fetch';

export async function post_extractCalendar(request) {
  try {
    const body = await request.body.json();
    const apiKey = await getSecret('GEMINI_API_KEY');

    // List of model candidates in order of preference
    const models = ['gemini-3.8-flash', 'gemini-1.5-flash', 'gemini-2.0-flash'];
    let lastError = null;

    for (const model of models) {
      try {
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
        const response = await fetch(geminiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: body.prompt }] }],
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
        lastError = data.error || { message: `Model ${model} returned status ${response.status}` };
      } catch (e) {
        lastError = e;
      }
    }

    // If all models failed, return server error with details so frontend can fall back to local parser
    return serverError({
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: { error: lastError }
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

// CORS Preflight handler
export function options_extractCalendar(request) {
  return ok({
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
