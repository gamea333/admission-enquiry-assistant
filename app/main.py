import logging
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import PROJECT_ROOT, get_settings
from app.db.seed import seed_sample_data
from app.rag.ingest import ingest
from app.router import router

logger = logging.getLogger(__name__)

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8501",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8501",
]

SUPPORTED_DOC_SUFFIXES = {".pdf", ".docx", ".txt"}


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def _resolve_sqlite_path(database_url: str) -> Path | None:
    if not database_url.startswith("sqlite"):
        return None

    raw_path = database_url.split("://", 1)[1]
    # Windows absolute: /C:/Dev/... or C:/Dev/...
    if len(raw_path) >= 3 and raw_path[0] == "/" and raw_path[2] == ":":
        return Path(raw_path[1:])
    if len(raw_path) >= 2 and raw_path[1] == ":":
        return Path(raw_path)
    if raw_path.startswith("/"):
        return Path(raw_path)

    normalized = raw_path.lstrip("./")
    return PROJECT_ROOT / normalized


def _database_exists(database_url: str) -> bool:
    db_path = _resolve_sqlite_path(database_url)
    return db_path is not None and db_path.is_file()


def _vectorstore_exists(vectorstore_dir: Path) -> bool:
    if not vectorstore_dir.is_dir():
        return False
    return any(p.name != ".gitkeep" for p in vectorstore_dir.iterdir())


def _documents_exist(documents_dir: Path) -> bool:
    if not documents_dir.is_dir():
        return False
    return any(
        p.is_file() and p.suffix.lower() in SUPPORTED_DOC_SUFFIXES
        for p in documents_dir.iterdir()
    )


def _ensure_sample_documents(documents_dir: Path) -> None:
    if _documents_exist(documents_dir):
        logger.info("Sample documents already present in %s — skipping generation", documents_dir)
        return

    script_path = PROJECT_ROOT / "scripts" / "generate_sample_docs.py"
    logger.info("No documents found in %s — generating sample documents", documents_dir)
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"generate_sample_docs.py failed (exit {result.returncode}): {result.stderr or result.stdout}"
        )
    if result.stdout.strip():
        logger.info(result.stdout.strip())


def _initialize_database() -> str:
    settings = get_settings()

    if _database_exists(settings.database_url):
        logger.info("SQLite database already exists — skipping seed")
        return "ready"

    db_path = _resolve_sqlite_path(settings.database_url)
    logger.info("SQLite database not found at %s — running seed", db_path)
    seed_sample_data()
    logger.info("Database seeded successfully")
    return "seeded"


def _initialize_vectorstore() -> str:
    settings = get_settings()

    if _vectorstore_exists(settings.vectorstore_dir):
        logger.info("Vector store already present at %s — skipping ingest", settings.vectorstore_dir)
        return "ready"

    if not settings.google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set — cannot build vector store on first run. "
            "Set the environment variable and restart."
        )

    _ensure_sample_documents(settings.documents_dir)

    logger.info("Vector store missing or empty at %s — running ingest", settings.vectorstore_dir)
    chunk_counts = ingest()
    total_chunks = sum(chunk_counts.values())
    logger.info("Ingest complete — %s chunks embedded", total_chunks)
    return "ready"


def run_startup_setup() -> None:
    db_status = "unknown"
    vectorstore_status = "unknown"

    try:
        db_status = _initialize_database()
    except Exception:
        db_status = "failed"
        logger.exception("Database initialization failed")

    try:
        vectorstore_status = _initialize_vectorstore()
    except Exception:
        vectorstore_status = "failed"
        logger.exception("Vector store initialization failed")

    logger.info(
        "Startup complete: DB %s, vectorstore %s",
        db_status,
        vectorstore_status,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    logger.info("Running first-run startup checks...")
    run_startup_setup()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")
    return app


app = create_app()
