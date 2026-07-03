import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/api")


st.set_page_config(page_title="Admission Enquiry Assistant", page_icon="🎓", layout="centered")

st.title("🎓 Admission Enquiry Assistant")
st.caption("Ask questions about programs, fees, eligibility, and application deadlines.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for src in message["sources"]:
                    st.text(src.get("content", "")[:300])

if prompt := st.chat_input("Ask about admissions..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {"message": prompt}
                if st.session_state.session_id:
                    payload["session_id"] = st.session_state.session_id

                response = requests.post(f"{API_URL}/chat", json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()

                st.session_state.session_id = data.get("session_id")
                answer = data.get("answer", "No response received.")
                sources = data.get("sources", [])

                st.markdown(answer)
                if sources:
                    with st.expander("Sources"):
                        for src in sources:
                            label = src.get("source", "document")
                            st.text(f"{label}: {src.get('content', '')[:300]}")

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except requests.RequestException as exc:
                st.error(f"Could not reach the API at {API_URL}. Is the server running?\n\n{exc}")
