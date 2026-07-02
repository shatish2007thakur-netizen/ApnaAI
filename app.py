import streamlit as strl
from google import genai
import json
import os

# ================= STREAMLIT PAGE CONFIG =================
strl.set_page_config(page_title="JARVIS AI ONLINE SYSTEM", page_icon="🤖", layout="centered")

# Custom CSS for Jarvis Terminal View
strl.markdown("""
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
        height: 300px;
        overflow-y: auto;
        margin-bottom: 20px;
        white-space: pre-wrap;
    }
    /* Hidden element hack for JS communication */
    div[data-testid="stTextInput"] {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title Header
strl.markdown('<div class="terminal-title">JARVIS AI ONLINE SYSTEM</div>', unsafe_allow_html=True)

# ================= GEMINI CONFIGURATION =================
if "GEMINI_API_KEY" in strl.secrets:
    api_key = strl.secrets["GEMINI_API_KEY"]
else:
    api_key = None

@strl.cache_resource
def get_ai_client(key):
    if key:
        try:
            return genai.Client(api_key=key)
        except Exception:
            return None
    return None

ai_client = get_ai_client(api_key)

# Initialize Session States
if "chat_history" not in strl.session_state:
    strl.session_state.chat_history = "Jarvis: Systems online. Jarvis AI initialized.\nJarvis: Ready for your command, Sir."
if "tts_text" not in strl.session_state:
    strl.session_state.tts_text = "Systems initialized with Gemini AI. I am online, Sir."
if "last_processed_query" not in strl.session_state:
    strl.session_state.last_processed_query = ""

# ================= CORE PROCESSOR =================
def process_command(command):
    if not command or command.strip() == "":
        return
        
    if strl.session_state.last_processed_query == command:
        return

    strl.session_state.last_processed_query = command
    strl.session_state.chat_history += f"\n\nYou: {command}"
    cmd = command.lower().strip()
    
    # 1. EXIT COMMANDS
    if "stop" in cmd or "exit" in cmd or "bye jarvis" in cmd:
        reply = "Going offline. Goodbye, Sir."
        strl.session_state.chat_history += f"\n\nJarvis: {reply}"
        strl.session_state.tts_text = reply
        
    # 2. OS/BROWSER CAPABILITIES
    elif "open google" in cmd:
        reply = "Opening Google, Sir."
        strl.session_state.chat_history += f"\n\nJarvis: {reply}"
        strl.session_state.tts_text = reply
        strl.markdown('<meta http-equiv="refresh" content="0;URL=\'https://www.google.com\'" />', unsafe_allow_html=True)
        
    elif "open youtube" in cmd:
        reply = "Opening YouTube, Sir."
        strl.session_state.chat_history += f"\n\nJarvis: {reply}"
        strl.session_state.tts_text = reply
        strl.markdown('<meta http-equiv="refresh" content="0;URL=\'https://www.youtube.com\'" />', unsafe_allow_html=True)

    # 3. GEMINI CORE RESPONSE
    else:
        if not ai_client:
            reply = "Sir, Gemini API Key core component missing configuration."
            strl.session_state.chat_history += f"\n\nJarvis: {reply}"
            strl.session_state.tts_text = reply
        else:
            try:
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=command,
                    config={
                        'system_instruction': "You are JARVIS, a helpful, ultra-smart AI assistant. Keep responses sweet, clean, smart, and under 2 sentences. Speak like a loyal assistant."
                    }
                )
                reply = response.text.strip()
                strl.session_state.chat_history += f"\n\nJarvis: {reply}"
                strl.session_state.tts_text = reply
            except Exception as e:
                if "429" in str(e):
                    reply = "Sir, Streamlit Cloud servers are currently facing high traffic with Gemini API. Please try again in a few seconds."
                else:
                    reply = f"Sir, I faced an error connecting to the AI core. Details: {str(e)[:30]}"
                strl.session_state.chat_history += f"\n\nJarvis: {reply}"
                strl.session_state.tts_text = "Apologies Sir, server is busy."

# ================= JAVASCRIPT FOR SPEECH & TTS =================
# We integrate this smoothly directly inside the app body
js_code = f"""
<script>
    function speak(text) {{
        if ('speechSynthesis' in window && text !== "") {{
            window.speechSynthesis.cancel(); 
            var msg = new SpeechSynthesisUtterance(text);
            var voices = window.speechSynthesis.getVoices();
            if(voices.length > 0) {{
                msg.voice = voices[0]; 
            }}
            msg.rate = 1.0;
            window.speechSynthesis.speak(msg);
        }}
    }}

    // Trigger TTS on load
    var current_tts = `{strl.session_state.tts_text}`;
    if (current_tts !== "") {{
        speak(current_tts);
    }}

    function startListening() {{
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            alert("Your browser does not support Speech Recognition. Please use Chrome.");
            return;
        }}
        
        var recognition = new SpeechRecognition();
        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        recognition.start();

        recognition.onresult = function(event) {{
            var speechToText = event.results[0][0].transcript;
            
            // Find standard Streamlit inputs via parent window securely
            var inputs = window.parent.document.querySelectorAll('input[type="text"]');
            if(inputs.length > 0) {{
                inputs[0].value = speechToText;
                inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                // Simulate pressing Enter key
                setTimeout(function() {{
                    inputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    var buttons = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {{
                        if (buttons[i].textContent.includes("SEND")) {{
                            buttons[i].click();
                            break;
                        }}
                    }}
                }}, 500);
            }}
        }};
    }}
</script>
"""
strl.components.v1.html(js_code, height=0, width=0)

# Display Status and Logs
st_status = strl.empty()
st_status.markdown('<div class="terminal-status">Status: Standby. Use terminal input below or Initialize Mic</div>', unsafe_allow_html=True)
strl.markdown(f'<div class="chat-box">{strl.session_state.chat_history}</div>', unsafe_allow_html=True)

# --- Manual & Voice Combined Input Box ---
col1, col2 = strl.columns([3, 1])
with col1:
    # Is input widget ko JS direct query inject karne ke liye use karega
    text_input = strl.text_input("Type command manually here:", key="manual_text_input", label_visibility="collapsed", placeholder="Type or speak a command...")
with col2:
    send_click = strl.button("SEND ↵", use_container_width=True)

# Trigger Processor if text submitted
if (text_input and text_input != strl.session_state.last_processed_query) or (send_click and text_input):
    st_status.markdown('<div class="terminal-status">Status: Processing Command...</div>', unsafe_allow_html=True)
    process_command(text_input)
    strl.rerun()

# Main Interactive Custom Mic Activation Button 
if strl.button("🎙️ INITIALIZE MIC SYSTEMS", use_container_width=True):
    # This invokes the JS speech trigger built on parent window level
    strl.components.v1.html(js_code + "<script>startListening();</script>", height=0, width=0)
