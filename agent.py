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
    backend: str = "auto",
    model: Optional[str] = None,
) -> AgentResult:
    language = normalize_language(language)
    if language == "auto":
        language = detect_language_from_text(transcript)

    backend = backend.strip().lower()
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    if backend in ("auto", "gemini") and os.getenv("GEMINI_API_KEY"):
        try:
            return _generate_with_gemini(transcript, language, model)
        except Exception as exc:
            if backend == "gemini":
                raise
            fallback = _local_response(transcript, language)
            fallback.note = "Gemini failed; used local fallback. Error: {}".format(exc)
            return fallback

    return _local_response(transcript, language)


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

    try:
        from google import genai

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(model=model, contents=prompt)
        text = getattr(response, "text", "") or ""
        backend_note = "Generated with Gemini through google-genai."
    except ImportError:
        text = _generate_with_gemini_rest(prompt, model)
        backend_note = "Generated with Gemini through REST fallback."

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
            "maxOutputTokens": 120,
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


def _local_response(transcript: str, language: str) -> AgentResult:
    lowered = transcript.lower()
    if language == "ja":
        if "請求" in transcript or "invoice" in lowered:
            text = "請求書についてですね。確認したい内容をもう少し詳しく教えてください。"
        elif "予約" in transcript or "appointment" in lowered:
            text = "予約変更ですね。ご希望の日付と時間を教えてください。"
        else:
            text = "承知しました。確認したい内容を一つ教えてください。"
    elif language == "zh":
        if "发票" in transcript or "請求" in transcript or "invoice" in lowered:
            text = "您想确认发票相关问题。请告诉我具体想查看哪一项。"
        elif "预约" in transcript or "appointment" in lowered:
            text = "当然可以。您想把预约改到哪一天和几点？"
        else:
            text = "好的。请告诉我您希望我先帮您处理哪一件事。"
    else:
        if "invoice" in lowered or "bill" in lowered:
            text = "Sure. Which invoice detail would you like to check?"
        elif "appointment" in lowered or "reschedule" in lowered:
            text = "Sure. What date and time would you prefer?"
        else:
            text = "Sure. Could you share one more detail so I can help?"

    return AgentResult(
        response_text=text,
        language=language,
        backend="local_rules",
        model="deterministic_support_responses",
        note="Used deterministic fallback; set GEMINI_API_KEY to use Gemini.",
    )
