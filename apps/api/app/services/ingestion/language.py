"""Language detection for ingested documents, restricted to the languages the
platform supports (Arabic and English) for speed and accuracy.
"""
from lingua import Language, LanguageDetectorBuilder

_detector = (
    LanguageDetectorBuilder.from_languages(Language.ENGLISH, Language.ARABIC)
    .with_preloaded_language_models()
    .build()
)

_LANGUAGE_CODES = {
    Language.ENGLISH: "en",
    Language.ARABIC: "ar",
}


def detect_language(text: str) -> str:
    """Returns "ar", "en", or "auto" if detection is inconclusive."""
    if not text or not text.strip():
        return "auto"

    language = _detector.detect_language_of(text)
    if language is None:
        return "auto"

    return _LANGUAGE_CODES.get(language, "auto")
