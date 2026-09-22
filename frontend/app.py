"""
Wikipedia RAG — Streamlit Frontend
A premium chat interface for the Wikipedia RAG API.
"""

import time
import requests
import streamlit as st

# ── Configuration ────────────────────────────────────────────────────────────
API_BASE_URL = "http://localhost:8000/api/v1"
QUERY_ENDPOINT = f"{API_BASE_URL}/query"
STATUS_ENDPOINT = f"{API_BASE_URL}/wikipedia/status"

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wikipedia RAG Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Import Google Font ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root Variables ─────────────────────────────────────────────────────── */
:root {
    --bg-primary: #0f0f1a;
    --bg-secondary: #1a1a2e;
    --bg-card: #16213e;
    --accent-1: #7c3aed;
    --accent-2: #a855f7;
    --accent-3: #6366f1;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border-color: rgba(124, 58, 237, 0.2);
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --glow-purple: rgba(124, 58, 237, 0.15);
}

/* ── Global ─────────────────────────────────────────────────────────────── */
.stApp {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hero Header ────────────────────────────────────────────────────────── */
.hero-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    margin-bottom: 1rem;
}

.hero-header h1 {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a855f7, #6366f1, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    letter-spacing: -0.02em;
}

.hero-header p {
    color: var(--text-secondary);
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* ── Chat Messages ──────────────────────────────────────────────────────── */
.user-message {
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    color: #ffffff;
    padding: 1rem 1.25rem;
    border-radius: 1.25rem 1.25rem 0.3rem 1.25rem;
    margin: 0.6rem 0;
    max-width: 85%;
    margin-left: auto;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
    animation: slideInRight 0.3s ease-out;
}

.assistant-message {
    background: rgba(30, 30, 60, 0.6);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 1rem 1.25rem;
    border-radius: 1.25rem 1.25rem 1.25rem 0.3rem;
    margin: 0.6rem 0;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.7;
    backdrop-filter: blur(10px);
    animation: slideInLeft 0.3s ease-out;
}

.blocked-message {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
    padding: 1rem 1.25rem;
    border-radius: 1.25rem 1.25rem 1.25rem 0.3rem;
    margin: 0.6rem 0;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.6;
    animation: slideInLeft 0.3s ease-out;
}

/* ── Source Card ─────────────────────────────────────────────────────────── */
.source-card {
    background: rgba(22, 33, 62, 0.5);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 0.75rem;
    padding: 0.85rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.55;
    transition: border-color 0.2s ease, background 0.2s ease;
}

.source-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(22, 33, 62, 0.8);
}

.source-label {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed, #6366f1);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 0.4rem;
    margin-bottom: 0.4rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Status Badge ───────────────────────────────────────────────────────── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.75rem;
    border-radius: 2rem;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.02em;
}

.status-online {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.25);
}

.status-offline {
    background: rgba(239, 68, 68, 0.12);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

/* ── Sidebar Styling ────────────────────────────────────────────────────── */
.sidebar-section {
    background: rgba(22, 33, 62, 0.4);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    padding: 1rem;
    margin-bottom: 0.75rem;
}

.sidebar-section h4 {
    color: var(--text-primary);
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.sidebar-section p {
    color: var(--text-secondary);
    font-size: 0.82rem;
    line-height: 1.5;
    margin: 0;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.35rem 0;
    color: var(--text-secondary);
    font-size: 0.82rem;
}

.stat-value {
    color: var(--accent-2);
    font-weight: 600;
}

/* ── Animations ─────────────────────────────────────────────────────────── */
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.5; }
}

.typing-indicator {
    display: inline-flex;
    gap: 4px;
    padding: 0.6rem 1rem;
}
.typing-indicator span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent-2);
    animation: pulse 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

/* ── Misc ───────────────────────────────────────────────────────────────── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    margin: 1rem 0;
}

/* Make the chat input prettier */
.stChatInput > div {
    border-color: var(--border-color) !important;
}
.stChatInput textarea {
    font-family: 'Inter', sans-serif !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── Helper Functions ─────────────────────────────────────────────────────────
def check_backend_status() -> dict:
    """Ping the backend health endpoint."""
    try:
        resp = requests.get(STATUS_ENDPOINT, timeout=5)
        resp.raise_for_status()
        return {"online": True, **resp.json()}
    except Exception:
        return {"online": False}


def query_rag(question: str) -> dict:
    """Send a question to the RAG pipeline."""
    try:
        resp = requests.post(
            QUERY_ENDPOINT,
            json={"question": question},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "answer": "⚠️ Cannot connect to the backend. Please make sure the FastAPI server is running on `localhost:8000`.",
            "sources": [],
            "blocked": False,
            "error": True,
        }
    except requests.exceptions.HTTPError as exc:
        detail = ""
        try:
            detail = exc.response.json().get("detail", str(exc))
        except Exception:
            detail = str(exc)
        return {
            "answer": f"⚠️ Backend error: {detail}",
            "sources": [],
            "blocked": False,
            "error": True,
        }
    except Exception as exc:
        return {
            "answer": f"⚠️ Unexpected error: {exc}",
            "sources": [],
            "blocked": False,
            "error": True,
        }


# ── Session State Initialization ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "blocked_count" not in st.session_state:
    st.session_state.blocked_count = 0


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
    <div style="text-align: center; padding: 1rem 0 0.5rem;">
        <span style="font-size: 2.5rem;">📚</span>
        <h2 style="
            font-size: 1.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a855f7, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.3rem 0 0;
        ">Wikipedia RAG</h2>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">Intelligent Q&A System</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Backend Status
    status = check_backend_status()
    if status["online"]:
        st.markdown(
            """
        <div class="sidebar-section">
            <h4>⚡ Backend Status</h4>
            <div class="status-badge status-online">
                <span>●</span> Online & Ready
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
        <div class="sidebar-section">
            <h4>⚡ Backend Status</h4>
            <div class="status-badge status-offline">
                <span>●</span> Offline
            </div>
            <p style="margin-top: 0.5rem; font-size: 0.78rem;">
                Start the backend with:<br>
                <code>uvicorn app.main:app --reload</code>
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Session Stats
    st.markdown(
        f"""
    <div class="sidebar-section">
        <h4>📊 Session Stats</h4>
        <div class="stat-row">
            <span>Questions Asked</span>
            <span class="stat-value">{st.session_state.query_count}</span>
        </div>
        <div class="stat-row">
            <span>Blocked Queries</span>
            <span class="stat-value">{st.session_state.blocked_count}</span>
        </div>
        <div class="stat-row">
            <span>Messages</span>
            <span class="stat-value">{len(st.session_state.messages)}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # About
    st.markdown(
        """
    <div class="sidebar-section">
        <h4>ℹ️ About</h4>
        <p>
            This assistant uses <strong>Retrieval-Augmented Generation</strong>
            to answer questions grounded in Wikipedia content.
            It features built-in safety guardrails to block unsafe
            and prompt-injection queries.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Tech Stack
    st.markdown(
        """
    <div class="sidebar-section">
        <h4>🛠️ Tech Stack</h4>
        <div class="stat-row"><span>LLM</span><span class="stat-value">Groq</span></div>
        <div class="stat-row"><span>Embeddings</span><span class="stat-value">MiniLM-L6</span></div>
        <div class="stat-row"><span>Vector DB</span><span class="stat-value">ChromaDB</span></div>
        <div class="stat-row"><span>Backend</span><span class="stat-value">FastAPI</span></div>
        <div class="stat-row"><span>Frontend</span><span class="stat-value">Streamlit</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Clear Chat Button
    if st.button("🗑️  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.session_state.blocked_count = 0
        st.rerun()


# ── Main Content ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-header">
    <h1>📚 Wikipedia RAG Assistant</h1>
    <p>Ask any question — powered by retrieval-augmented generation with safety guardrails</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Chat History ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(
                f'<div class="user-message">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
    else:
        avatar = "🚫" if msg.get("blocked") else "🤖"
        with st.chat_message("assistant", avatar=avatar):
            css_class = "blocked-message" if msg.get("blocked") else "assistant-message"
            st.markdown(
                f'<div class="{css_class}">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

            # Show sources if available
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📄 View {len(sources)} source(s)", expanded=False):
                    for idx, source in enumerate(sources, 1):
                        st.markdown(
                            f"""
                        <div class="source-card">
                            <div class="source-label">Source {idx}</div>
                            <div>{source}</div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )


# ── Chat Input ───────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a Wikipedia question…", key="chat_input"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(
            f'<div class="user-message">{prompt}</div>',
            unsafe_allow_html=True,
        )

    # Show typing indicator and get response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(""):
            # Show a subtle typing indicator
            typing_placeholder = st.empty()
            typing_placeholder.markdown(
                """
            <div class="assistant-message">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Call the backend
            result = query_rag(prompt)
            st.session_state.query_count += 1

            # Clear typing indicator
            typing_placeholder.empty()

            answer = result.get("answer", "No response received.")
            sources = result.get("sources", [])
            blocked = result.get("blocked", False)
            is_error = result.get("error", False)

            if blocked:
                st.session_state.blocked_count += 1

            # Determine styling
            if blocked:
                css_class = "blocked-message"
                avatar_icon = "🚫"
            elif is_error:
                css_class = "blocked-message"
                avatar_icon = "⚠️"
            else:
                css_class = "assistant-message"
                avatar_icon = "🤖"

            # Display answer with streaming effect
            answer_placeholder = st.empty()
            displayed_text = ""
            for char in answer:
                displayed_text += char
                answer_placeholder.markdown(
                    f'<div class="{css_class}">{displayed_text}</div>',
                    unsafe_allow_html=True,
                )
                time.sleep(0.008)

            # Show sources
            if sources:
                with st.expander(
                    f"📄 View {len(sources)} source(s)", expanded=False
                ):
                    for idx, source in enumerate(sources, 1):
                        st.markdown(
                            f"""
                        <div class="source-card">
                            <div class="source-label">Source {idx}</div>
                            <div>{source}</div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

    # Save to session
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "blocked": blocked,
        }
    )


# ── Welcome message when no conversation yet ─────────────────────────────────
if not st.session_state.messages:
    st.markdown(
        """
    <div style="
        text-align: center;
        padding: 3rem 2rem;
        color: #94a3b8;
    ">
        <div style="font-size: 3.5rem; margin-bottom: 1rem;">💬</div>
        <h3 style="
            color: #e2e8f0;
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        ">Start a Conversation</h3>
        <p style="font-size: 0.9rem; max-width: 400px; margin: 0 auto; line-height: 1.6;">
            Type your question below to query the Wikipedia knowledge base.
            The AI will retrieve relevant passages and generate a grounded answer.
        </p>

        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            margin-top: 1.5rem;
        ">
            <div style="
                background: rgba(124, 58, 237, 0.1);
                border: 1px solid rgba(124, 58, 237, 0.2);
                border-radius: 2rem;
                padding: 0.4rem 0.9rem;
                font-size: 0.8rem;
                color: #a78bfa;
            ">🌍 Geography</div>
            <div style="
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: 2rem;
                padding: 0.4rem 0.9rem;
                font-size: 0.8rem;
                color: #818cf8;
            ">📜 History</div>
            <div style="
                background: rgba(168, 85, 247, 0.1);
                border: 1px solid rgba(168, 85, 247, 0.2);
                border-radius: 2rem;
                padding: 0.4rem 0.9rem;
                font-size: 0.8rem;
                color: #c084fc;
            ">🔬 Science</div>
            <div style="
                background: rgba(129, 140, 248, 0.1);
                border: 1px solid rgba(129, 140, 248, 0.2);
                border-radius: 2rem;
                padding: 0.4rem 0.9rem;
                font-size: 0.8rem;
                color: #a5b4fc;
            ">🎭 Culture</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="
    text-align: center;
    padding: 2rem 1rem 1rem;
    color: #475569;
    font-size: 0.75rem;
    letter-spacing: 0.03em;
">
    <div class="divider"></div>
    Built with ❤️ using <strong>Streamlit</strong> • <strong>FastAPI</strong> • <strong>LangChain</strong> • <strong>ChromaDB</strong> • <strong>Groq</strong>
</div>
""",
    unsafe_allow_html=True,
)
