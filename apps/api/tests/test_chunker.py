"""Tests for the token-count-based chunker.

Requires `tiktoken` (a real project dependency), which may not be installed
in every sandbox. These are meant to run via the full docker-compose stack.
"""
import tiktoken

from app.services.ingestion.chunker import chunk_text

_ENCODING = tiktoken.get_encoding("cl100k_base")


def test_chunk_text_empty_pages_returns_empty_list():
    assert chunk_text([], chunk_size_tokens=100, overlap_tokens=10) == []


def test_chunk_text_skips_blank_pages():
    pages = [
        {"content": "   \n\n  ", "page_number": 1},
        {"content": "Hello world.", "page_number": 2},
    ]
    chunks = chunk_text(pages, chunk_size_tokens=100, overlap_tokens=10)

    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 2
    assert "Hello world" in chunks[0]["content"]


def test_chunk_text_single_short_page_produces_one_chunk():
    pages = [{"content": "The quick brown fox jumps over the lazy dog.", "page_number": 1}]
    chunks = chunk_text(pages, chunk_size_tokens=50, overlap_tokens=10)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["chunk_index"] == 0
    assert chunk["page_number"] == 1
    assert chunk["token_count"] > 0
    assert "fox" in chunk["content"]


def test_chunk_text_long_text_produces_multiple_sequential_chunks():
    words = " ".join(f"word{i}" for i in range(300))
    pages = [{"content": words, "page_number": 1}]

    chunks = chunk_text(pages, chunk_size_tokens=50, overlap_tokens=10)

    assert len(chunks) > 1
    assert [chunk["chunk_index"] for chunk in chunks] == list(range(len(chunks)))
    # Every window but the last should be exactly the requested size.
    for chunk in chunks[:-1]:
        assert chunk["token_count"] == 50


def test_chunk_text_overlap_shares_tail_and_head_tokens():
    words = " ".join(f"word{i}" for i in range(300))
    pages = [{"content": words, "page_number": 1}]

    chunks = chunk_text(pages, chunk_size_tokens=50, overlap_tokens=10)

    first_tokens = _ENCODING.encode(chunks[0]["content"])
    second_tokens = _ENCODING.encode(chunks[1]["content"])

    # The last `overlap_tokens` of chunk N should equal the first
    # `overlap_tokens` of chunk N+1.
    assert first_tokens[-10:] == second_tokens[:10]


def test_chunk_text_tracks_page_number_across_boundaries():
    pages = [
        {"content": "First page content. " * 40, "page_number": 1},
        {"content": "Second page content. " * 40, "page_number": 2},
    ]
    chunks = chunk_text(pages, chunk_size_tokens=50, overlap_tokens=5)

    page_numbers = {chunk["page_number"] for chunk in chunks}
    assert page_numbers == {1, 2}

    first_page_2_index = next(
        index for index, chunk in enumerate(chunks) if chunk["page_number"] == 2
    )
    assert all(chunk["page_number"] == 1 for chunk in chunks[:first_page_2_index])


def test_chunk_text_clamps_overlap_to_avoid_infinite_loop():
    # overlap_tokens >= chunk_size_tokens must not stall progress.
    pages = [{"content": "word " * 200, "page_number": 1}]
    chunks = chunk_text(pages, chunk_size_tokens=20, overlap_tokens=20)

    assert len(chunks) > 0
