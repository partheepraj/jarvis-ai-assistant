import streamlit as st
import streamlit.components.v1 as components
import time
from safe_agent import agent

# Page configuration
st.set_page_config(
    page_title="🤖 Jarvis AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
        text-align: right;
    }
    .assistant-message {
        background-color: #f3e5f5;
        margin-right: auto;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #4caf50;
        margin-right: 0.5rem;
    }
    .quick-button {
        margin: 0.25rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Jarvis, your AI assistant. How can I help you today?"}
    ]
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'voice_processed' not in st.session_state:
    st.session_state.voice_processed = None
if 'voice_processed_id' not in st.session_state:
    st.session_state.voice_processed_id = None
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""
if 'debug_logs' not in st.session_state:
    st.session_state.debug_logs = []


def process_command(command, source='keyboard'):
    command_text = (command or "").strip()
    if not command_text:
        return "No command provided"

    normalized_command = command_text.lower()
    debug_entry = f"[DEBUG] source={source} command={command_text} normalized={normalized_command}"
    st.session_state.debug_logs.append(debug_entry)
    print(debug_entry)

    with st.spinner(f"Processing {source} command..."):
        response = agent(normalized_command)

    response_entry = f"[DEBUG] response={response}"
    st.session_state.debug_logs.append(response_entry)
    print(response_entry)

    return response


# Handle voice command from query param
query_params = st.query_params
voice_text = query_params.get('voice', [None])[0]
voice_id = query_params.get('voice_id', [None])[0]
if voice_text:
    voice_debug = f"[DEBUG] voice_text received from query params: {voice_text} voice_id={voice_id}"
    st.session_state.debug_logs.append(voice_debug)
    st.session_state.debug_logs.append(f"[DEBUG] full query_params={query_params}")
    print(voice_debug)
    print('[DEBUG] full query_params=', query_params)

if voice_text and voice_id != st.session_state.voice_processed_id:
    st.session_state.user_input = voice_text
    st.session_state.messages.append({"role": "user", "content": voice_text})
    response = process_command(voice_text, source='voice')
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.voice_processed = voice_text
    st.session_state.voice_processed_id = voice_id
    st.rerun()


def quick_command(cmd):
    """Handle quick action buttons"""
    st.session_state.messages.append({"role": "user", "content": cmd})
    response = process_command(cmd, source='quick action')
    st.session_state.messages.append({"role": "assistant", "content": response})
    # st.rerun()  # Remove this as Streamlit handles reruns automatically

# Sidebar
with st.sidebar:
    st.title("🎛️ Control Panel")

    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Search Web", use_container_width=True):
            quick_command("search web")
        if st.button("🌐 Open Chrome", use_container_width=True):
            quick_command("open chrome")
        if st.button("📁 List Files", use_container_width=True):
            quick_command("list files")
        if st.button("🔊 Volume Up", use_container_width=True):
            quick_command("volume up")

    with col2:
        if st.button("💻 System Info", use_container_width=True):
            quick_command("system info")
        if st.button("🔇 Mute", use_container_width=True):
            quick_command("mute")
        if st.button("🔉 Volume Down", use_container_width=True):
            quick_command("volume down")
        if st.button("🔊 Unmute", use_container_width=True):
            quick_command("unmute")

    st.subheader("Settings")
    voice_enabled = st.checkbox("Enable Voice Output", value=True)
    safe_mode = st.checkbox("Safe Mode", value=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! Ready for new commands."}
        ]
        st.rerun()

    st.subheader("System Status")
    st.markdown('<div class="status-indicator"></div><span>Online</span>', unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">🤖 Jarvis AI Assistant</h1>', unsafe_allow_html=True)

# Chat container
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">👤 You: {message["content"]}</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">🤖 Jarvis: {message["content"]}</div>',
                       unsafe_allow_html=True)

# Input area
st.markdown("---")

# Text input
col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    user_input = st.text_input(
        "Type your command here...",
        key="user_input",
        placeholder="e.g., open chrome and search for python",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤 Send", use_container_width=True, type="primary")

with col3:
    st.write("")

# Handle send button or enter key
if send_button or (user_input and st.session_state.get('last_input') != user_input):
    if user_input.strip():
        st.session_state.last_input = user_input
        st.session_state.messages.append({"role": "user", "content": user_input})

        response = process_command(user_input, source='keyboard')
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Auto-scroll to bottom
        st.markdown('<script>window.scrollTo(0, document.body.scrollHeight);</script>',
                   unsafe_allow_html=True)

with st.expander('🎤 Voice Command'):
    st.write('Click the red button below and speak your command. Your speech will be filled into the input box automatically.')
    voice_html = """
    <div id="voice-container">
        <button id="start-voice" style="background: #ff6b6b; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
            🎤 Start Voice Recognition
        </button>
        <div id="voice-status" style="margin-top: 10px; color: #666;"></div>
    </div>

    <script>
        const startVoiceBtn = document.getElementById('start-voice');
        const voiceStatus = document.getElementById('voice-status');

        startVoiceBtn.addEventListener('click', function() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();

                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';

                recognition.onstart = function() {
                    voiceStatus.textContent = '🎤 Listening... Speak now!';
                    voiceStatus.style.color = '#4CAF50';
                    startVoiceBtn.disabled = true;
                    startVoiceBtn.textContent = '🎤 Listening...';
                };

                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    console.log('Voice recognition result:', transcript);
                    voiceStatus.textContent = '✅ Heard: "' + transcript + '"';
                    voiceStatus.style.color = '#2196F3';

                    const parentDoc = window.parent.document;
                    const input = parentDoc.querySelector('input[placeholder="e.g., open chrome and search for python"]');
                    const allInputs = Array.from(parentDoc.querySelectorAll('input[type="text"], textarea'));
                    const buttons = Array.from(parentDoc.querySelectorAll('button, [role="button"]'));
                    const sendButton = buttons.find(b => {
                        const text = (b.innerText || b.textContent || '').trim().toLowerCase();
                        return text.includes('send') || text.includes('submit');
                    });

                    if (!input) {
                        console.log('Voice input field not found by placeholder. Found inputs:', allInputs.length);
                        allInputs.forEach((el, idx) => console.log('input', idx, el.placeholder || el.getAttribute('aria-label') || el.type || el.tagName));
                    }

                    if (!sendButton) {
                        console.log('Send button not found. Candidate buttons:');
                        buttons.forEach((b, idx) => console.log('button', idx, (b.innerText || b.textContent || '').trim()));
                    }

                    if (input) {
                        input.focus();
                        input.value = transcript;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Filled Streamlit input with transcript');
                    }

                    if (sendButton) {
                        setTimeout(() => {
                            console.log('Clicking Send button');
                            sendButton.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
                            sendButton.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
                            sendButton.click();
                        }, 100);
                        return;
                    }

                    console.log('Send button not found, using URL redirect with voice_id');
                    const redirectUrl = window.location.origin + window.location.pathname + '?voice=' + encodeURIComponent(transcript.trim()) + '&voice_id=' + Date.now();
                    console.log('Redirecting to:', redirectUrl);
                    window.location.href = redirectUrl;
                };

                recognition.onerror = function(event) {
                    voiceStatus.textContent = '❌ Error: ' + event.error;
                    voiceStatus.style.color = '#f44336';
                    startVoiceBtn.disabled = false;
                    startVoiceBtn.textContent = '🎤 Start Voice Recognition';
                };

                recognition.onend = function() {
                    startVoiceBtn.disabled = false;
                    startVoiceBtn.textContent = '🎤 Start Voice Recognition';
                    setTimeout(() => {
                        voiceStatus.textContent = '';
                    }, 3000);
                };

                recognition.start();
            } else {
                voiceStatus.textContent = '❌ Speech recognition not supported in this browser';
                voiceStatus.style.color = '#f44336';
            }
        });
    </script>
    """
    components.html(voice_html, height=300, scrolling=False)

# Debug log
with st.expander('🪵 Debug logs', expanded=False):
    if st.session_state.debug_logs:
        for log in st.session_state.debug_logs[-20:]:
            st.write(log)
    else:
        st.write('No debug logs yet.')

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit • AI-powered assistant with voice capabilities*")

# Auto-focus on input (JavaScript)
st.markdown("""
<script>
    // Auto-focus on the text input
    setTimeout(function() {
        const inputs = document.querySelectorAll('input[type="text"]');
        if (inputs.length > 0) {
            inputs[inputs.length - 1].focus();
        }
    }, 100);
</script>
""", unsafe_allow_html=True)