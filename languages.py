from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_LANGUAGES = ("en", "ja", "zh")


@dataclass(frozen=True)
class LanguageProfile:
    code: str
    name: str
    macos_voice: str
    sample_text: str


LANGUAGE_PROFILES = {
    "en": LanguageProfile(
        code="en",
        name="English",
        macos_voice="Samantha",
        sample_text="I want to reschedule my appointment.",
    ),
    "ja": LanguageProfile(
        code="ja",
        name="Japanese",
        macos_voice="Kyoko",
        sample_text="請求書について確認したいです。",
    ),
    "zh": LanguageProfile(
        code="zh",
        name="Chinese",
        macos_voice="Ting-Ting",
        sample_text="我想更改我的预约时间。",
    ),
}


def normalize_language(language: str | None) -> str:
    if not language or language == "auto":
        return "auto"

    value = language.strip().lower()
    aliases = {
        "eng": "en",
        "english": "en",
        "japanese": "ja",
        "jp": "ja",
        "jpn": "ja",
        "zh-cn": "zh",
        "zh_cn": "zh",
        "chinese": "zh",
        "mandarin": "zh",
        "cn": "zh",
    }
    value = aliases.get(value, value)
    if value not in SUPPORTED_LANGUAGES:
        raise ValueError(
            "Unsupported language '{}'. Use one of: auto, {}".format(
                language, ", ".join(SUPPORTED_LANGUAGES)
            )
        )
    return value


def detect_language_from_text(text: str, fallback: str = "en") -> str:
    has_hiragana_or_katakana = any(
        "\u3040" <= char <= "\u30ff" for char in text
    )
    if has_hiragana_or_katakana:
        return "ja"

    has_cjk = any("\u4e00" <= char <= "\u9fff" for char in text)
    if has_cjk:
        return "zh"

    try:
        return normalize_language(fallback)
    except ValueError:
        return "en"


def language_profile(language: str) -> LanguageProfile:
    code = normalize_language(language)
    if code == "auto":
        code = "en"
    return LANGUAGE_PROFILES[code]
