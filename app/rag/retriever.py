from typing import Any, TypedDict

from app.rag.ingest import get_vectorstore


class RetrievedChunk(TypedDict):
    content: str
    source_file: str
    source_type: str | None
    page_number: int | None
    score: float


def retrieve_context(query: str, k: int = 4) -> list[RetrievedChunk]:
    """Query Chroma and return top-k chunks with source metadata and similarity score."""
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=k)

    chunks: list[RetrievedChunk] = []
    for doc, score in results:
        chunks.append(
            RetrievedChunk(
                content=doc.page_content,
                source_file=doc.metadata.get("source_file")
                or doc.metadata.get("source", "unknown"),
                source_type=doc.metadata.get("source_type"),
                page_number=doc.metadata.get("page_number", doc.metadata.get("page")),
                score=float(score),
            )
        )
    return chunks


def format_retrieved_chunks(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "No relevant documents found."

    parts: list[str] = []
    for chunk in chunks:
        header = f"[Document: {chunk['source_file']}]"
        page = chunk.get("page_number")
        if page is not None:
            display_page = int(page) + 1 if isinstance(page, int) else page
            header += f" (page {display_page}, score={chunk['score']:.4f})"
        else:
            header += f" (score={chunk['score']:.4f})"
        parts.append(f"{header}\n{chunk['content']}")
    return "\n\n".join(parts)
