import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import urllib.parse

# Page configuration
st.set_page_config(page_title="AI Agent - Nitish Kumar", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# Complete CSS for accurate Gemini UI and Fixed Bottom Chat alignment
st.markdown("""
    <style>
    /* Global dark theme and font matching the screenshot */
    .stApp {
        background-color: #0b121f !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', 'Segoe UI', Arial, sans-serif;
    }
    
    /* Hide default Streamlit clutter for a cleaner app look */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    
    /* Center layout for the initial greeting as seen in screenshot_19.png */
    .gemini-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 15vh;
    }
    
    /* Animated Gradient Text for the 'Hi Nitish' greeting */
    .gemini-greeting {
        font-size: 3.2rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }
    
    /* Fixed Positioning for the Chat Input at the bottom center */
    div[data-testid="stBottom"] {
        background-color: #0b121f !important;
        display: flex;
        justify-content: center;
        align-items: center;
        padding-bottom: 20px;
    }
    
    /* Styling for the central, pill-shaped Gemini Input bar */
    div[data-testid="stChatInput"] {
        max-width: 720px !important;
        margin: 0 auto !important;
        border-radius: 32px !important;
        border: 1px solid #3c4043 !important;
        background-color: #1e1f20 !important;
        padding: 4px 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    div[data-testid="stChatInput"] textarea {
        color: #e3e3e3 !important;
        background-color: transparent !important;
        font-size: 1.05rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Setup text model only (using multimodal for vision inputs)
@st.cache_resource
def load_ai_model():
    # Regular conversational model for chat and vision analysis
    return genai.GenerativeModel("gemini-1.5-flash")

try:
    chat_engine = load_ai_model()
except Exception as e:
    st.error(f"API Client Error: {e}")
    st.stop()

# Initialize Chat Memory state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MAIN CHAT INTERFACE ---

# If no messages exist, show the beautiful Gemini greeting
if not st.session_state.messages:
    st.markdown("""
        <div class="gemini-container">
            <h1 class="gemini-greeting">Hi Nitish kumar, what's the plan?</h1>
        </div>
    """, unsafe_allow_html=True)

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            # Display inline image that works without a payment profile
            st.image(message["content"], caption=message.get("caption", "Generated Image"))

# 2. ULTRA-PRO BOTTOM CHAT INPUT (Ask AI Agent ke bagal me plus sign fixed!)
user_payload = st.chat_input("Ask AI Agent...", accept_file=True, file_type=["pdf", "png", "jpg", "jpeg"])

if user_payload:
    # 3. PRO LOGIC: Handle User Text Input or File Input
    prompt_text = user_payload.text if user_payload.text else ""
    attached_file = user_payload.files[0] if user_payload.files else None
    
    # Render user command instantly on screen
    if prompt_text or attached_file:
        with st.chat_message("user"):
            if prompt_text:
                st.markdown(prompt_text)
            if attached_file:
                st.caption(f"📎 Attached Asset: {attached_file.name}")
        
        # Save to chat logs
        st.session_state.messages.append({"role": "user", "type": "text", "content": prompt_text if prompt_text else f"Uploaded {attached_file.name}"})

    # PRO ROUTING: Define regular chat vs image generation calls
    is_image_request = any(kw in prompt_text.lower() for kw in ["creat", "generate", "draw", "make a photo", "picture of", "image of"])

    # assistant response block
    with st.chat_message("assistant"):
        # 4. FIXED IMAGE ROUTE (The World-Class Pollinations Bypass)
        if is_image_request:
            with st.spinner("⚡ Matrix is constructing your image... Please wait"):
                try:
                    # PRO CODING: Standardize the prompt and encode it safely for direct display
                    encoded_prompt = urllib.parse.quote(prompt_text)
                    image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true"
                    
                    # Direct inline display—perfectly integrated!
                    st.image(image_url, caption=f"Result for: '{prompt_text}'")
                    
                    st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_url, "caption": prompt_text})
                except Exception as img_err:
                    st.error(f"Image generation tool error: {img_err}")
        
        # 5. FIXED CHAT ROUTE (Multimodal handling for Text / Screenshot / PDF)
        else:
            with st.spinner("Thinking..."):
                content_payload = []
                
                # Check for context files (Screenshots/PDFs)
                if attached_file:
                    file_extension = attached_file.name.split(".")[-1].lower()
                    if file_extension in ["png", "jpg", "jpeg"]:
                        # Convert screenshot to processable image bytes
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
                
                # Append main query
                content_payload.append(prompt_text if prompt_text else "Analyze this attached asset.")
                
                try:
                    response = chat_engine.generate_content(content_payload)
                    ai_reply = response.text
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "type": "text", "content": ai_reply})
                except Exception as chat_err:
                    st.error(f"Chat error: {chat_err}")
                    
    st.rerun()