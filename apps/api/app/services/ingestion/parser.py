"""Extracts raw page text from supported document types (PDF, TXT, MD)."""


async def parse_document(file_bytes: bytes, file_type: str) -> list[dict]:
    """Returns a list of pages: [{"content": str, "page_number": int | None}].

    PDF documents are split into one entry per page (1-indexed). Plain text
    and Markdown documents are treated as a single "page" with no page
    number, since they have no inherent pagination.
    """
    normalized_type = file_type.lower().lstrip(".")

    if normalized_type == "pdf":
        return _parse_pdf(file_bytes)
    if normalized_type in ("txt", "md"):
        return _parse_text(file_bytes)

    raise ValueError(f"Unsupported file type for parsing: {file_type}")


def _parse_pdf(file_bytes: bytes) -> list[dict]:
    import fitz  # pymupdf

    pages: list[dict] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for index, page in enumerate(doc):
            pages.append({"content": page.get_text(), "page_number": index + 1})
    return pages


def _parse_text(file_bytes: bytes) -> list[dict]:
    try:
        content = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = file_bytes.decode("latin-1")
    return [{"content": content, "page_number": None}]
