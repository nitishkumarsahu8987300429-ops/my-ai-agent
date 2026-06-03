import streamlit as st
import google.generativeai as genai
import pypdf

# Page config and styling for a completely clean layout
st.set_page_config(page_title="Gemini - Nitish Kumar", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# Advanced CSS to mirror Google Gemini's precise web UI
st.markdown("""
    <style>
    /* Global App Background */
    .stApp {
        background-color: #0b121f !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', 'Segoe UI', Arial, sans-serif;
    }
    
    /* Hide Streamlit elements to keep it clean */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    
    /* Center Layout Container */
    .gemini-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 12vh;
    }
    
    /* Animated Gradient Text matching original look */
    .gemini-greeting {
        font-size: 3.2rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }
    
    /* Custom Styling for the Gemini Chat Input Wrapper */
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

    /* Style Sidebar for document handling */
    div[data-testid="stSidebar"] {
        background-color: #0f141c !important;
        border-right: 1px solid #282c34;
    }
    
    .sidebar-title {
        color: #8ab4f8;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 15px;
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

# --- SIDEBAR (Hidden by default, open using top-left arrow for uploading docs) ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">📁 Context Files</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Add PDF for Gemini to reference", type=["pdf"])
    
    if uploaded_file is not None:
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            with st.spinner("Processing document..."):
                try:
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text: extracted_text += text + "\n"
                    st.session_state.pdf_context = extracted_text
                    st.session_state.last_uploaded_file = uploaded_file.name
                    st.success("Document attached! ✅")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.session_state.pdf_context = ""

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_context = ""
        st.rerun()

# --- MAIN INTERFACE ---

# If no chat has started, show the beautiful Gemini greeting page
if not st.session_state.messages:
    st.markdown("""
        <div class="gemini-container">
            <h1 class="gemini-greeting">Hi Nitish kumar, what's the plan?</h1>
        </div>
    """, unsafe_allow_html=True)

# Display chat history neatly
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input Box (Capsule Design)
if user_query := st.chat_input("Ask Gemini..."):
    # If it's the first message, rerun to clear the greeting instantly
    is_first_message = len(st.session_state.messages) == 0
    
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Prepare prompt
    full_prompt = ""
    if st.session_state.pdf_context:
        full_prompt += f"[Document Context Included]\n{st.session_state.pdf_context}\n\n"
    full_prompt += user_query

    # Generate response
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