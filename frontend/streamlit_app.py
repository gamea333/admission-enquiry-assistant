import os
import uuid

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "https://admission-enquiry-assistant.onrender.com/")

SAMPLE_QUESTIONS = [
    "Are seats available in Grade 7?",
    "What are the fees for Grade 5?",
    "Is transport available in Whitefield?",
    "What is the sibling discount policy?",
    "What documents are required for admission?",
    "What are the school timings for the primary section?",
]

st.set_page_config(
    page_title="Greenfield Admissions Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
            --bg-page: #0b0f17;
            --bg-card: #121826;
            --bg-sidebar: #0f1420;
            --bg-elevated: #1a2233;
            --bg-input: #161d2b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --border: #243044;
            --border-strong: #334155;
            --accent: #60a5fa;
            --accent-soft: #1e293b;
            --accent-hover: #93c5fd;
            --user-bg: #172554;
            --user-border: #1d4ed8;
            --assistant-bg: #151c2b;
            --assistant-border: #243044;
            --success: #34d399;
            --success-bg: #052e1c;
            --danger: #f87171;
            --danger-bg: #3b1111;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
            --radius-lg: 16px;
            --radius-md: 10px;
            --radius-pill: 999px;
            --content-width: 760px;
        }

        html, body, [class*="css"] {
            font-family: var(--font-sans);
            color: var(--text-primary);
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        .main,
        [data-testid="stMain"] {
            background: var(--bg-page) !important;
            color: var(--text-primary);
        }

        /* Bottom chat input bar — match page background */
        [data-testid="stBottom"],
        [data-testid="stBottom"] > div,
        [data-testid="stBottomBlockContainer"],
        section[data-testid="stSidebar"] + div [data-testid="stVerticalBlock"] {
            background: var(--bg-page) !important;
        }

        .stChatFloatingInputContainer,
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] {
            background: transparent !important;
        }

        /* Main column card */
        .main .block-container {
            max-width: var(--content-width);
            padding-top: 1rem !important;
            padding-bottom: 1.5rem !important;
            background: var(--bg-card) !important;
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            margin-top: 0.75rem;
            margin-bottom: 0.5rem;
        }

        /* Header */
        .app-header {
            margin-bottom: 0.35rem;
        }

        .app-header h1 {
            font-size: 1.65rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
            color: var(--text-primary) !important;
            margin: 0 0 0.35rem 0 !important;
            padding: 0 !important;
            line-height: 1.25 !important;
        }

        .app-subtitle {
            font-size: 0.98rem;
            line-height: 1.55;
            color: var(--text-secondary);
            margin: 0 0 0.65rem 0;
            font-weight: 400;
        }

        .app-badge-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }

        .powered-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            color: #a5b4fc;
            background: #1e1b4b;
            border: 1px solid #4338ca;
            border-radius: var(--radius-pill);
            padding: 0.28rem 0.65rem;
        }

        /* Empty state */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 1.75rem 1.25rem 1.25rem;
            margin: 0.25rem 0 0.5rem;
            border: 1px dashed var(--border-strong);
            border-radius: var(--radius-md);
            background: linear-gradient(180deg, #141b29 0%, #111827 100%);
        }

        .empty-state-icon {
            font-size: 1.75rem;
            line-height: 1;
            margin-bottom: 0.55rem;
        }

        .empty-state-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.3rem;
        }

        .empty-state-copy {
            font-size: 0.92rem;
            color: var(--text-muted);
            max-width: 32rem;
            line-height: 1.5;
        }

        /* Chat bubbles */
        [data-testid="stChatMessage"] {
            border-radius: var(--radius-md) !important;
            padding: 0.85rem 1rem !important;
            margin-bottom: 0.65rem !important;
            border: 1px solid transparent !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: var(--user-bg) !important;
            border-color: var(--user-border) !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: var(--assistant-bg) !important;
            border-color: var(--assistant-border) !important;
        }

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] code {
            color: var(--text-primary) !important;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        [data-testid="chatAvatarIcon-user"],
        [data-testid="chatAvatarIcon-assistant"] {
            border-radius: 8px !important;
            background: var(--bg-elevated) !important;
        }

        /* Sources expander */
        [data-testid="stChatMessage"] details {
            margin-top: 0.35rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-elevated);
        }

        [data-testid="stChatMessage"] summary {
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-muted);
        }

        /* Chat input */
        [data-testid="stChatInput"] {
            padding-top: 0.25rem;
            background: transparent !important;
        }

        [data-testid="stChatInput"] textarea {
            border-radius: 12px !important;
            border: 1px solid var(--border-strong) !important;
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
            caret-color: var(--accent) !important;
            font-family: var(--font-sans) !important;
            font-size: 0.95rem !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: var(--text-muted) !important;
        }

        [data-testid="stChatInput"] textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.18) !important;
        }

        [data-testid="stChatInputSubmitButton"] button {
            background: var(--accent) !important;
            color: #0b1220 !important;
            border: none !important;
        }

        [data-testid="stChatInputSubmitButton"] button:hover {
            background: var(--accent-hover) !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
            background: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.25rem;
            background: transparent !important;
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stCaption {
            color: var(--text-muted) !important;
        }

        .sidebar-brand {
            margin-bottom: 0.15rem;
        }

        .sidebar-brand h3 {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0 0 0.2rem 0;
            line-height: 1.3;
        }

        .sidebar-brand p {
            font-size: 0.84rem;
            color: var(--text-muted);
            margin: 0;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.78rem;
            font-weight: 600;
            border-radius: var(--radius-pill);
            padding: 0.32rem 0.7rem;
            margin: 0.15rem 0 0.85rem;
            border: 1px solid transparent;
        }

        .status-pill--ok {
            color: var(--success);
            background: var(--success-bg);
            border-color: #065f46;
        }

        .status-pill--error {
            color: var(--danger);
            background: var(--danger-bg);
            border-color: #7f1d1d;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
        }

        .status-dot--ok { background: var(--success); }
        .status-dot--error { background: var(--danger); }

        .sidebar-section-title {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin: 0.2rem 0 0.15rem;
        }

        .sidebar-section-copy {
            font-size: 0.82rem;
            color: var(--text-muted);
            margin: 0 0 0.65rem;
        }

        /* Sample question buttons */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--border) !important;
            background: var(--bg-elevated) !important;
            color: var(--text-primary) !important;
            font-family: var(--font-sans) !important;
            font-size: 0.86rem !important;
            font-weight: 500 !important;
            text-align: left !important;
            padding: 0.62rem 0.8rem !important;
            margin-bottom: 0.35rem !important;
            line-height: 1.4 !important;
            transition: all 0.15s ease !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25) !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: #3b82f6 !important;
            background: #1e293b !important;
            color: var(--accent-hover) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
        }

        [data-testid="stSidebar"] .stButton > button:active {
            transform: translateY(0);
        }

        /* Ghost clear button */
        div[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
            border-radius: 8px !important;
            border: 1px dashed var(--border-strong) !important;
            background: transparent !important;
            color: var(--text-muted) !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            padding: 0.35rem 0.6rem !important;
            margin-bottom: 0.85rem !important;
            box-shadow: none !important;
        }

        div[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
            color: var(--text-secondary) !important;
            background: var(--bg-elevated) !important;
            border-color: var(--border-strong) !important;
            transform: none !important;
        }

        /* Footer */
        .app-footer {
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.35rem;
            padding-top: 0.25rem;
        }

        /* Misc Streamlit widgets */
        .stSpinner > div {
            color: var(--text-muted) !important;
        }

        [data-testid="stExpander"] {
            background: var(--bg-elevated) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }

        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] p,
        [data-testid="stExpander"] li {
            color: var(--text-secondary) !important;
        }

        /* Hide Streamlit chrome for demo polish */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }

        hr {
            margin: 0.85rem 0 !important;
            border-color: var(--border) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None


def check_api_health() -> bool:
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


def call_chat_api(query: str) -> dict:
    payload = {
        "query": query,
        "session_id": st.session_state.session_id,
    }
    response = requests.post(f"{API_URL}/chat", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


def render_sources(sources: list[str]) -> None:
    with st.expander("Sources", expanded=False):
        for source in sources:
            st.markdown(f"- `{source}`")


def process_user_query(query: str) -> None:
    st.session_state.messages.append({"role": "user", "content": query})

    try:
        with st.spinner("Looking that up..."):
            data = call_chat_api(query)
        answer = data.get("answer", "No response received.")
        sources = data.get("sources", [])
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
    except requests.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"Sorry, the server returned an error.\n\n`{detail}`",
                "sources": [],
            }
        )
    except requests.RequestException:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    f"I couldn't reach the API at `{API_URL}`. "
                    "Make sure the FastAPI server is running:\n\n"
                    "`uvicorn app.main:app --reload --port 8000`"
                ),
                "sources": [],
            }
        )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <h3>Greenfield International School</h3>
                <p>Admission Enquiry Assistant</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Clear chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

        api_ok = check_api_health()
        if api_ok:
            st.markdown(
                '<span class="status-pill status-pill--ok">'
                '<span class="status-dot status-dot--ok"></span>API connected</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-pill status-pill--error">'
                '<span class="status-dot status-dot--error"></span>API offline</span>',
                unsafe_allow_html=True,
            )
            st.caption("Start the server with `uvicorn app.main:app --reload`")

        st.markdown('<p class="sidebar-section-title">Sample questions</p>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-section-copy">Click any question to ask</p>', unsafe_allow_html=True)

        for question in SAMPLE_QUESTIONS:
            if st.button(question, key=f"sample_{question}", use_container_width=True):
                st.session_state.pending_query = question
                st.rerun()


init_session_state()
render_sidebar()

st.markdown(
    """
    <div class="app-header">
        <h1>🎓 Admission Enquiry Assistant</h1>
        <p class="app-subtitle">
            Ask about seats, fees, transport, policies, and more — answers are grounded
            in school documents and live admission data.
        </p>
        <div class="app-badge-row">
            <span class="powered-pill">⚡ Powered by Gemini + RAG</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-title">How can I help you today?</div>
            <p class="empty-state-copy">
                Ask me anything about admissions, fees, seat availability, transport routes,
                or school policies — or pick a sample question from the sidebar.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            render_sources(message["sources"])

if st.session_state.pending_query:
    process_user_query(st.session_state.pending_query)
    st.session_state.pending_query = None
    st.rerun()

if prompt := st.chat_input("Ask about admissions..."):
    process_user_query(prompt)
    st.rerun()

st.markdown(
    '<div class="app-footer">Greenfield International School · Gemini 2.5 Flash + Chroma RAG</div>',
    unsafe_allow_html=True,
)
