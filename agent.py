import streamlit as st
import google.generativeai as genai
import pypdf

# Page config and styling
st.set_page_config(page_title="Premium Global AI Business Agent", page_icon="🤖", layout="wide")

# Custom CSS for premium dark theme look
st.markdown("""
    <style>
    .main { background-color: #0f111a; }
    .stHeadingContainer h1 { color: #ffffff; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    div[data-testid="stSidebar"] { background-color: #161925; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Premium Global AI Business Agent")
st.subheader("Now with Google Search & PDF Intelligence")
st.write("---")

# Initialize Gemini Client
@st.cache_resource
def get_ai_model():
    # Correct structure to pass Google Search tool to Gemini model
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[{"google_search": {}}]
    )

try:
    model = get_ai_model()
except Exception as e:
    st.error(f"API Client Error: {e}")
    st.stop()

# Initialize session states for chat and PDF content
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# --- SIDEBAR: PDF UPLOAD & CONFIG ---
with st.sidebar:
    st.header("📁 Business Documents")
    uploaded_file = st.file_uploader("Upload Market Reports, Invoices, or PDFs", type=["pdf"])
    
    if uploaded_file is not None:
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            with st.spinner("Reading your document..."):
                try:
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
                    
                    st.session_state.pdf_context = extracted_text
                    st.session_state.last_uploaded_file = uploaded_file.name
                    st.success(f"Successfully loaded: {uploaded_file.name} ✅")
                except Exception as e:
                    st.error(f"Could not read PDF: {e}")
    else:
        st.session_state.pdf_context = ""
        if "last_uploaded_file" in st.session_state:
            del st.session_state.last_uploaded_file

    st.write("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN CHAT INTERFACE ---
# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_query := st.chat_input("Ask your premium AI Agent anything about business or your PDF..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Prepare complete prompt for AI
    full_prompt = ""
    if st.session_state.pdf_context:
        full_prompt += f"--- START OF UPLOADED DOCUMENT CONTEXT ---\n{st.session_state.pdf_context}\n--- END OF UPLOADED DOCUMENT CONTEXT ---\n\n"
        full_prompt += f"Instructions: Use the above document context to answer the user's question. If the answer is not in the document, use Google Search to find the answer.\n\n"
    
    full_prompt += f"User Question: {user_query}"

    # Generate response from Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing and searching..."):
            try:
                response = model.generate_content(full_prompt)
                ai_response = response.text
                message_placeholder.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                error_msg = f"Sorry, I ran into an error: {e}"
                message_placeholder.markdown(error_msg)