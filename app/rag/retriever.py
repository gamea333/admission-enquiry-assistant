from langchain_core.documents import Document

from app.config import get_settings
from app.rag.ingest import get_vectorstore


def get_retriever(k: int = 4):
    settings = get_settings()
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_context(query: str, k: int = 4) -> list[Document]:
    retriever = get_retriever(k=k)
    return retriever.invoke(query)


def format_retrieved_docs(docs: list[Document]) -> str:
    if not docs:
        return "No relevant documents found."

    parts = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page")
        header = f"[{i}] Source: {source}"
        if page is not None:
            header += f" (page {page + 1})"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n".join(parts)
