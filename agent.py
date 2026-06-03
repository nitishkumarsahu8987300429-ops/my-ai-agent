import os
import streamlit as str  # Sundar UI banane ke liye
from google import genai
from google.genai import types

# API Key configuration
os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6LDNpB3T-uM5appm_McL5Zino9mC7529pCRMM1i3Ujoqw"

# Initialize Gemini Client
@str.cache_resource
def get_ai_client():
    return genai.Client()

client = get_ai_client()

# Website ka Title aur Theme setup
str.set_page_config(page_title="Premium AI Business Agent", page_icon="🤖", layout="centered")
str.title("🤖 Premium Global AI Business Agent")
str.markdown("---")

# Chat history ko website ki memory mein save rakhne ke liye
if "chat_session" not in str.session_state:
    str.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a premium, high-end global AI Business Agent. "
                "Rule: Always detect the user's language and respond in the EXACT same language and tone. "
                "Agar user Hinglish (Hindi+English) mein baat kare, toh Hinglish mein jawab dein. "
                "If the user speaks in English, reply in professional English. "
                "Use Google Search tool whenever current or live data is needed."
            ),
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )

if "messages" not in str.session_state:
    str.session_state.messages = []

# Purani baaton ko screen par dikhane ke liye
for msg in str.session_state.messages:
    with str.chat_message(msg["role"]):
        str.markdown(msg["text"])

# User ke likhne ke liye chat box
if user_query := str.chat_input("Ask your premium AI Agent anything..."):
    # User ka message screen par dikhao
    with str.chat_message("user"):
        str.markdown(user_query)
    str.session_state.messages.append({"role": "user", "text": user_query})

    # AI se jawab mangna (Google Search grounding ke sath)
    with str.chat_message("assistant"):
        with str.spinner("AI is thinking & searching Google..."):
            response = str.session_state.chat_session.send_message(user_query)
            str.markdown(response.text)
            
    str.session_state.messages.append({"role": "assistant", "text": response.text})