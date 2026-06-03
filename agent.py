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
    /* Fixed Bottom Chat styling to force premium integration */
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

# 3. Setup Gemini Core Engines
@st.cache_resource
def load_ai_cores():
    # Regular Chat Model (Supports Vision/Multimodal natively)
    chat_model = genai.GenerativeModel("gemini-2.5-flash")
    # Native High-Fidelity Image Generator Engine
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
            st.image(message["content"], caption=message.get("caption", "Generated Image"))

# 4. ULTRA-PRO INLINE CHAT WITH BUILT-IN PLUS COMPONENT
# Using native accept_file directly injects the Plus symbol inside the box right next to text input!
user_payload = st.chat_input(
    "Ask AI Agent...", 
    accept_file=True, 
    file_type=["pdf", "png", "jpg", "jpeg"]
)

if user_payload:
    # Separate Text Prompt and File Elements safely
    prompt_text = user_payload.text if user_payload.text else ""
    attached_file = user_payload.files[0] if user_payload.files else None
    
    # Render user command instantly
    if prompt_text or attached_file:
        with st.chat_message("user"):
            if prompt_text:
                st.markdown(prompt_text)
            if attached_file:
                st.caption(f"📎 Attached Document: {attached_file.name}")
        
        # Save to logs
        st.session_state.chat_history.append({"role": "user", "type": "text", "content": f"{prompt_text} (File: {attached_file.name if attached_file else 'None'})"})

    # Check Engine Target: Image Generation vs Chat Processing
    is_image_request = any(keyword in prompt_text.lower() for keyword in ["create image", "generate picture", "draw", "make a photo", "create an image", "picture of"])

    with st.chat_message("assistant"):
        # ROUTE A: HIGH-POWERED IMAGE CREATION ENGINE
        if is_image_request:
            with st.spinner("⚡ Matrix generating your custom image..."):
                try:
                    result = image_engine.generate_content(prompt_text)
                    # Extract raw image bytes from response
                    for part in result.candidates[0].content.parts:
                        if part.inline_data:
                            img_bytes = part.inline_data.data
                            image_object = Image.open(io.BytesIO(img_bytes))
                            
                            st.image(image_object, caption=f"Result for: '{prompt_text}'")
                            st.session_state.chat_history.append({"role": "assistant", "type": "image", "content": image_object, "caption": prompt_text})
                            break
                except Exception as img_err:
                    st.error(f"Image Engine Interruption: {img_err}. Make sure your prompt describes a clear scene.")
        
        # ROUTE B: MULTIMODAL CHAT ENGINE (TEXT/PDF/SCREENSHOTS)
        else:
            with st.spinner("Thinking..."):
                content_payload = []
                
                # Append attached contextual layers if present
                if attached_file:
                    file_extension = attached_file.name.split(".")[-1].lower()
                    if file_extension in ["png", "jpg", "jpeg"]:
                        # Convert screenshot image bytes directly for multimodal processing
                        screenshot_img = Image.open(attached_file)
                        content_payload.append(screenshot_img)
                    elif file_extension == "pdf":
                        # Process PDF Data 
                        pdf_reader = pypdf.PdfReader(attached_file)
                        extracted_text = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text: extracted_text += text + "\n"
                        content_payload.append(f"[Document Context: {attached_file.name}]\n{extracted_text}\n\n")
                
                # Append main user question string
                content_payload.append(prompt_text if prompt_text else "Analyze this attached asset.")
                
                try:
                    response = chat_engine.generate_content(content_payload)
                    ai_reply = response.text
                    st.markdown(ai_reply)
                    st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": ai_reply})
                except Exception as chat_err:
                    st.error(f"Chat Matrix Error: {chat_err}")
                    
    # Force seamless sync rerun
    st.rerun()