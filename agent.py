import streamlit as st
import google.generativeai as genai
import pypdf

# Page config and styling
st.set_page_config(page_title="Premium Global AI Business Agent", page_icon="🤖", layout="wide")

# Advanced Custom CSS for Ultra-Premium Cyberpunk Business Dark Theme
st.markdown("""
    <style>
    /* Global background and font */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #10121d 0%, #07080d 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e2e8f0;
    }
    
    /* Glowing Title Effect */
    .premium-title {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 5px;
        text-shadow: 0 0 30px rgba(0, 242, 254, 0.2);
    }
    
    .premium-subtitle {
        color: #94a3b8;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 25px;
    }
    
    /* Glassmorphism Sidebar */
    div[data-testid="stSidebar"] {
        background-color: rgba(15, 18, 30, 0.75) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Custom style for cards and boxes */
    .status-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Make chat input look sleek */
    div[data-testid="stChatInput"] {
        border-radius: 14px !important;
        border: 1px solid rgba(0, 242, 254, 0.2) !important;
        background-color: #131722 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    /* Hide default streamlit badges */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Premium Header Layout
st.markdown('<h1 class="premium-title">🤖 Premium Global AI Business Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="premium-subtitle">⚡ Enterprise-Grade PDF Intelligence & Market Analytics</p>', unsafe_allow_html=True)
st.write("---")

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

# --- SIDEBAR: DESIGNER PANEL ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2fe; font-size:1.5rem; font-weight:700; margin-bottom:15px;'>📁 Control Center</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Upload documents to feed data directly into the AI's core memory core.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["pdf"])
    
    if uploaded_file is not None:
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            with st.spinner("Decoding document matrix..."):
                try:
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
                    
                    st.session_state.pdf_context = extracted_text
                    st.session_state.last_uploaded_file = uploaded_file.name
                except Exception as e:
                    st.error(f"Read Error: {e}")
                    
    if st.session_state.pdf_context:
        st.markdown(f"""
        <div class="status-box">
            <p style='color:#00ff88; margin:0; font-weight:600;'>🟢 DATA STREAM ACTIVE</p>
            <p style='color:#e2e8f0; font-size:0.85rem; margin:5px 0 0 0;'>File: {st.session_state.last_uploaded_file}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-box">
            <p style='color:#ff3b3b; margin:0; font-weight:600;'>🔴 NO DATA UPLOADED</p>
            <p style='color:#94a3b8; font-size:0.85rem; margin:5px 0 0 0;'>AI is running on standard knowledge base.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔄 Reset System Memory", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_context = ""
        if "last_uploaded_file" in st.session_state:
            del st.session_state.last_uploaded_file
        st.rerun()

# --- MAIN CHAT INTERFACE ---
# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_query := st.chat_input("Ask your premium AI Agent anything about business or your PDF..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Prepare complete prompt for AI
    full_prompt = ""
    if st.session_state.pdf_context:
        full_prompt += f"--- START OF UPLOADED DOCUMENT CONTEXT ---\n{st.session_state.pdf_context}\n--- END OF UPLOADED DOCUMENT CONTEXT ---\n\n"
        full_prompt += f"Instructions: You are an Ultra-Premium Global AI Business Agent. Analyze the document context above and give deep enterprise-level business insights to answer the question.\n\n"
    
    full_prompt += f"User Question: {user_query}"

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("AI Agent is computing insights..."):
            try:
                response = model.generate_content(full_prompt)
                ai_response = response.text
                message_placeholder.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                error_msg = f"System Error: {e}"
                message_placeholder.markdown(error_msg)