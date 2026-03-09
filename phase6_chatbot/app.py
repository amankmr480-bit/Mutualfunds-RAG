"""
Phase 6: Streamlit chat UI for ICICI Prudential Mutual Fund RAG.
No personal data stored; personal questions are refused.
Layout: Header (red) | Chat history (left) | Main chat (center) | Suggested questions (right)
"""
import sys
from pathlib import Path

# Ensure project root is on path when running from phase6_chatbot dir
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Load .env so GROQ_API_KEY is available (paste key in .env file)
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env", override=True)
except ImportError:
    pass

import streamlit as st

from phase6_chatbot.orchestrator import chat_turn

# Page config - wide layout for 3-column design
st.set_page_config(
    page_title="ICICI Prudential MF Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS: header (red), main area (blue/purple), layout
st.markdown("""
<style>
    /* Red header with diagonal pattern */
    .icici-header {
        background: linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
        background-image: 
            linear-gradient(135deg, transparent 25%, rgba(0,0,0,0.03) 25%),
            linear-gradient(225deg, transparent 25%, rgba(0,0,0,0.03) 25%),
            linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
        background-size: 20px 20px, 20px 20px, 100% 100%;
        padding: 1rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        border-radius: 0 0 8px 8px;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .icici-logo-box {
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .icici-title {
        color: black;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
    }
    /* Blue/purple main content area */
    .main-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 50%, #2c3e50 100%);
        padding: 1.5rem;
        border-radius: 8px;
        min-height: 60vh;
    }
    /* Chat history panel (left) */
    .chat-history-panel {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 1rem;
        max-height: 50vh;
        overflow-y: auto;
    }
    /* Suggested questions panel (right) */
    .suggested-panel {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 1rem;
    }
    .suggested-btn {
        width: 100%;
        text-align: left;
        margin-bottom: 0.5rem;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        font-size: 0.9rem;
        cursor: pointer;
    }
    .suggested-btn:hover {
        background: rgba(255,255,255,0.2);
    }
    /* Override Streamlit default background */
    .stApp {
        background: linear-gradient(180deg, #1a252f 0%, #2c3e50 100%);
    }
    /* White text for intro, disclaimer, and center column content */
    .white-text, .white-text p, .white-text strong, .white-text em {
        color: white !important;
    }
    /* Center column (2nd of 3 in horizontal block) - all text white including output */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) p,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) span,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) label,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) a,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stChatMessage"] p,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stChatMessage"] span,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stChatMessage"] div,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stMarkdown,
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stMarkdown * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Header (as in image)
_assets_dir = _root / "assets"
_logo_path = _assets_dir / "icici_prudential_logo.png"
if not _logo_path.exists():
    _logo_path = _assets_dir / "icici.jpg"
if not _logo_path.exists() and _assets_dir.exists():
    _logos = list(_assets_dir.glob("*icici*")) or list(_assets_dir.glob("*.png")) or list(_assets_dir.glob("*.jpg"))
    if _logos:
        _logo_path = _logos[0]

header_html = """
<div class="icici-header">
    <div class="icici-logo-box">
"""
if _logo_path.exists():
    import base64
    ext = _logo_path.suffix.lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    with open(_logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    header_html += f'<img src="data:{mime};base64,{logo_b64}" style="height:50px; max-width:180px; object-fit:contain;" />'
else:
    header_html += '<span style="color:#c41e3a; font-weight:700;">ICICI</span><br/><span style="color:#c41e3a; font-size:1.1rem;">PRUDENTIAL</span><br/><span style="color:#333; font-size:0.75rem;">ASSET MANAGEMENT</span>'

header_html += """
    </div>
    <h1 class="icici-title">ICICI Prudential Mutual Fund Assistant</h1>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Intro text, privacy, and source URL (below header) - white text
SOURCE_URL = "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds"
st.markdown(f"""
<div class="white-text">
<strong>Ask questions about ICICI Prudential mutual fund schemes.</strong><br/>
<em>Privacy: We do not answer personal questions or store any personal data. Only your question and our answer are shown in this chat.</em><br/>
<strong>Source:</strong> <a href="{SOURCE_URL}" target="_blank" rel="noopener" style="color: white; text-decoration: underline;">Groww - ICICI Prudential Mutual Fund</a>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Suggested questions (fund-related)
SUGGESTED_QUESTIONS = [
    "What are the top performing ICICI Prudential equity funds?",
    "What is the NAV of ICICI Prudential Bluechip Fund?",
    "Compare expense ratios of ICICI Prudential debt funds",
    "What is the minimum investment for ICICI Prudential funds?",
    "Which ICICI Prudential funds have the best 5-year returns?",
    "What is the AUM of ICICI Prudential Mutual Fund schemes?",
]

# Three-column layout: Chat history (left) | Main chat (center) | Suggested (right)
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_left:
    st.markdown("#### Chat History")
    if st.session_state.messages:
        with st.container():
            for i, msg in enumerate(st.session_state.messages):
                role = msg["role"]
                short = (msg["content"][:60] + "…") if len(msg["content"]) > 60 else msg["content"]
                st.caption(f"**{role.title()}:** {short}")
    else:
        st.caption("No messages yet. Ask a question below.")

with col_right:
    st.markdown("#### Suggested Questions")
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        if st.button(q, key=f"suggest_{i}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

# Main chat area (center)
with col_center:
    st.markdown("---")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("refused_personal"):
                st.caption("Personal questions are not answered.")
            # no_data_found: answer content already includes the fallback link

# Get prompt: from suggested question click or from chat input
prompt = st.session_state.pop("pending_question", None)
if prompt is None:
    with col_center:
        prompt = st.chat_input("Ask about ICICI Prudential funds (e.g. NAV, returns, expense ratio)...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col_center:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = chat_turn(prompt)
            answer = result.get("answer", "Sorry, I couldn't generate an answer.")
            st.markdown(answer)
            if result.get("refused_personal"):
                st.caption("We don't handle personal questions or store personal data.")
            if result.get("sources"):
                source_url = None
                for s in result["sources"]:
                    if s and s.get("source_url"):
                        source_url = s.get("source_url")
                        break
                if not source_url:
                    source_url = SOURCE_URL
                st.markdown(f"[Source: Groww ICICI Prudential MF]({source_url})")
            # no_data_found: answer already includes "For more funds detail visit https://www.icicipruamc.com/home"
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "refused_personal": result.get("refused_personal", False),
        "no_data_found": result.get("no_data_found", False),
    })
    st.rerun()

# Sidebar: clear chat
with st.sidebar:
    st.header("Options")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.markdown("**About**")
    st.markdown("Answers are based on ICICI Prudential fund data. We do not store personal data or answer personal questions.")
