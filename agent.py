import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import urllib.parse

# 1. Page Configuration
st.set_page_config(page_title="AI Agent - Nitish Kumar", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# 2. Premium Dark UI Theme CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0b121f !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', sans-serif;
    }
    header, footer, div[data-testid="stToolbar"], div[data-testid="stSidebar"] {
        visibility: hidden !important;
    }
    .gemini-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 12vh;
        margin-bottom: 5vh;
    }
    .gemini-greeting {
        font-size: 3.2rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    div[data-testid="stBottom"] {
        background-color: #0b121f !important;
        padding-bottom: 20px;
    }
    div[data-testid="stChatInput"] {
        max-width: 760px !important;
        margin: 0 auto !important;
        border-radius: 28px !important;
        border: 1px solid #3c4043 !important;
        background-color: #1e1f20 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Setup Gemini Text Engine
@st.cache_resource
def load_chat_core():
    return genai.GenerativeModel("gemini-1.5-flash")

try:
    chat_engine = load_chat_core()
except Exception as e:
    st.error(f"Engine connection failed: {e}")
    st.stop()

# Initialize Chat Memory Matrix
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- MAIN INTERFACE DISPLAY ---
if not st.session_state.chat_history:
    st.markdown("""
        <div class="gemini-container">
            <h1 class="gemini-greeting">Hi Nitish kumar, what's the plan?</h1>
        </div>
    """, unsafe_allow_html=True)

# Container to lock dynamic message rendering without refresh bugs
chat_placeholder = st.container()

with chat_placeholder:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "image":
                st.image(message["content"], caption=message.get("caption", "Generated Asset"))

# 4. INLINE CHAT WITH PLUS COMPONENT
user_payload = st.chat_input(
    "Ask AI Agent...", 
    accept_file=True, 
    file_type=["pdf", "png", "jpg", "jpeg"]
)

if user_payload:
    prompt_text = user_payload.text if user_payload.text else ""
    attached_file = user_payload.files[0] if user_payload.files else None
    
    if prompt_text or attached_file:
        # Append User Input instantly to layout container
        with chat_placeholder.chat_message("user"):
            if prompt_text:
                st.markdown(prompt_text)
            if attached_file:
                st.caption(f"📎 Attached Asset: {attached_file.name}")
        
        st.session_state.chat_history.append({
            "role": "user", 
            "type": "text", 
            "content": prompt_text if prompt_text else f"Uploaded {attached_file.name}"
        })

    # Global Image Verification Key-checks (Handles misspelling like 'creat')
    clean_prompt = prompt_text.lower()
    is_image_request = any(kw in clean_prompt for kw in ["creat", "generate", "draw", "make a photo", "picture of", "image of", "snake", "buterfly", "dog"])

    # Process AI Response block
    with chat_placeholder.chat_message("assistant"):
        if is_image_request:
            with st.spinner("⚡ Creating your custom image... Please wait"):
                try:
                    # Clean and encode the string cleanly for direct image rendering
                    encoded_prompt = urllib.parse.quote(prompt_text)
                    image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
                    
                    # Direct display injects perfectly without relying on st.rerun
                    st.image(image_url, caption=f"Result for: '{prompt_text}'")
                    
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "type": "image", 
                        "content": image_url, 
                        "caption": prompt_text
                    })
                except Exception as img_err:
                    st.error(f"Image Pipeline Interrupted: {img_err}")
        
        else:
            with st.spinner("Thinking..."):
                content_payload = []
                
                if attached_file:
                    file_extension = attached_file.name.split(".")[-1].lower()
                    if file_extension in ["png", "jpg", "jpeg"]:
                        screenshot_img = Image.open(attached_file)
                        content_payload.append(screenshot_img)
                    elif file_extension == "pdf":
                        pdf_reader = pypdf.PdfReader(attached_file)
                        extracted_text = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text: extracted_text += text + "\n"
                        content_payload.append(f"[Document Context: {attached_file.name}]\n{extracted_text}\n\n")
                
                content_payload.append(prompt_text if prompt_text else "Analyze this attached asset.")
                
                try:
                    response = chat_engine.generate_content(content_payload)
                    ai_reply = response.text
                    st.markdown(ai_reply)
                    st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": ai_reply})
                except Exception as chat_err:
                    st.error(f"Chat Error: {chat_err}")