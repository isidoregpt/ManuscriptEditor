import streamlit as st
import openai

# Streamlit UI setup
st.set_page_config(page_title="AI Manuscript Editor", layout="wide")
st.title("✍️ AI Manuscript Editor")

# Store API key securely in session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# API Key input field (masked)
st.session_state.api_key = st.text_input(
    "🔑 Enter your OpenAI API Key",
    value=st.session_state.api_key,
    type="password",
    help="Your key is not saved or sent anywhere except to OpenAI."
)

# If no API key, stop early
if not st.session_state.api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

# Set OpenAI API key
openai.api_key = st.session_state.api_key

# Select OpenAI model
model = st.selectbox(
    "Choose your editor model:",
    options=["gpt-4o", "o3", "gpt-4.1"],
    help="Try different models for different feedback quality."
)

# Choose editor personality
editor_name = st.text_input("Editor Persona (e.g., Nan Graham)", value="Nan Graham")

# Input manuscript
manuscript_input = st.text_area("📄 Paste your manuscript segment here:", height=300)

# Upload .txt file (optional)
uploaded_file = st.file_uploader("Or upload a .txt file", type="txt")
if uploaded_file:
    manuscript_input = uploaded_file.read().decode("utf-8")
    st.success("Manuscript text loaded.")

# Editor instruction
editor_prompt = st.text_area(
    "🧠 What should your editor focus on?",
    placeholder="e.g., Is the pacing right? Are the characters believable?"
)

# Run editor
if st.button("📝 Get Editor Feedback"):
    if not manuscript_input or not editor_prompt:
        st.warning("Please enter both manuscript text and an editor prompt.")
    else:
        with st.spinner(f"Asking {editor_name} ({model}) to review..."):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": f"You are a seasoned fiction editor named {editor_name}. Offer kind, insightful, and constructive literary feedback."},
                        {"role": "user", "content": f"Manuscript:\n{manuscript_input}\n\nFeedback Request:\n{editor_prompt}"}
                    ],
                    temperature=0.7
                )
                output = response.choices[0].message.content.strip()
                st.subheader(f"📘 Feedback from {editor_name} ({model})")
                st.write(output)
            except Exception as e:
                st.error(f"❌ OpenAI Error: {e}")
