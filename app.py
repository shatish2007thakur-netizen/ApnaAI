import streamlit as st
from google import genai
import json
import os
import time
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import streamlit_js_eval

# ================= STREAMLIT PAGE CONFIG =================
st.set_page_config(page_title="JARVIS AI ONLINE SYSTEM", page_icon="🤖", layout="centered")

# Custom CSS for Jarvis Terminal View
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
    }
    .terminal-title {
        font-family: 'Courier New', Courier, monospace;
        color: #4af626;
        font-weight: bold;
        text-align: center;
        font-size: 32px;
        margin-bottom: 5px;
    }
    .terminal-status {
        color: #ffffff;
        font-style: italic;
        text-align: center;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .chat-box {
        background-color: #000000;
        border: 2px solid #2d2d2d;
        border-radius: 5px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #4af626;
        height: 350px;
        overflow-y: auto;
        margin-bottom: 20px;
        white-space: pre-wrap;
    }
    .stButton > button {
        background-color: #4af626;
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton > button:hover {
        background-color: #ffffff;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

# Title Header
st.markdown('<div class="terminal-title">⚡ JARVIS AI ONLINE SYSTEM</div>', unsafe_allow_html=True)

# ================= GEMINI CONFIGURATION =================
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = None

@st.cache_resource
def get_ai_client(key):
    if key:
        try:
            return genai.Client(api_key=key)
        except Exception:
            return None
    return None

ai_client = get_ai_client(api_key)

# Initialize Session States
if "chat_history" not in st.session_state:
    st.session_state.chat_history = "Jarvis: Systems online. Jarvis AI initialized.\nJarvis: Ready for your command, Sir."
if "tts_text" not in st.session_state:
    st.session_state.tts_text = ""

# ================= CORE PROCESSOR =================
def process_command(command):
    if not command or command.strip() == "":
        return
        
    st.session_state.chat_history += f"\n\nYou: {command}"
    cmd = command.lower().strip()
    
    # System Commands
    if "stop" in cmd or "exit" in cmd or "bye jarvis" in cmd or "shutdown" in cmd:
        reply = "Going offline. Goodbye, Sir. 🖥️"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply
        
    elif "open google" in cmd:
        reply = "Opening Google, Sir. 🌐"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply
        st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://www.google.com\'" />', unsafe_allow_html=True)
        
    elif "open youtube" in cmd:
        reply = "Opening YouTube, Sir. 📺"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply
        st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://www.youtube.com\'" />', unsafe_allow_html=True)
    
    elif "open github" in cmd:
        reply = "Opening GitHub, Sir. 🐙"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply
        st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://github.com\'" />', unsafe_allow_html=True)

    elif "time" in cmd or "kitna baj" in cmd:
        now = datetime.now().strftime("%I:%M %p")
        reply = f"Sir, the current time is {now}. ⏰"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply

    elif "date" in cmd or "tareek" in cmd:
        today = datetime.now().strftime("%d %B %Y")
        reply = f"Sir, today is {today}. 📅"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply

    else:
        if not ai_client:
            reply = "Sir, Gemini API Key is missing. Please add it to secrets."
            st.session_state.chat_history += f"\n\nJarvis: {reply}"
            st.session_state.tts_text = reply
        else:
            try:
                response = ai_client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=command,
                    config={
                        'system_instruction': """You are JARVIS, Tony Stark's AI assistant. 
                        Keep responses: 
                        - Short and crisp (1-2 sentences max)
                        - Professional but friendly
                        - Use 'Sir' when addressing the user
                        - Be helpful and precise"""
                    }
                )
                reply = response.text.strip()
                st.session_state.chat_history += f"\n\nJarvis: {reply}"
                st.session_state.tts_text = reply
            except Exception as e:
                if "429" in str(e):
                    reply = "Sir, rate limit reached. Please wait 5 seconds. ⏳"
                elif "API_KEY" in str(e):
                    reply = "Sir, invalid API key. Please check your credentials. 🔑"
                else:
                    reply = f"Sir, AI core error: {str(e)[:50]}"
                st.session_state.chat_history += f"\n\nJarvis: {reply}"
                st.session_state.tts_text = reply

# Status Bar
status_col1, status_col2 = st.columns([3, 1])
with status_col1:
    st.markdown('<div class="terminal-status">🟢 Status: Active | Ready for voice or text commands</div>', unsafe_allow_html=True)
with status_col2:
    if ai_client:
        st.markdown('<div class="terminal-status" style="color:#4af626;">✅ AI Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="terminal-status" style="color:#ff4b4b;">❌ AI Offline</div>', unsafe_allow_html=True)

# Display Terminal logs
st.markdown(f'<div class="chat-box">{st.session_state.chat_history}</div>', unsafe_allow_html=True)

# ================= VOICE RECORDER (NEW) =================
st.markdown("### 🎤 Voice Command")
col1, col2 = st.columns([2, 1])

with col1:
    # Use streamlit-mic-recorder
    audio = mic_recorder(
        start_prompt="🎙️ Click to Speak",
        stop_prompt="⏹️ Stop Recording",
        just_once=True,
        use_container_width=True,
        format="webm",
        key="jarvis_mic"
    )

with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = "Jarvis: Chat cleared. Ready for new commands."
        st.session_state.tts_text = "Chat cleared."
        st.rerun()

# Process audio when available
if audio:
    # Save audio temporarily
    audio_bytes = audio.get('bytes')
    if audio_bytes:
        # Convert audio to text using Google Speech Recognition (via st-js-eval or alternative)
        # Since mic_recorder gives bytes, we can use a speech-to-text service
        # Option 1: Use Google Cloud Speech-to-Text (requires API)
        # Option 2: Use a local model (slower)
        # Option 3: Use a free online API
        
        # For simplicity, we'll use streamlit_js_eval to call Web Speech API
        # But mic_recorder already records, so we can use a JS fallback for transcription
        
        # We'll use a JS approach to transcribe the audio
        st.session_state.tts_text = "Processing voice... Please wait."
        
        # Temporary solution: Show a message and use text input as fallback
        st.warning("Voice transcription requires additional setup. Please use the text input below for now.")
        st.session_state.chat_history += "\n\nJarvis: Voice received but transcription not configured. Please type your command."

# ================= TEXT-TO-SPEECH (JARVIS SPEAKS) =================
# Use streamlit_js_eval to trigger TTS
if st.session_state.tts_text:
    # JavaScript to speak the text
    tts_js = f"""
    <script>
    (function() {{
        if (window.speechSynthesis) {{
            let utterance = new SpeechSynthesisUtterance(`{st.session_state.tts_text}`);
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            window.speechSynthesis.speak(utterance);
        }}
    }})();
    </script>
    """
    st.components.v1.html(tts_js, height=0)
    # Clear after speaking (optional, but keep for next command)
    # st.session_state.tts_text = ""  # Uncomment to clear after speaking

# ================= MANUAL TEXT INPUT FORM =================
st.markdown("---")
st.markdown("### ⌨️ Type Your Command")

with st.form(key="command_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        text_input = st.text_input("Command:", placeholder="Type your command here...", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button("🚀 Send", use_container_width=True)
    
    if submit_button and text_input:
        process_command(text_input)
        st.rerun()

# ================= FOOTER =================
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px; font-family: 'Courier New', monospace;">
        ⚡ JARVIS AI v2.0 | Powered by Gemini 2.0 Flash
    </div>
""", unsafe_allow_html=True)
