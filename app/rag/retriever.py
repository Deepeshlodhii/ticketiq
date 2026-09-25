from pathlib import Path

import faiss

from app.rag.embeddings import EmbeddingModel


class KnowledgeBaseRetriever:
    """FAISS-based semantic retriever for the TicketIQ knowledge base."""

    def __init__(self, knowledge_base_path: str = "knowledge_base"):
        self.knowledge_base_path = Path(knowledge_base_path)

        self.embedding_model = EmbeddingModel()

        self.documents: list[dict] = []
        self.index = None

        self._load_documents()
        self._build_index()

    def _load_documents(self):
        """Load markdown knowledge-base documents."""

        for file_path in sorted(self.knowledge_base_path.glob("*.md")):
            content = file_path.read_text(encoding="utf-8").strip()

            if not content:
                continue

            self.documents.append(
                {
                    "source": file_path.name,
                    "content": content,
                }
            )

    def _build_index(self):
        """Create FAISS index from document embeddings."""

        if not self.documents:
            raise ValueError("No knowledge-base documents found.")

        texts = [document["content"] for document in self.documents]

        embeddings = self.embedding_model.encode(texts)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """Retrieve the most relevant KB documents."""

        if self.index is None:
            raise RuntimeError("FAISS index has not been initialized.")

        top_k = min(
            top_k,
            len(self.documents),
        )

        query_embedding = self.embedding_model.encode([query])

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            document = self.documents[index]

            results.append(
                {
                    "source": document["source"],
                    "content": document["content"],
                    "score": round(float(score), 4),
                }
            )

        return results
