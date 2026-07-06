from __future__ import annotations

import os
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Optional

from languages import detect_language_from_text, normalize_language


@dataclass
class AgentResult:
    response_text: str
    language: str
    backend: str
    model: str
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def generate_response(
    transcript: str,
    language: str = "auto",
    model: Optional[str] = None,
) -> AgentResult:
    language = normalize_language(language)
    if language == "auto":
        language = detect_language_from_text(transcript)

    model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("Gemini API key required for the agent stage. Set GEMINI_API_KEY.")
    return _generate_with_gemini(transcript, language, model)


def _generate_with_gemini(transcript: str, language: str, model: str) -> AgentResult:
    prompt = """You are a concise enterprise customer-support voice assistant.
Reply in the same language as the user.
Keep the answer under two sentences.
Do not invent account-specific facts.
If information is missing, ask one clear follow-up question.

Language code: {language}
User transcript: {transcript}
""".format(
        language=language,
        transcript=transcript,
    )

    text = _generate_with_gemini_rest(prompt, model)
    backend_note = "Generated with Gemini through REST."

    text = text.strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return AgentResult(
        response_text=text,
        language=language,
        backend="gemini",
        model=model,
        note=backend_note,
    )


def _generate_with_gemini_rest(prompt: str, model: str) -> str:
    api_key = os.environ["GEMINI_API_KEY"]
    encoded_model = urllib.parse.quote(model, safe="")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + encoded_model
        + ":generateContent?key="
        + urllib.parse.quote(api_key, safe="")
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 256,
            "thinkingConfig": {
                "thinkingBudget": 0,
            },
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            error_data = json.loads(body)
            message = error_data.get("error", {}).get("message", body)
            status = error_data.get("error", {}).get("status", "HTTP_ERROR")
        except json.JSONDecodeError:
            message = body
            status = "HTTP_ERROR"
        raise RuntimeError("Gemini API error {} {}: {}".format(exc.code, status, message)) from exc

    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    return "".join(part.get("text", "") for part in parts)
