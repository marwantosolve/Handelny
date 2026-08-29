"""Token-count-based chunking with overlap, using tiktoken for token counting.

This is intentionally simple (not semantic/heading-aware) per the v1 scope
decision: pages are concatenated (with a page-boundary marker so words don't
merge across pages) into one token stream, then split into fixed-size,
overlapping windows.
"""
import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")


def chunk_text(pages: list[dict], chunk_size_tokens: int, overlap_tokens: int) -> list[dict]:
    """Splits page text into overlapping, fixed-size token windows.

    Returns a list of:
        {"content": str, "chunk_index": int, "page_number": int | None, "token_count": int}

    `page_number` reflects the page that the *start* of the chunk falls on.
    """
    if chunk_size_tokens <= 0:
        raise ValueError("chunk_size_tokens must be positive")

    # Overlap must be strictly smaller than the window, or we'd never advance.
    overlap_tokens = max(0, min(overlap_tokens, chunk_size_tokens - 1))

    all_tokens: list[int] = []
    token_page_numbers: list[int | None] = []

    for page in pages:
        content = page.get("content", "")
        if not content or not content.strip():
            continue

        # Prepend a separator (except for the very first page) so tokens
        # from adjacent pages don't merge into a single word on decode.
        text = content if not all_tokens else "\n\n" + content
        tokens = _ENCODING.encode(text)
        if not tokens:
            continue

        all_tokens.extend(tokens)
        token_page_numbers.extend([page.get("page_number")] * len(tokens))

    if not all_tokens:
        return []

    step = chunk_size_tokens - overlap_tokens
    total = len(all_tokens)

    chunks: list[dict] = []
    start = 0
    chunk_index = 0

    while start < total:
        end = min(start + chunk_size_tokens, total)
        window_tokens = all_tokens[start:end]
        content = _ENCODING.decode(window_tokens).strip()

        if content:
            chunks.append(
                {
                    "content": content,
                    "chunk_index": chunk_index,
                    "page_number": token_page_numbers[start],
                    "token_count": len(window_tokens),
                }
            )
            chunk_index += 1

        if end >= total:
            break
        start += step

    return chunks
