"""Embeds text using the multilingual-e5-large sentence-transformers model.

The model is loaded lazily (on first use) rather than at import time, so
importing this module stays fast and doesn't require the model weights to be
present just to boot the app.
"""
import asyncio

from app.core.config import settings

EMBEDDING_DIM = 1024

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.embedding_model)
    return _model


def _encode(texts: list[str], is_query: bool) -> list[list[float]]:
    prefix = "query: " if is_query else "passage: "
    prefixed = [f"{prefix}{text}" for text in texts]
    model = _get_model()
    embeddings = model.encode(prefixed, convert_to_numpy=True, normalize_embeddings=True)
    return [embedding.tolist() for embedding in embeddings]


async def embed_texts(texts: list[str], is_query: bool) -> list[list[float]]:
    """Embeds a batch of texts, prefixing per the e5 model's convention.

    e5 models require a "query: " or "passage: " prefix depending on whether
    the text is a search query or a document being indexed.
    """
    if not texts:
        return []

    return await asyncio.to_thread(_encode, texts, is_query)
