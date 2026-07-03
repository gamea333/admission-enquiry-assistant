from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings


def load_documents(documents_dir: Path | None = None) -> list:
    settings = get_settings()
    docs_path = documents_dir or settings.documents_dir
    docs_path.mkdir(parents=True, exist_ok=True)

    documents = []
    for file_path in sorted(docs_path.iterdir()):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file_path))
        elif suffix == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
        else:
            continue
        documents.extend(loader.load())

    return documents


def chunk_documents(documents: list) -> list:
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(documents)


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )


def build_vectorstore(documents_dir: Path | None = None) -> Chroma:
    settings = get_settings()
    settings.vectorstore_dir.mkdir(parents=True, exist_ok=True)

    documents = load_documents(documents_dir)
    if not documents:
        raise ValueError(f"No documents found in {settings.documents_dir}")

    chunks = chunk_documents(documents)
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(settings.vectorstore_dir),
    )
    return vectorstore


def get_vectorstore() -> Chroma:
    settings = get_settings()
    settings.vectorstore_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        persist_directory=str(settings.vectorstore_dir),
        embedding_function=get_embeddings(),
    )


if __name__ == "__main__":
    store = build_vectorstore()
    print(f"Ingested {store._collection.count()} chunks into vector store.")
