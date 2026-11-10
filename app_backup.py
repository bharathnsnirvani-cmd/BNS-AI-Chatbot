
import streamlit as st
import json
from google import genai
from google.genai import types

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="BNS AI Voice Assistant",
    page_icon="🤖",
    layout="centered"
)

# ==========================================
# 2. GEMINI CONNECTION
# ==========================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# ==========================================
# 3. CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #101827;
    color: white;
}

h1 {
    color: #38bdf8;
    text-align: center;
}

.stCaption {
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

st.title("🤖 BNS AI")
st.caption("Your Personal AI Voice Assistant")

st.divider()

# ==========================================
# 4. INITIALIZE SESSION MEMORY
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "previous_interaction_id" not in st.session_state:
    st.session_state.previous_interaction_id = None

# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("⚙️ Settings")

    st.write("BNS AI Assistant")

    if st.button("🗑️ New Chat", use_container_width=True):

        st.session_state.messages = []
        st.session_state.previous_interaction_id = None

        st.rerun()

    st.divider()

    st.write("🚀 Powered by Gemini AI")
    st.write("🎤 Voice Input Enabled")
    st.write("🔊 Voice Output Enabled")

# ==========================================
# 6. VOICE OUTPUT FUNCTION
# ==========================================

def voice_player(text):

    safe_text = json.dumps(text)

    html_code = """
    <div style="
        background:#1e293b;
        padding:15px;
        border-radius:12px;
        color:white;
        font-family:Arial;
    ">

        <h4>🔊 BNS AI Voice Player</h4>

        <label>Choose Voice:</label>

        <select id="voice" style="padding:8px;width:100%;">
        </select>

        <br><br>

        <button onclick="speak()">▶ Play</button>
        <button onclick="pauseSpeech()">⏸ Pause</button>
        <button onclick="resumeSpeech()">▶ Resume</button>
        <button onclick="stopSpeech()">⏹ Stop</button>

    </div>

    <script>

        const speechText = __TEXT__;

        const synth = window.speechSynthesis;

        const voiceSelect = document.getElementById("voice");

        function loadVoices() {

            const voices = synth.getVoices();

            voiceSelect.innerHTML = "";

            voices.forEach((voice, index) => {

                const option = document.createElement("option");

                option.value = index;

                option.textContent =
                    voice.name + " (" + voice.lang + ")";

                voiceSelect.appendChild(option);

            });
        }

        loadVoices();

        synth.onvoiceschanged = loadVoices;

        function speak() {

            synth.cancel();

            const utterance =
                new SpeechSynthesisUtterance(speechText);

            const voices = synth.getVoices();

            const selectedVoice =
                voices[voiceSelect.value];

            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }

            utterance.rate = 1;
            utterance.pitch = 1;

            synth.speak(utterance);
        }

        function pauseSpeech() {

            if (synth.speaking) {
                synth.pause();
            }
        }

        function resumeSpeech() {

            synth.resume();
        }

        function stopSpeech() {

            synth.cancel();
        }

    </script>
    """

    html_code = html_code.replace(
        "__TEXT__", safe_text
    )

    st.components.v1.html(
        html_code,
        height=190
    )

# ==========================================
# 7. DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":
            voice_player(message["content"])

# ==========================================
# 8. GEMINI AI FUNCTION
# ==========================================

def ask_bns_ai(question):

    request_args = {
        "model": "gemini-3.1-flash-lite",
        "input": question,
        "timeout": 60000,
        "system_instruction": (
            "You are BNS AI, a friendly and intelligent "
            "personal AI assistant. "
            "Give clear, simple and helpful answers."
        )
    }

    if st.session_state.previous_interaction_id:

        request_args["previous_interaction_id"] = (
            st.session_state.previous_interaction_id
        )

    response = client.interactions.create(
        **request_args
    )

    st.session_state.previous_interaction_id = response.id

    return response.output_text or (
        "Sorry, I couldn't generate an answer."
    )

# ==========================================
# 9. VOICE INPUT FUNCTION
# ==========================================

def transcribe_audio(audio_file):

    audio_bytes = audio_file.getvalue()

    response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=[

            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav"
            ),

            "Transcribe the spoken words exactly. "
            "Return only the transcription."
        ]
    )

    return response.text.strip()

# ==========================================
# 10. TEXT INPUT
# ==========================================

user_input = st.chat_input(
    "💬 Ask BNS AI anything..."
)

# ==========================================
# 11. VOICE INPUT
# ==========================================

st.subheader("🎤 Talk to BNS AI")

audio_value = st.audio_input(
    "Record your question"
)

voice_question = None

if audio_value:

    if st.button("📤 Send Voice Message"):

        with st.spinner("Listening to your voice..."):

            try:

                voice_question = transcribe_audio(
                    audio_value
                )

                if not voice_question:
                    st.warning("No speech detected.")
                    voice_question = None

            except Exception as e:

                st.error(f"Voice input error: {e}")

# ==========================================
# 12. PROCESS USER QUESTION
# ==========================================

question = user_input or voice_question

if question:

    # Save user question

    st.session_state.messages.append({

        "role": "user",
        "content": question

    })

    with st.chat_message("user"):

        st.markdown(question)

    # Generate AI answer

    with st.chat_message("assistant"):

        with st.spinner("🤖 BNS AI is thinking..."):

            try:

                answer = ask_bns_ai(question)

                st.markdown(answer)

                # Voice output

                voice_player(answer)

                # Save AI answer

                st.session_state.messages.append({

                    "role": "assistant",
                    "content": answer

                })

            except Exception as e:

                st.error(f"Something went wrong: {e}")

# ==========================================
# 13. FOOTER
# ==========================================

st.divider()

st.markdown(
    "<center>Built with ❤️ | BNS AI Assistant</center>",
    unsafe_allow_html=True
)
