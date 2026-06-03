import streamlit as st
import google.generativeai as genai
import pypdf

# Page config and styling for an absolute Gemini layout
st.set_page_config(page_title="AI Agent - Nitish Kumar", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to mimic the accurate Gemini dropdown pop-up menu
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #0b121f !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', 'Segoe UI', Arial, sans-serif;
    }
    
    /* Hide default Streamlit clutter */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    div[data-testid="stSidebar"] {visibility: hidden;}
    
    /* Center Layout Container */
    .gemini-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 15vh;
    }
    
    /* Animated Gradient Text */
    .gemini-greeting {
        font-size: 3.2rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }
    
    /* Gemini-styled Floating Pop-up Menu Container */
    .gemini-popup {
        background-color: #1e1f20;
        border: 1px solid #3c4043;
        border-radius: 16px;
        padding: 12px 0px;
        width: 100%;
        max-width: 280px;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.5);
        margin-bottom: -10px;
    }
    
    /* Dropdown item styles */
    .popup-item {
        display: flex;
        align-items: center;
        padding: 10px 20px;
        font-size: 0.95rem;
        color: #e3e3e3;
        cursor: pointer;
        transition: background 0.2s;
    }
    .popup-item:hover {
        background-color: #2d2f31;
    }
    
    /* Chat Input Styling */
    div[data-testid="stChatInput"] {
        max-width: 720px !important;
        margin: 0 auto !important;
        border-radius: 32px !important;
        border: 1px solid #3c4043 !important;
        background-color: #1e1f20 !important;
        padding: 4px 12px !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        color: #e3e3e3 !important;
        background-color: transparent !important;
        font-size: 1.05rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Gemini Client
@st.cache_resource
def get_ai_model():
    return genai.GenerativeModel(model_name="gemini-1.5-flash")

try:
    model = get_ai_model()
except Exception as e:
    st.error(f"API Client Error: {e}")
    st.stop()

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# --- MAIN INTERFACE ---

# Show greeting if chat screen is empty
if not st.session_state.messages:
    st.markdown("""
        <div class="gemini-container">
            <h1 class="gemini-greeting">Hi Nitish kumar, what's the plan?</h1>
        </div>
    """, unsafe_allow_html=True)

# --- INLINE UTILITY MATRIX (Pop-up system) ---
st.markdown("<div style='max-width:720px; margin: 0 auto;'>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 11])
with col1:
    # Trigger checkbox that acts as our click button
    if st.button("➕", help="Click to open menu"):
        st.session_state.menu_open = not st.session_state.menu_open

with col2:
    if st.session_state.pdf_context and not st.session_state.menu_open:
        st.markdown(f"<span style='color:#4ade80; font-size:0.9rem; background:#0d3c26; padding: 4px 12px; border-radius:20px;'>Attached: {st.session_state.last_uploaded_file} ✅</span>", unsafe_allow_html=True)

# If menu is active, display the beautiful floating item panel
if st.session_state.menu_open:
    col_menu, _ = st.columns([4, 6])
    with col_menu:
        st.markdown("""
            <div class="gemini-popup">
                <div class="popup-item">📄 Upload Files (Select document below)</div>
                <div class="popup-item" style="color: #80868b;">☁️ Add from Drive (Premium Feature)</div>
                <div class="popup-item" style="color: #80868b;">🔍 Deep Research (Enterprise Only)</div>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
        if uploaded_file is not None:
            if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
                with st.spinner("Embedding document matrix..."):
                    try:
                        pdf_reader = pypdf.PdfReader(uploaded_file)
                        extracted_text = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text: extracted_text += text + "\n"
                        st.session_state.pdf_context = extracted_text
                        st.session_state.last_uploaded_file = uploaded_file.name
                        st.session_state.menu_open = False  # Close menu automatically
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            # Clear context if file removed
            if "last_uploaded_file" in st.session_state and not uploaded_file:
                st.session_state.pdf_context = ""
                del st.session_state.last_uploaded_file

st.markdown("</div>", unsafe_allow_html=True)

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Box
if user_query := st.chat_input("Ask AI Agent..."):
    is_first_message = len(st.session_state.messages) == 0
    st.session_state.menu_open = False  # Auto close on enter
    
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Prepare prompt
    full_prompt = ""
    if st.session_state.pdf_context:
        full_prompt += f"[Document Context]\n{st.session_state.pdf_context}\n\n"
    full_prompt += user_query

    # Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = model.generate_content(full_prompt)
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            message_placeholder.markdown(f"Error: {e}")
            
    if is_first_message:
        st.rerun()