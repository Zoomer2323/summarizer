"""Calls the Gemini API and turns the response into {summary, tags[3]}.

Kept as a plain function (no SDK) so the request/response shape is fully
visible and there's nothing to version-pin beyond `requests`.
"""
import json
import os

import requests

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)
REQUEST_TIMEOUT_SECONDS = 15

# Ask Gemini to return JSON that already matches our shape. This is Gemini's
# "structured output" feature -- it constrains the model's output, so we
# mostly avoid the classic "model wrapped JSON in prose/markdown" failure
# mode. We still validate the result ourselves below, because "the model is
# supposed to obey the schema" is not the same guarantee as "it always will".
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
        },
    },
    "required": ["summary", "tags"],
}

PROMPT_TEMPLATE = """You are a content-analysis assistant. Read the text below and produce:
- a concise summary (2-4 sentences)
- exactly three short, relevant tags (lowercase, single words or short phrases)

Text:
\"\"\"
{text}
\"\"\"
"""


class AIServiceError(Exception):
    """Raised for any AI failure we want the API layer to turn into a clean HTTP error."""


def call_gemini(text: str) -> dict:
    """Call Gemini and return a dict like {"summary": str, "tags": [str, str, str]}.

    Raises AIServiceError on timeout, network failure, invalid JSON, or a
    response that doesn't match the expected shape.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIServiceError("GEMINI_API_KEY is not configured on the server.")

    payload = {
        "contents": [{"parts": [{"text": PROMPT_TEMPLATE.format(text=text)}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }

    try:
        response = requests.post(
            GEMINI_API_URL,
            params={"key": api_key},
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise AIServiceError("The AI service timed out. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise AIServiceError("The AI service could not be reached.") from exc

    return _parse_gemini_response(response.json())


def _parse_gemini_response(raw: dict) -> dict:
    try:
        model_text = raw["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIServiceError("The AI response was missing expected content.") from exc

    try:
        parsed = json.loads(model_text)
    except json.JSONDecodeError as exc:
        raise AIServiceError("The AI did not return valid JSON.") from exc

    return _validate_ai_output(parsed)


def _validate_ai_output(parsed: dict) -> dict:
    """Ensure the parsed payload has a non-empty summary and exactly 3 tags."""
    if not isinstance(parsed, dict):
        raise AIServiceError("The AI response was not a JSON object.")

    summary = parsed.get("summary")
    tags = parsed.get("tags")

    if not isinstance(summary, str) or not summary.strip():
        raise AIServiceError("The AI response did not include a summary.")

    if not isinstance(tags, list) or len(tags) != 3:
        raise AIServiceError("The AI did not return exactly three tags.")

    clean_tags = [t.strip() for t in tags if isinstance(t, str) and t.strip()]
    if len(clean_tags) != 3:
        raise AIServiceError("The AI returned one or more empty tags.")

    return {"summary": summary.strip(), "tags": clean_tags}
