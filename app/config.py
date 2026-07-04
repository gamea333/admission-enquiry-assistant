import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str
    debug: bool
    google_api_key: str
    database_url: str
    documents_dir: Path
    vectorstore_dir: Path
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    llm_model: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Admission Enquiry Assistant"),
        debug=os.getenv("DEBUG", "false").lower() in ("1", "true", "yes"),
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        database_url=os.getenv(
            "DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'data' / 'admissions.db'}"
        ),
        documents_dir=Path(os.getenv("DOCUMENTS_DIR", PROJECT_ROOT / "data" / "documents")),
        vectorstore_dir=Path(os.getenv("VECTORSTORE_DIR", PROJECT_ROOT / "data" / "vectorstore")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
        embedding_model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"),
        llm_model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
    )
