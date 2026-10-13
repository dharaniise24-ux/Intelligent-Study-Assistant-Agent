import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

from knowledge_base import (
    STUDY_AGENT_INSTRUCTION,
    PROMPT_EVALUATOR_INSTRUCTION,
)


# 1. SETUP & MINIMALIST UI STYLING

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="Study Assistant Agent",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Clean, modern CSS with zero clutter
st.markdown(
    """
    <style>
    /* Clean layout bounds */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 800px;
    }
    /* Compact coaching badge */
    .prompt-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        background: #2563eb;
        color: #ffffff;
        margin-bottom: 0.4rem;
    }
    /* Suggested prompt box */
    .prompt-box {
        background-color: rgba(37, 99, 235, 0.08);
        border: 1px dashed rgba(37, 99, 235, 0.4);
        padding: 0.6rem 0.9rem;
        border-radius: 8px;
        font-family: monospace;
        font-size: 0.85rem;
        margin-top: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. STATE & CLIENT INITIALIZATION
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""

if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None


@st.cache_resource
def get_client():
    if not api_key:
        return None
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=120000),
    )


client = get_client()
MODEL_NAME = "gemini-3.5-flash-lite"


def extract_document_text(file) -> str:
    """Extract text from uploaded PDF or TXT files."""
    text = ""
    try:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            text = file.read().decode("utf-8", errors="replace")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
    return text.strip()


def evaluate_prompt(user_text: str) -> dict:
    """Classifies the prompt engineering type and provides quick improvements."""
    try:
        res = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_EVALUATOR_INSTRUCTION,
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        return json.loads(res.text)
    except Exception:
        return {
            "category": "Zero-shot Prompting",
            "tip": "Add constraints like output format or difficulty level to get better answers.",
            "better_prompt": f"Explain '{user_text}' in simple terms with a code example.",
        }


# -----------------------------------------------------------------------------
# 3. SIDEBAR (ONLY FOR UPLOADING & CLEARING)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("📚 Study Material")
    uploaded = st.file_uploader(
        "Upload Notes (PDF / TXT):",
        type=["pdf", "txt", "md"],
        help="The agent will answer questions based on this file.",
    )

    if uploaded is not None:
        if st.session_state.uploaded_name != uploaded.name:
            st.session_state.uploaded_text = extract_document_text(uploaded)
            st.session_state.uploaded_name = uploaded.name
            st.success(f"Attached: {uploaded.name}")
    else:
        st.session_state.uploaded_text = ""
        st.session_state.uploaded_name = None

    if st.session_state.uploaded_name:
        st.caption(f"Currently referencing **{st.session_state.uploaded_name}**")
        if st.button("Remove file", use_container_width=True):
            st.session_state.uploaded_text = ""
            st.session_state.uploaded_name = None
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# 4. CHAT INTERFACE
# -----------------------------------------------------------------------------
st.title("🤖 Study Assistant")
if st.session_state.uploaded_name:
    st.caption(f"📄 Grounded in your notes: **{st.session_state.uploaded_name}**")
else:
    st.caption("Ask any computer science concept, lab query, or course question.")

if not api_key:
    st.error("Missing `GEMINI_API_KEY`. Check your `.env` file.")
    st.stop()

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Show prompt coaching drawer if present
        if "coaching" in msg:
            c = msg["coaching"]
            with st.expander(f"💡 Prompt Coach • Detected: **{c.get('category')}**"):
                st.write(f"**Tip:** {c.get('tip')}")
                st.markdown(
                    f"<div class='prompt-box'>✨ <b>Try prompting like this:</b><br>{c.get('better_prompt')}</div>",
                    unsafe_allow_html=True,
                )
        st.markdown(msg["content"])

# Quick conversation starters when chat is fresh
if not st.session_state.messages:
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚖️ What is DBMS Normalization?", use_container_width=True):
            st.session_state.starter_prompt = "Explain Normalization in DBMS with 1NF, 2NF, and 3NF examples."
    with col2:
        if st.button("⏰ What is the Late Penalty?", use_container_width=True):
            st.session_state.starter_prompt = "What is the course submission deadline and late penalty policy?"

# Input bar
user_input = st.chat_input("Ask a question, request an explanation, or test a concept...")

# Check if a starter button was clicked
if "starter_prompt" in st.session_state and st.session_state.starter_prompt:
    user_input = st.session_state.starter_prompt
    st.session_state.starter_prompt = None

# -----------------------------------------------------------------------------
# 5. AGENT EXECUTION
# -----------------------------------------------------------------------------
if user_input:
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Run agent prompt analysis in background
    with st.spinner("Analyzing and preparing answer..."):
        prompt_coach_data = evaluate_prompt(user_input)

    # 3. Build system instructions (combining document if present)
    system_prompt = STUDY_AGENT_INSTRUCTION
    if st.session_state.uploaded_text:
        system_prompt += f"\n\n[STUDENT UPLOADED NOTES: {st.session_state.uploaded_name}]\n{st.session_state.uploaded_text}\n[END NOTES]\nAnswer using these notes whenever applicable."

    # 4. Format conversation history for Gemini
    history_payload = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        history_payload.append({"role": role, "parts": [{"text": m["content"]}]})
    history_payload.append({"role": "user", "parts": [{"text": user_input}]})

    # 5. Stream the response
    with st.chat_message("assistant"):
        # Neat, non-intrusive collapsible drawer for coaching
        with st.expander(f"💡 Prompt Coach • Detected: **{prompt_coach_data.get('category')}**", expanded=False):
            st.write(f"**Tip:** {prompt_coach_data.get('tip')}")
            st.markdown(
                f"<div class='prompt-box'>✨ <b>Try prompting like this:</b><br>{prompt_coach_data.get('better_prompt')}</div>",
                unsafe_allow_html=True,
            )

        response_placeholder = st.empty()
        streamed_text = ""

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4,
            )

            stream = client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=history_payload,
                config=config,
            )

            for chunk in stream:
                if chunk.text:
                    streamed_text += chunk.text
                    response_placeholder.markdown(streamed_text + "▌")

            response_placeholder.markdown(streamed_text)

            # Persist to memory
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "coaching": prompt_coach_data,
            })
            st.session_state.messages.append({
                "role": "assistant",
                "content": streamed_text,
            })

        except Exception as e:
            response_placeholder.empty()
            st.error(f"Error: {e}")