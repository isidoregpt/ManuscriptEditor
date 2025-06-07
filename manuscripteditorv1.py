import streamlit as st
import os
import openai

# Streamlit UI setup
st.set_page_config(page_title="AI Manuscript Editor", layout="wide")
st.title("✍️ AI Manuscript Editor")

# Store API key securely in session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# API Key input
st.session_state.api_key = st.text_input(
    "🔑 Enter your OpenAI API Key",
    value=st.session_state.api_key,
    type="password",
    help="Your key is only used during this session and not saved."
)

# Exit early if no key
if not st.session_state.api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

# Configure OpenAI client using new API format
client = openai.OpenAI(api_key=st.session_state.api_key)

# Model selection
model = st.selectbox(
    "Choose your editor model:",
    options=["gpt-4o", "o3", "gpt-4.1"]
)

# Editor persona
editor_name = st.text_input("Editor Persona (e.g., Nan Graham)", value="Nan Graham")

# Input area
manuscript_input = st.text_area("📄 Paste a portion of your manuscript:", height=300)

# File upload option
uploaded_file = st.file_uploader("Or upload a .txt file", type="txt")
if uploaded_file:
    manuscript_input = uploaded_file.read().decode("utf-8")
    st.success("Manuscript text loaded.")

# Prompt
editor_prompt = st.text_area("🧠 What should your editor focus on?", placeholder="e.g., Is the pacing tight? Are the stakes clear?")

# Submit button
if st.button("📝 Get Editor Feedback"):
    if not manuscript_input or not editor_prompt:
        st.warning("Please enter both manuscript content and an editorial prompt.")
    else:
        with st.spinner(f"Asking {editor_name} via {model}..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a brilliant fiction editor named {editor_name}. Give constructive and literary feedback to help improve the manuscript."
                        },
                        {
                            "role": "user",
                            "content": f"Manuscript:\n{manuscript_input}\n\nFeedback Request:\n{editor_prompt}"
                        }
                    ],
                    temperature=0.7
                )
                output = response.choices[0].message.content.strip()
                st.subheader(f"📘 Feedback from {editor_name} ({model})")
                st.write(output)
            except Exception as e:
                st.error(f"❌ OpenAI Error: {e}")
