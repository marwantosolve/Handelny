"""Text normalization applied to parsed document pages before chunking."""
import re
import unicodedata

_TRAILING_WHITESPACE_RE = re.compile(r"[ \t]+\n")
_MULTIPLE_SPACES_RE = re.compile(r"[ \t]{2,}")
_EXCESSIVE_BLANK_LINES_RE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Normalizes whitespace/newlines and unicode form.

    - Applies NFC unicode normalization.
    - Converts CRLF/CR to LF.
    - Strips trailing whitespace on each line.
    - Collapses runs of 2+ spaces/tabs into one space.
    - Collapses 3+ consecutive blank lines into a single blank line.
    - Strips leading/trailing whitespace from the whole text.
    """
    if not text:
        return ""

    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _TRAILING_WHITESPACE_RE.sub("\n", normalized)
    normalized = _MULTIPLE_SPACES_RE.sub(" ", normalized)
    normalized = _EXCESSIVE_BLANK_LINES_RE.sub("\n\n", normalized)

    return normalized.strip()
