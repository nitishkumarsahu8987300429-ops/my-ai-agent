import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import json
import os

# 1. Page Configuration & Setup
st.set_page_config(page_title="Enterprise AI Agent Pro", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

# 2. Premium Commercial UI Styling (Client-Ready)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b121f !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', sans-serif;
    }
    /* Sidebar Styling for Admin Panel */
    section[data-testid="stSidebar"] {
        background-color: #111a2e !important;
        border-right: 1px solid #1e293b !important;
    }
    .sidebar-title {
        color: #4285f4;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 15px;
    }
    .gemini-container {
        text-align: center;
        margin-top: 10vh;
        margin-bottom: 5vh;
    }
    .gemini-greeting {
        font-size: 3rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0, #ea4335);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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

# 3. Setup Core AI Engine
@st.cache_resource
def load_ai_model():
    return genai.GenerativeModel("gemini-1.5-flash")

try:
    chat_engine = load_ai_model()
except Exception as e:
    st.error(f"Engine Connection Failed: {e}")
    st.stop()

# Persistent Local File Database (For Leads and Knowledge)
LEADS_FILE = "client_leads.json"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "company_context" not in st.session_state:
    st.session_state.company_context = ""

# --- 🛠️ FEATURE 1: CUSTOM ADMIN & KNOWLEDGE BASE (SIDEBAR) ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">⚙️ Client Admin Panel</p>', unsafe_allow_html=True)
    st.write("Feed your business data here so the AI learns about your company.")
    
    # Client uploads their business info / price list / FAQs
    biz_file = st.file_uploader("Upload Company Knowledge Base (PDF/TXT)", type=["pdf", "txt"], key="biz_upload")
    
    if biz_file:
        with st.spinner("AI is learning your business data..."):
            file_ext = biz_file.name.split(".")[-1].lower()
            if file_ext == "txt":
                st.session_state.company_context = biz_file.read().decode("utf-8")
            elif file_ext == "pdf":
                pdf_reader = pypdf.PdfReader(biz_file)
                extracted_text = ""
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text: extracted_text += text + "\n"
                st.session_state.company_context = extracted_text
            st.success("✅ AI updated with company data!")

    st.markdown("---")
    st.markdown('<p class="sidebar-title">📊 Captured Business Leads</p>', unsafe_allow_html=True)
    
    # Download Leads Button for Client
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r") as f:
            leads_data = f.read()
        st.download_button(label="📥 Download Leads (JSON)", data=leads_data, file_name="captured_leads.json", mime="application/json")
    else:
        st.info("No leads captured yet. Keep chatting!")


# --- MAIN USER CHAT INTERFACE ---

if not st.session_state.messages:
    st.markdown("""
        <div class="gemini-container">
            <h1 class="gemini-greeting">Welcome to Corporate AI Support</h1>
            <p style='color:#9aa0a6;'>How can our automated business agent help you today?</p>
        </div>
    """, unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 🛠️ FEATURE 2: USER INPUT & LEAD CAPTURE PIPELINE ---
user_payload = st.chat_input("Ask anything about our services...", accept_file=True, file_type=["png", "jpg", "jpeg", "pdf"])

if user_payload:
    prompt_text = user_payload.text if user_payload.text else ""
    attached_file = user_payload.files[0] if user_payload.files else None
    
    if prompt_text or attached_file:
        with chat_container.chat_message("user"):
            if prompt_text:
                st.markdown(prompt_text)
            if attached_file:
                st.caption(f"📎 Attached Asset: {attached_file.name}")
        
        user_display = prompt_text if prompt_text else f"Uploaded data file: {attached_file.name}"
        st.session_state.messages.append({"role": "user", "content": user_display})

        # AUTOMATED LEAD EXTRATOR: If user types email or phone number, background saves it automatically!
        import re
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', prompt_text)
        phones = re.findall(r'\b\d{10}\b', prompt_text)
        
        if emails or phones:
            lead_entry = {"email": emails if emails else "N/A", "phone": phones if phones else "N/A", "raw_message": prompt_text}
            # Save directly to local JSON database file
            existing_leads = []
            if os.path.exists(LEADS_FILE):
                try:
                    with open(LEADS_FILE, "r") as f: existing_leads = json.load(f)
                except: pass
            existing_leads.append(lead_entry)
            with open(LEADS_FILE, "w") as f: json.dump(existing_leads, f, indent=4)

    # Compile dynamic engine payload
    with chat_container.chat_message("assistant"):
        with st.spinner("Processing inquiry..."):
            content_payload = []
            
            # Inject Company Knowledge Base Context directly into AI's active memory layer
            if st.session_state.company_context:
                content_payload.append(f"CRITICAL SYSTEM DIRECTIVE:\nYou are an automated official representative. Answer ONLY based on this company data:\n{st.session_state.company_context}\n\n")
            else:
                content_payload.append("You are a professional enterprise virtual assistant.\n")
                
            if attached_file:
                file_extension = attached_file.name.split(".")[-1].lower()
                if file_extension in ["png", "jpg", "jpeg"]:
                    content_payload.append(Image.open(attached_file))
                elif file_extension == "pdf":
                    pdf_reader = pypdf.PdfReader(attached_file)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        t = page.extract_text()
                        if t: pdf_text += t + "\n"
                    content_payload.append(f"[User uploaded file: {attached_file.name}]:\n{pdf_text}\n\n")
            
            content_payload.append(prompt_text if prompt_text else "Acknowledge file upload professionally.")
            
            try:
                response = chat_engine.generate_content(content_payload)
                ai_reply = response.text
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as chat_err:
                st.error(f"Response Error: {chat_err}")
                
    st.rerun()