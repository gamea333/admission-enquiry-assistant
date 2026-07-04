from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.db.models import get_session_factory
from app.db.queries import (
    extract_area_name,
    extract_class_name,
    get_fees_for_class,
    get_seat_availability,
    get_transport_for_area,
    search_faq,
)
from app.rag.retriever import retrieve_context

SYSTEM_PROMPT = """You are the admission enquiry assistant for Greenfield International School (Nursery to Grade 10).

Your job is to answer parent questions using ONLY the context provided below. The context contains two types of sources:
- [Database] lines: live data from the school ERP (seats, fees, transport, FAQs)
- [Document: filename] lines: excerpts from official school documents (prospectus, policies, fee tables, timings)

Rules:
1. Answer ONLY using information present in the provided context. Do not invent or assume facts.
2. If the context does not contain enough information to answer, say clearly: "I don't have that information in our records." Then suggest contacting the admissions office at +91 80 4123 5600 or admissions@greenfield.edu.in.
3. At the end of every answer, include a line starting with "Sources:" that lists the exact [Database] labels and/or [Document: filename] entries you relied on.
4. Be concise, accurate, and friendly. Format Indian Rupee amounts with the ₹ symbol and thousands separators.
5. For seat availability, state clearly whether a grade is full or how many seats remain.
6. For transport, state whether the route is available or waitlist-only when that information is present.
7. Do not mention internal system details (vector store, SQL, embeddings, or intent detection)."""

FEE_KEYWORDS = frozenset(
    {"fee", "fees", "tuition", "cost", "price", "admission fee", "deposit", "charges"}
)
SEAT_KEYWORDS = frozenset(
    {"seat", "seats", "available", "availability", "vacancy", "vacancies", "full", "open"}
)
TRANSPORT_KEYWORDS = frozenset(
    {"transport", "bus", "route", "pickup", "pick-up", "shuttle"}
)
FAQ_KEYWORDS = frozenset(
    {
        "uniform",
        "holiday",
        "holidays",
        "sibling",
        "discount",
        "extracurricular",
        "activity",
        "visit",
        "tour",
        "campus",
        "lunch",
        "meal",
        "withdraw",
        "refund",
    }
)
DOCUMENT_KEYWORDS = frozenset(
    {
        "policy",
        "process",
        "procedure",
        "eligibility",
        "document",
        "documents",
        "prospectus",
        "timing",
        "timings",
        "curriculum",
        "mission",
        "facility",
        "facilities",
        "required",
        "deadline",
        "date",
        "apply",
        "application",
    }
)


def _query_matches_keywords(query: str, keywords: frozenset[str]) -> bool:
    lowered = query.lower()
    return any(keyword in lowered for keyword in keywords)


def detect_intent(query: str) -> dict[str, bool]:
    """Lightweight keyword-based intent routing."""
    needs_db = (
        _query_matches_keywords(query, FEE_KEYWORDS)
        or _query_matches_keywords(query, SEAT_KEYWORDS)
        or _query_matches_keywords(query, TRANSPORT_KEYWORDS)
        or _query_matches_keywords(query, FAQ_KEYWORDS)
    )
    needs_documents = _query_matches_keywords(query, DOCUMENT_KEYWORDS) or not needs_db

    # Broad questions benefit from both sources
    if needs_db and (
        _query_matches_keywords(query, DOCUMENT_KEYWORDS)
        or _query_matches_keywords(query, {"admission", "admit", "enrol", "enroll"})
    ):
        needs_documents = True

    return {"db": needs_db, "documents": needs_documents}


def _format_fee_line(fees: dict) -> str:
    return (
        f"[Database] {fees['class_name']} Section {fees['section']} fees: "
        f"admission ₹{fees['admission_fee']:,}, "
        f"tuition ₹{fees['tuition_fee_annual']:,}/year, "
        f"transport ₹{fees['transport_fee_annual']:,}/year"
    )


def _format_seat_line(seats: dict) -> str:
    if seats["is_full"]:
        status = "FULL — no seats available"
    else:
        status = f"{seats['seats_available']} seat(s) available"
    return (
        f"[Database] {seats['class_name']} Section {seats['section']} seats: "
        f"{seats['seats_filled']}/{seats['capacity']} filled — {status}"
    )


def _format_transport_lines(routes: list[dict]) -> list[str]:
    lines: list[str] = []
    for route in routes:
        status = "available" if route["available"] else "NOT available (waitlist only)"
        lines.append(
            f"[Database] Transport in {route['area_name']} — {route['pickup_point']}: "
            f"₹{route['monthly_fee']:,}/month — {status}"
        )
    return lines


def _format_faq_lines(faqs: list[dict]) -> list[str]:
    return [
        f"[Database] FAQ ({faq['category']}): Q: {faq['question']} A: {faq['answer']}"
        for faq in faqs
    ]


def _build_db_context(query: str, db) -> tuple[list[str], list[str]]:
    context_lines: list[str] = []
    source_labels: list[str] = []

    class_name = extract_class_name(query, db)
    area_name = extract_area_name(query, db)

    if class_name and _query_matches_keywords(query, FEE_KEYWORDS):
        fees = get_fees_for_class(db, class_name)
        if fees:
            context_lines.append(_format_fee_line(fees))
            source_labels.append(f"Database: {class_name} fees")

    if class_name and _query_matches_keywords(query, SEAT_KEYWORDS):
        seats = get_seat_availability(db, class_name)
        if seats:
            context_lines.append(_format_seat_line(seats))
            source_labels.append(f"Database: {class_name} seat availability")

    if area_name and _query_matches_keywords(query, TRANSPORT_KEYWORDS):
        routes = get_transport_for_area(db, area_name)
        if routes:
            context_lines.extend(_format_transport_lines(routes))
            source_labels.append(f"Database: transport in {area_name}")

    if _query_matches_keywords(query, FAQ_KEYWORDS):
        faqs = search_faq(db, query, limit=3)
        if faqs:
            context_lines.extend(_format_faq_lines(faqs))
            source_labels.append("Database: FAQ matches")

    # Seat/fee questions without explicit grade — try extracted class anyway
    if class_name and not context_lines:
        if _query_matches_keywords(query, {"admission", "admit", "enrol", "enroll"}):
            seats = get_seat_availability(db, class_name)
            if seats:
                context_lines.append(_format_seat_line(seats))
                source_labels.append(f"Database: {class_name} seat availability")

    return context_lines, source_labels


def _build_document_context(query: str, k: int = 4) -> tuple[list[str], list[str]]:
    chunks = retrieve_context(query, k=k)
    context_lines: list[str] = []
    source_labels: list[str] = []

    for chunk in chunks:
        page = chunk.get("page_number")
        page_suffix = ""
        if page is not None:
            display_page = int(page) + 1 if isinstance(page, int) else page
            page_suffix = f", page {display_page}"
        label = f"Document: {chunk['source_file']}"
        context_lines.append(
            f"[Document: {chunk['source_file']}{page_suffix}] (score={chunk['score']:.4f})\n"
            f"{chunk['content']}"
        )
        if label not in source_labels:
            source_labels.append(label)

    return context_lines, source_labels


def answer_query(query: str) -> dict[str, Any]:
    """
    Route the query to structured DB lookups and/or document retrieval,
    then generate an answer grounded in the combined context.
    """
    settings = get_settings()
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is not set. Add it to your .env file.")

    intent = detect_intent(query)
    context_blocks: list[str] = []
    sources: list[str] = []

    session = get_session_factory()()
    try:
        if intent["db"]:
            db_lines, db_sources = _build_db_context(query, session)
            context_blocks.extend(db_lines)
            sources.extend(db_sources)
    finally:
        session.close()

    if intent["documents"]:
        try:
            doc_lines, doc_sources = _build_document_context(query)
            context_blocks.extend(doc_lines)
            sources.extend(doc_sources)
        except Exception:
            # Vector store missing or unreadable — continue with DB context only
            pass

    if not sources:
        return {
            "answer": (
                "I don't have that information in our records. "
                "Please contact the admissions office at +91 80 4123 5600 "
                "or admissions@greenfield.edu.in."
            ),
            "sources": [],
        }

    combined_context = "\n\n".join(context_blocks)
    user_prompt = f"""Context:
{combined_context}

User question: {query}

Answer the question following all rules in your instructions."""

    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )
    response = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )

    # Deduplicate sources while preserving order
    unique_sources = list(dict.fromkeys(sources))

    return {"answer": response.content, "sources": unique_sources}


# Backward-compatible alias used by the API router
def generate_answer(query: str) -> tuple[str, list[str]]:
    result = answer_query(query)
    return result["answer"], result["sources"]
