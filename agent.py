import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import io

# 1. Page Configuration
st.set_page_config(page_title="AI Agent - Nitish Kumar", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# 2. Premium Professional Gemini Layout CSS
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

# 3. Setup Gemini Core Engines Safely
@st.cache_resource
def load_ai_cores():
    # Stable 1.5/2.5 models used for reliable conversational API calls
    chat_model = genai.GenerativeModel("gemini-1.5-flash")
    image_model = genai.GenerativeModel("imagen-3.0-generate-002")
    return chat_model, image_model

try:
    chat_engine, image_engine = load_ai_cores()
except Exception as e:
    st.error(f"Engine connection failed: {e}")
    st.stop()

# Initialize Persistent Brain Memory Matrix
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- MAIN INTERFACE DISPLAY ---

if not st.session_state.chat_history:
    st.markdown("""
        <div class="gemini-container">
            <h1 class="gemini-greeting">Hi Nitish kumar, what's the plan?</h1>
        </div>
    """, unsafe_allow_html=True)

# Print Chat logs dynamically 
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"], caption=message.get("caption", "Generated Asset"))

# 4. ULTRA-PRO INLINE CHAT WITH BUILT-IN PLUS COMPONENT
user_payload = st.chat_input(
    "Ask AI Agent...", 
    accept_file=True, 
    file_type=["pdf", "png", "jpg", "jpeg"]
)

if user_payload:
    prompt_text = user_payload.text if user_payload.text else ""
    attached_file = user_payload.files[0] if user_payload.files else None
    
    if prompt_text or attached_file:
        with st.chat_message("user"):
            if prompt_text:
                st.markdown(prompt_text)
            if attached_file:
                st.caption(f"📎 Attached Asset: {attached_file.name}")
        
        # Log to structural session state safely
        st.session_state.chat_history.append({
            "role": "user", 
            "type": "text", 
            "content": prompt_text if prompt_text else f"Uploaded {attached_file.name}"
        })

    # Advanced keywords matching logic (Fixed spelling mistake handling like 'creat')
    clean_prompt = prompt_text.lower()
    is_image_request = any(kw in clean_prompt for kw in ["creat", "generate", "draw", "make a photo", "picture of", "image of", "buterfly"])

    with st.chat_message("assistant"):
        # ROUTE A: EXTRA-POWERFUL IMAGE CREATION ENGINE (IMAGEN 3)
        if is_image_request:
            with st.spinner("⚡ Creating your custom image... Please wait a moment"):
                try:
                    # Enforce high-level prompt extraction
                    result = image_engine.generate_content(prompt_text if prompt_text else "A beautiful abstract render")
                    
                    # Direct check for valid generation packets
                    if result.candidates and result.candidates[0].content.parts:
                        for part in result.candidates[0].content.parts:
                            if part.inline_data:
                                img_bytes = part.inline_data.data
                                image_object = Image.open(io.BytesIO(img_bytes))
                                
                                st.image(image_object, caption=f"Result for: '{prompt_text}'")
                                st.session_state.chat_history.append({"role": "assistant", "type": "image", "content": image_object, "caption": prompt_text})
                                break
                    else:
                        st.warning("Google's safety filter blocked this generation prompt. Try using different words!")
                except Exception as img_err:
                    st.error(f"Generation Note: Imagen 3 API is processing heavy load. Error trace: {img_err}")
        
        # ROUTE B: CONVERSATIONAL MULTIMODAL ENGINE
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
                    
    st.rerun()