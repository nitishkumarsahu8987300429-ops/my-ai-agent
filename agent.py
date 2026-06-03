import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

# 1. Page Configuration (Ekdum Clean UI)
st.set_page_config(page_title="AI Agent - Nitish Kumar", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# 2. Premium Gemini Dark UI Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0b121f !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', 'Segoe UI', sans-serif;
    }
    header, footer, div[data-testid="stToolbar"] {
        visibility: hidden !important;
    }
    .gemini-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 15vh;
    }
    .gemini-greeting {
        font-size: 3.2rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }
    div[data-testid="stBottom"] {
        background-color: #0b121f !important;
        padding-bottom: 20px;
    }
    div[data-testid="stChatInput"] {
        max-width: 720px !important;
        margin: 0 auto !important;
        border-radius: 32px !important;
        border: 1px solid #3c4043 !important;
        background-color: #1e1f20 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Setup Ultra-Fast Gemini 1.5 Flash Model
@st.cache_resource
def load_ai_model():
    return genai.GenerativeModel("gemini-1.5-flash")

try:
    chat_engine = load_ai_model()
except Exception as e:
    st.error(f"API Client Error: {e}")
    st.stop()

# Initialize Chat Memory Matrix
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MAIN CHAT INTERFACE ---

# Initial Greeting
if not st.session_state.messages:
    st.markdown("""
        <div class="gemini-container">
            <h1 class="gemini-greeting">Hi Nitish kumar, what's the plan?</h1>
        </div>
    """, unsafe_allow_html=True)

# Display Chat History
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 4. CHAT INPUT WITH FILE UPLOAD COMPONENT (Plus Icon)
user_payload = st.chat_input("Ask AI Agent...", accept_file=True, file_type=["pdf", "png", "jpg", "jpeg"])

if user_payload:
    prompt_text = user_payload.text if user_payload.text else ""
    attached_file = user_payload.files[0] if user_payload.files else None
    
    if prompt_text or attached_file:
        with chat_container.chat_message("user"):
            if prompt_text:
                st.markdown(prompt_text)
            if attached_file:
                st.caption(f"📎 Attached: {attached_file.name}")
        
        # Save user message to memory
        user_display_text = prompt_text if prompt_text else f"Analyzed uploaded file: {attached_file.name}"
        st.session_state.messages.append({"role": "user", "content": user_display_text})

    # Core Multimodal AI Processing Block
    with chat_container.chat_message("assistant"):
        with st.spinner("Thinking..."):
            content_payload = []
            
            # If user uploaded a document or an image
            if attached_file:
                file_extension = attached_file.name.split(".")[-1].lower()
                
                # Handle Image / Screenshot Analysis
                if file_extension in ["png", "jpg", "jpeg"]:
                    screenshot_img = Image.open(attached_file)
                    content_payload.append(screenshot_img)
                    
                # Handle PDF Document Scanning
                elif file_extension == "pdf":
                    try:
                        pdf_reader = pypdf.PdfReader(attached_file)
                        extracted_text = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text: 
                                extracted_text += text + "\n"
                        content_payload.append(f"[Document Content from {attached_file.name}]:\n{extracted_text}\n\n")
                    except Exception as pdf_err:
                        st.error(f"Failed to read PDF: {pdf_err}")
            
            # Append the main text query
            content_payload.append(prompt_text if prompt_text else "Examine the attached asset carefully and give a summary.")
            
            # Fire API Request
            try:
                response = chat_engine.generate_content(content_payload)
                ai_reply = response.text
                st.markdown(ai_reply)
                
                # Save assistant response to memory
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as chat_err:
                st.error(f"Chat error: {chat_err}")
                
    st.rerun()