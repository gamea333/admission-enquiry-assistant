from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.db.models import get_session_factory
from app.db.queries import get_all_programs, get_upcoming_deadlines, search_faqs
from app.rag.retriever import format_retrieved_docs, retrieve_context

SYSTEM_PROMPT = """You are a helpful admission enquiry assistant for a university.
Answer questions about programs, eligibility, fees, deadlines, and application procedures.
Use the provided context from documents and structured database facts.
If you cannot find the answer in the context, say so honestly and suggest contacting the admissions office.
Be concise, accurate, and friendly."""


def _build_structured_context() -> str:
    session = get_session_factory()()
    try:
        programs = get_all_programs(session)
        deadlines = get_upcoming_deadlines(session)
        lines = ["## Programs"]
        for p in programs:
            lines.append(
                f"- {p.name} ({p.degree}): {p.duration_years} years, "
                f"fee ${p.tuition_fee:,}/year, intake {p.intake_month}. "
                f"Eligibility: {p.eligibility}"
            )
        lines.append("\n## Upcoming Deadlines")
        for d in deadlines:
            lines.append(f"- {d.program_name} ({d.round}): {d.deadline_date.strftime('%Y-%m-%d')}")
        return "\n".join(lines)
    finally:
        session.close()


def generate_answer(query: str) -> tuple[str, list[Document]]:
    settings = get_settings()
    docs = retrieve_context(query)
    doc_context = format_retrieved_docs(docs)
    structured_context = _build_structured_context()

    faq_hits = []
    session = get_session_factory()()
    try:
        faq_hits = search_faqs(session, query, limit=3)
    finally:
        session.close()

    faq_context = "\n".join(f"Q: {f.question}\nA: {f.answer}" for f in faq_hits)

    prompt = f"""{SYSTEM_PROMPT}

## Structured Database Facts
{structured_context}

## FAQ Matches
{faq_context or "None"}

## Retrieved Document Excerpts
{doc_context}

## User Question
{query}

Provide a clear, helpful answer:"""

    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )
    response = llm.invoke(prompt)
    return response.content, docs
