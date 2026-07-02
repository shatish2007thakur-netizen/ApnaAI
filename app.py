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
    /* Hidden bridge component style */
    div[data-testid="stMarkdownContainer"] > iframe {
        display: none;
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
    strl.session_state.tts_text = ""

# ================= CORE PROCESSOR =================
def process_command(command):
    if not command or command.strip() == "":
        return
        
    strl.session_state.chat_history += f"\n\nYou: {command}"
    cmd = command.lower().strip()
    
    if "stop" in cmd or "exit" in cmd or "bye jarvis" in cmd:
        reply = "Going offline. Goodbye, Sir."
        strl.session_state.chat_history += f"\n\nJarvis: {reply}"
        strl.session_state.tts_text = reply
        
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
                    reply = "Sir, request rate limit reached. Please wait 5 seconds after your next command."
                else:
                    reply = f"Sir, I faced an error connecting to the AI core. Details: {str(e)[:30]}"
                strl.session_state.chat_history += f"\n\nJarvis: {reply}"
                strl.session_state.tts_text = "Apologies Sir, server is busy."

# Status Bar
st_status = strl.empty()
st_status.markdown('<div class="terminal-status">Status: Standby. Use terminal input below or Initialize Mic</div>', unsafe_allow_html=True)

# Display Terminal logs
strl.markdown(f'<div class="chat-box">{strl.session_state.chat_history}</div>', unsafe_allow_html=True)

# ================= HIDDEN VOICE INPUT BRIDGE =================
# Yeh invisible input box pure page par JavaScript ka bola hua data receive karega
voice_bridge_text = strl.text_input("Voice Input Catch", key="hidden_voice_bridge", label_visibility="collapsed")

if voice_bridge_text:
    # Jaise hi JS se data isme aayega, hum isko process karenge aur box khali kar denge
    process_command(voice_bridge_text)
    # Clear input state manually to avoid looping
    strl.empty()
    strl.rerun()

# ================= JAVASCRIPT & CUSTOM MIC BUTTON =================
js_and_html = f"""
<div style="margin-bottom: 10px;">
    <button id="mic-btn" style="
        width: 100%; 
        padding: 14px; 
        border-radius: 8px; 
        border: 1px solid #ffffff; 
        background-color: #ffffff; 
        color: #000000; 
        font-weight: bold; 
        cursor: pointer;
        font-size: 16px;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        transition: 0.3s;">
        🎙️ INITIALIZE MIC SYSTEMS
    </button>
</div>

<script>
    // --- TEXT TO SPEECH (Jarvis Voice Reply) ---
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

    var current_tts = `{strl.session_state.tts_text}`;
    if (current_tts !== "") {{
        speak(current_tts);
    }}

    // --- SPEECH RECOGNITION (Live Mic System) ---
    const button = document.getElementById('mic-btn');
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {{
        button.innerText = "❌ Browser Mic Not Supported";
        button.style.backgroundColor = "#ff4b4b";
        button.style.color = "white";
    }} else {{
        var recognition = new SpeechRecognition();
        recognition.lang = 'en-IN'; // Mix English-Hindi language support
        recognition.interimResults = false;
        
        button.addEventListener('click', () => {{
            button.innerText = "⏳ LISTENING CORE ACTIVE...";
            button.style.backgroundColor = "#4af626";
            button.style.color = "black";
            recognition.start();
        }});
        
        recognition.onresult = function(event) {{
            var speechToText = event.results[0][0].transcript;
            
            button.innerText = "🎙️ INITIALIZE MIC SYSTEMS";
            button.style.backgroundColor = "#ffffff";
            button.style.color = "#000000";
            
            // Streamlit ke hidden input box ko dhund kar usme text daalna aur submit trigger karna
            var inputs = window.parent.document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {{
                // Pehla hidden box jo humne upar banaya h use target karega
                var targetInput = inputs[0]; 
                targetInput.value = speechToText;
                
                // Streamlit ko batane ke liye ki input change ho gaya h
                targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                // Submit logic automatically trigger karne ke liye enter stroke simulate karna
                var ke = new KeyboardEvent('keydown', {{ bubbles: true, cancelable: true, keyCode: 13, key: 'Enter' }});
                targetInput.dispatchEvent(ke);
            }}
        }};
        
        recognition.onerror = function() {{
            button.innerText = "❌ MIC ERROR! TRY AGAIN";
            button.style.backgroundColor = "#ff4b4b";
            button.style.color = "white";
            setTimeout(() => {{
                button.innerText = "🎙️ INITIALIZE MIC SYSTEMS";
                button.style.backgroundColor = "#ffffff";
                button.style.color = "#000000";
            }}, 2000);
        }};
    }}
</script>
"""

# HTML block inject karna button display karne ke liye
strl.components.v1.html(js_and_html, height=65)

# ================= MANUAL TEXT INPUT FORM =================
with strl.form(key="command_form", clear_on_submit=True):
    text_input = strl.text_input("Type command manually here:", placeholder="Type a command and press Enter...")
    submit_button = strl.form_submit_button("SEND COMMAND ↵", use_container_width=True)
    
    if submit_button and text_input:
        process_command(text_input)
        strl.rerun()
