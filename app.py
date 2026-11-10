
import os
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="BNS AI | Smart Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME = "gemini-3.1-flash-lite"

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080d19;
    color: #f1f5f9;
}

[data-testid="stSidebar"] {
    background: #101827;
    border-right: 1px solid #263449;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #d1d9e6;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 15px;
    margin-bottom: 30px;
}

.brand {
    font-size: 27px;
    font-weight: 800;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.feature-card {
    background: linear-gradient(145deg, #17243a, #101827);
    border: 1px solid #263b5c;
    padding: 20px;
    border-radius: 16px;
    min-height: 125px;
    margin-bottom: 12px;
}

.feature-card h4 {
    color: #93c5fd;
    margin-bottom: 8px;
}

.feature-card p {
    color: #aab8ca;
    font-size: 13px;
}

.welcome-box {
    background: linear-gradient(145deg, #14233c, #111827);
    border: 1px solid #304765;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
}

.welcome-box h2 {
    color: #e2e8f0;
}

.welcome-box p {
    color: #94a3b8;
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid #36547b;
    background: #172b49;
    color: white;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #24436e;
    border-color: #60a5fa;
    color: white;
}

[data-testid="stChatMessage"] {
    background: #111c2d;
    border: 1px solid #263b55;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 12px;
}

[data-testid="stChatInput"] {
    border-color: #36547b;
}

.status {
    color: #4ade80;
    font-size: 13px;
}

.footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 25px 0 10px 0;
}

hr {
    border-color: #263449;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# API CONFIGURATION
# =========================================================

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


API_KEY = get_api_key()

client = None

if API_KEY:
    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(timeout=60000)
        )
    except Exception as error:
        st.error(f"Could not initialize Gemini: {error}")


# =========================================================
# SESSION STATE
# =========================================================

if "chats" not in st.session_state:
    st.session_state.chats = {
        "chat_1": {
            "title": "New Conversation",
            "messages": [],
            "previous_interaction_id": None
        }
    }

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "chat_1"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_current_chat():
    return st.session_state.chats[st.session_state.active_chat]


def create_new_chat():
    st.session_state.chat_counter += 1
    chat_id = f"chat_{st.session_state.chat_counter}"

    st.session_state.chats[chat_id] = {
        "title": "New Conversation",
        "messages": [],
        "previous_interaction_id": None
    }

    st.session_state.active_chat = chat_id
    st.session_state.pending_prompt = None


def clear_current_chat():
    chat = get_current_chat()
    chat["messages"] = []
    chat["previous_interaction_id"] = None
    chat["title"] = "New Conversation"
    st.session_state.pending_prompt = None


def extract_response_text(response):
    """Extract text from a Gemini interaction response."""

    output_text = getattr(response, "output_text", None)

    if output_text:
        return output_text

    collected_text = []

    output = getattr(response, "output", None) or []

    for item in output:
        content_list = getattr(item, "content", None) or []

        for content in content_list:
            text_value = getattr(content, "text", None)

            if text_value:
                collected_text.append(text_value)

    if collected_text:
        return "\n".join(collected_text)

    return "I received a response, but could not read its text."


def ask_gemini(prompt, chat):
    """Send a message to Gemini and preserve conversation context."""

    if client is None:
        return "Gemini API is not configured. Please check your API key."

    try:
        request_args = {
            "model": MODEL_NAME,
            "input": prompt
        }

        previous_id = chat.get("previous_interaction_id")

        if previous_id:
            request_args["previous_interaction_id"] = previous_id

        response = client.interactions.create(**request_args)

        new_id = getattr(response, "id", None)

        if new_id:
            chat["previous_interaction_id"] = new_id

        return extract_response_text(response)

    except Exception as error:
        return (
            "Sorry, I couldn't generate a response.\n\n"
            f"**Error:** `{type(error).__name__}: {error}`\n\n"
            "Please check your internet connection and try again."
        )


def transcribe_audio(audio_file):
    """Transcribe recorded audio using Gemini."""

    if client is None:
        return "Gemini API is not configured."

    try:
        audio_bytes = audio_file.getvalue()
        mime_type = audio_file.type or "audio/wav"

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                "Transcribe the speech in this audio accurately. "
                "Return only the spoken words.",
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type
                )
            ]
        )

        return response.text or ""

    except Exception as error:
        return f"Audio transcription failed: {error}"


def process_message(prompt):
    """Display user message, request AI response and save both."""

    prompt = prompt.strip()

    if not prompt:
        return

    chat = get_current_chat()

    chat["messages"].append({
        "role": "user",
        "content": prompt
    })

    if chat["title"] == "New Conversation":
        chat["title"] = prompt[:35] + ("..." if len(prompt) > 35 else "")

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("BNS AI is thinking..."):
            answer = ask_gemini(prompt, chat)

        st.markdown(answer)

    chat["messages"].append({
        "role": "assistant",
        "content": answer
    })


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown('<div class="brand">🤖 BNS AI</div>', unsafe_allow_html=True)

    st.caption("Your intelligent AI companion")

    st.markdown("---")

    if st.button("＋  New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.markdown("### 💬 Chat History")

    for chat_id, chat_data in reversed(list(st.session_state.chats.items())):

        label = chat_data["title"]

        if len(label) > 25:
            label = label[:25] + "..."

        is_active = chat_id == st.session_state.active_chat

        if st.button(
            f"{'● ' if is_active else '○ '}{label}",
            key=f"history_{chat_id}",
            use_container_width=True
        ):
            st.session_state.active_chat = chat_id
            st.session_state.pending_prompt = None
            st.rerun()

    st.markdown("---")

    st.markdown("### ⚙️ Settings")

    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        clear_current_chat()
        st.rerun()

    st.markdown("### ✨ Features")

    st.markdown("""
    - 🤖 Gemini AI responses
    - 🧠 Conversation memory
    - 🎙️ Voice input
    - 🔊 Voice output
    - 💬 Multiple conversations
    - ⚡ Fast AI assistance
    """)

    st.markdown("---")

    if client:
        st.markdown(
            '<p class="status">● Gemini AI Connected</p>',
            unsafe_allow_html=True
        )
    else:
        st.error("Gemini API not connected")

    st.caption("BNS AI • Version 1.0")


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="main-title">BNS AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your personal intelligent AI assistant</div>',
    unsafe_allow_html=True
)

if not API_KEY:
    st.error(
        "Gemini API key not found. Add GEMINI_API_KEY "
        "to your .streamlit/secrets.toml file."
    )


# =========================================================
# WELCOME SCREEN
# =========================================================

chat = get_current_chat()

if not chat["messages"]:

    st.markdown("""
    <div class="welcome-box">
        <h2>👋 Welcome to BNS AI!</h2>
        <p>Your ideas, questions and creativity start here.</p>
        <p>Ask me anything. I'm ready to help you!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 What would you like to explore?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "💻 Learn Programming",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Teach me Python programming from beginner level "
                "with simple examples."
            )
            st.rerun()

        if st.button(
            "🎓 Study Assistant",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Help me prepare for my engineering examinations."
            )
            st.rerun()

    with col2:
        if st.button(
            "🧠 Explore Artificial Intelligence",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Explain artificial intelligence and its real-world "
                "applications in simple English."
            )
            st.rerun()

        if st.button(
            "💡 Generate Project Ideas",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Suggest innovative beginner-friendly AI and IoT "
                "project ideas."
            )
            st.rerun()

    st.markdown("### ⭐ Why use BNS AI?")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 Smart AI</h4>
            <p>Get intelligent answers to your questions.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-card">
            <h4>🎙️ Voice Support</h4>
            <p>Speak to your assistant and listen to responses.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-card">
            <h4>🧠 Memory</h4>
            <p>Continue conversations with contextual memory.</p>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# DISPLAY EXISTING CONVERSATION
# =========================================================

else:

    for message in chat["messages"]:

        avatar = "👤" if message["role"] == "user" else "🤖"

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


# =========================================================
# VOICE INPUT
# =========================================================

st.markdown("---")

with st.expander("🎙️ Talk to BNS AI"):

    st.write("Record your question using your microphone.")

    audio_file = st.audio_input("Record your voice")

    if audio_file is not None:

        if st.button("Transcribe Audio", use_container_width=True):

            with st.spinner("Converting speech to text..."):
                transcript = transcribe_audio(audio_file)

            if transcript and not transcript.startswith(
                "Audio transcription failed:"
            ):
                st.session_state.pending_prompt = transcript
                st.success("Speech converted successfully!")
                st.write("**Recognized text:**", transcript)
            else:
                st.error(transcript or "No speech was detected.")


# =========================================================
# CHAT INPUT
# =========================================================

user_prompt = st.chat_input("Message BNS AI...")

if user_prompt:
    process_message(user_prompt)
    st.rerun()

if st.session_state.pending_prompt:

    pending = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    process_message(pending)
    st.rerun()


# =========================================================
# VOICE OUTPUT
# =========================================================

if chat["messages"]:

    last_message = chat["messages"][-1]

    if last_message["role"] == "assistant":

        st.markdown("### 🔊 Listen to the latest response")

        voice_text = last_message["content"]

        escaped_text = (
            voice_text
            .replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("$", "\\$")
        )

        components.html(
            f"""
            <div style="
                background:#14233c;
                padding:15px;
                border-radius:12px;
                color:white;
                font-family:Arial;
            ">
                <button onclick="speakText()"
                    style="
                        background:#2563eb;
                        color:white;
                        border:none;
                        padding:10px 18px;
                        border-radius:8px;
                        cursor:pointer;
                        margin-right:8px;
                    ">
                    ▶ Play
                </button>

                <button onclick="stopText()"
                    style="
                        background:#334155;
                        color:white;
                        border:none;
                        padding:10px 18px;
                        border-radius:8px;
                        cursor:pointer;
                    ">
                    ■ Stop
                </button>

                <script>
                    const textToSpeak = `{escaped_text}`;

                    function speakText() {{
                        window.speechSynthesis.cancel();

                        const speech = new SpeechSynthesisUtterance(
                            textToSpeak
                        );

                        speech.lang = "en-IN";
                        speech.rate = 1;
                        speech.pitch = 1;

                        window.speechSynthesis.speak(speech);
                    }}

                    function stopText() {{
                        window.speechSynthesis.cancel();
                    }}
                </script>
            </div>
            """,
            height=85
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    Built with ❤️ using Python, Streamlit and Google Gemini
    <br>
    © 2026 BNS AI. All rights reserved.
</div>
""", unsafe_allow_html=True)
