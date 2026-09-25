import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL


class EmbeddingModel:
    """Wrapper around the Sentence Transformer embedding model."""

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def encode(self, texts: list[str]) -> np.ndarray:
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.astype("float32")
