from functools import lru_cache
from typing import List
from fastembed import TextEmbedding
from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    """Load and cache the local ONNX embedding model once per process."""
    return TextEmbedding(model_name=settings.EMBEDDING_MODEL)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Convert a list of document passages into 384-dim vectors."""
    model = get_embedding_model()
    return [vec.tolist() for vec in model.passage_embed(texts)]


def embed_query(query: str) -> List[float]:
    """Convert a user search query into a 384-dim vector."""
    model = get_embedding_model()
    return next(model.query_embed(query)).tolist()
