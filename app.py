import streamlit as st
from google import genai
import json
import os
import time

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
    .mic-button {
        width: 100%;
        padding: 14px;
        border-radius: 8px;
        border: 2px solid #4af626;
        background-color: #000000;
        color: #4af626;
        font-weight: bold;
        cursor: pointer;
        font-size: 18px;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        transition: 0.3s;
        margin-bottom: 10px;
    }
    .mic-button:hover {
        background-color: #4af626;
        color: #000000;
    }
    .mic-button.listening {
        background-color: #4af626;
        color: #000000;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
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
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""
if "process_voice" not in st.session_state:
    st.session_state.process_voice = False

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
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        reply = f"Sir, the current time is {now}. ⏰"
        st.session_state.chat_history += f"\n\nJarvis: {reply}"
        st.session_state.tts_text = reply

    elif "date" in cmd or "tareek" in cmd:
        from datetime import datetime
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

# ================= VOICE INPUT HANDLER =================
# Hidden input to receive voice from JavaScript
voice_text = st.text_input("🎤 Voice Input", key="voice_input_field", label_visibility="collapsed", 
                           placeholder="Voice input will appear here...")

if voice_text and voice_text != "":
    process_command(voice_text)
    # Clear the input after processing
    st.session_state.voice_input_field = ""
    st.rerun()

# ================= JAVASCRIPT VOICE RECOGNITION =================
# Voice TTS and Recognition JavaScript
tts_text = st.session_state.tts_text

js_code = f"""
<script>
// ================= TEXT TO SPEECH =================
function speakJarvis(text) {{
    if ('speechSynthesis' in window && text && text !== "") {{
        window.speechSynthesis.cancel();
        let utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Try to get a male voice for Jarvis
        let voices = window.speechSynthesis.getVoices();
        let jarvisVoice = voices.find(voice => voice.name.includes('Male') || voice.name.includes('David'));
        if (jarvisVoice) {{
            utterance.voice = jarvisVoice;
        }}
        
        window.speechSynthesis.speak(utterance);
    }}
}}

// Speak if there's text
var ttsText = `{tts_text}`;
if (ttsText && ttsText !== "") {{
    setTimeout(() => {{
        speakJarvis(ttsText);
    }}, 500);
}}

// ================= SPEECH RECOGNITION =================
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {{
    document.getElementById('mic-btn').innerHTML = '❌ Browser Not Supported';
    document.getElementById('mic-btn').disabled = true;
}} else {{
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const micBtn = document.getElementById('mic-btn');
    
    micBtn.addEventListener('click', function() {{
        try {{
            recognition.start();
            this.innerHTML = '⏳ Listening... Speak Now 🎤';
            this.classList.add('listening');
        }} catch (e) {{
            console.log('Error starting recognition:', e);
        }}
    }});

    recognition.onresult = function(event) {{
        const transcript = event.results[0][0].transcript;
        console.log('Recognized:', transcript);
        
        // Send to Streamlit via hidden input
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        let targetInput = null;
        
        // Find our voice input field
        for (let input of inputs) {{
            if (input.id && input.id.includes('voice_input_field')) {{
                targetInput = input;
                break;
            }}
        }}
        
        if (targetInput) {{
            // Set value and trigger events
            targetInput.value = transcript;
            targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            
            // Trigger Enter key to submit
            const enterEvent = new KeyboardEvent('keydown', {{
                bubbles: true,
                cancelable: true,
                key: 'Enter',
                keyCode: 13
            }});
            targetInput.dispatchEvent(enterEvent);
        }}
        
        // Reset button
        micBtn.innerHTML = '🎙️ Click to Speak';
        micBtn.classList.remove('listening');
    }};

    recognition.onerror = function(event) {{
        console.error('Recognition error:', event.error);
        micBtn.innerHTML = '❌ Error: ' + event.error;
        micBtn.classList.remove('listening');
        setTimeout(() => {{
            micBtn.innerHTML = '🎙️ Click to Speak';
        }}, 2000);
    }};

    recognition.onend = function() {{
        micBtn.innerHTML = '🎙️ Click to Speak';
        micBtn.classList.remove('listening');
    }};
}}
</script>
"""

# ================= MIC BUTTON =================
st.markdown("""
    <button id="mic-btn" class="mic-button">
        🎙️ Click to Speak
    </button>
""", unsafe_allow_html=True)

# Inject JavaScript
st.components.v1.html(js_code, height=0)

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
