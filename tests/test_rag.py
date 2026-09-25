from app.rag.retriever import KnowledgeBaseRetriever


def test_retriever_returns_results():
    retriever = KnowledgeBaseRetriever()

    results = retriever.retrieve(
        "I was charged twice and need a refund.",
        top_k=3,
    )

    assert len(results) == 3

    sources = [result["source"] for result in results]

    assert "billing.md" in sources or "refunds.md" in sources


def test_retriever_respects_top_k():
    retriever = KnowledgeBaseRetriever()

    results = retriever.retrieve(
        "I cannot login to my account.",
        top_k=2,
    )

    assert len(results) == 2
