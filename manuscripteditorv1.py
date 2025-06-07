import streamlit as st
import openai
import anthropic
import os
from io import BytesIO
from docx import Document

# Set up Streamlit
st.set_page_config(page_title="AI Manuscript Editor", layout="wide")
st.title("✍️ AI Manuscript Editor")

# API key inputs
col1, col2 = st.columns(2)

with col1:
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    st.session_state.openai_api_key = st.text_input(
        "🔑 Enter your OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password"
    )

with col2:
    if "anthropic_api_key" not in st.session_state:
        st.session_state.anthropic_api_key = ""
    st.session_state.anthropic_api_key = st.text_input(
        "🔑 Enter your Anthropic API Key",
        value=st.session_state.anthropic_api_key,
        type="password"
    )

# Set up API clients
openai_client = None
anthropic_client = None

if st.session_state.openai_api_key:
    openai_client = openai.OpenAI(api_key=st.session_state.openai_api_key)

if st.session_state.anthropic_api_key:
    anthropic_client = anthropic.Anthropic(api_key=st.session_state.anthropic_api_key)

# Choose models
openai_models = ["gpt-4o", "o3", "gpt-4.1"]
anthropic_models = ["claude-sonnet-4-20250514"]

available_models = []
if openai_client:
    available_models.extend(openai_models)
if anthropic_client:
    available_models.extend(anthropic_models)

if not available_models:
    st.warning("Please enter at least one API key.")
    st.stop()

selected_models = st.multiselect(
    "🧠 Choose one or more models to use:",
    options=available_models,
    default=available_models
)

if not selected_models:
    st.warning("Please select at least one model.")
    st.stop()

# Editor name
editor_name = st.text_input("Editor Persona (e.g., Nan Graham)", value="Nan Graham")

# Manuscript
manuscript_input = st.text_area("📄 Paste a portion of your manuscript:", height=300)
uploaded_file = st.file_uploader("Or upload a .txt file", type="txt")

if uploaded_file:
    manuscript_input = uploaded_file.read().decode("utf-8")
    st.success("Manuscript text loaded.")

# Prompt
editor_prompt = st.text_area("🧠 Editor Prompt", placeholder="e.g., Is the pacing too fast?")

# Run feedback
run_button = st.button("📝 Get Feedback")

# Store results
all_feedback = {}

if run_button:
    if not manuscript_input or not editor_prompt:
        st.warning("Manuscript and prompt are required.")
    else:
        for model in selected_models:
            with st.spinner(f"Running {model}..."):
                try:
                    if model in openai_models:
                        # Use OpenAI API
                        response = openai_client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content": f"You are a brilliant fiction editor named {editor_name}. Provide constructive feedback on the user's manuscript."},
                                {"role": "user", "content": f"Manuscript:\n{manuscript_input}\n\nFeedback Request:\n{editor_prompt}"}
                            ],
                            temperature=0.7
                        )
                        all_feedback[model] = response.choices[0].message.content.strip()
                    
                    elif model in anthropic_models:
                        # Use Anthropic API
                        response = anthropic_client.messages.create(
                            model=model,
                            max_tokens=4096,
                            temperature=0.7,
                            system=f"You are a brilliant fiction editor named {editor_name}. Provide constructive feedback on the user's manuscript.",
                            messages=[
                                {"role": "user", "content": f"Manuscript:\n{manuscript_input}\n\nFeedback Request:\n{editor_prompt}"}
                            ]
                        )
                        all_feedback[model] = response.content[0].text.strip()
                
                except Exception as e:
                    all_feedback[model] = f"❌ Error: {e}"

# Show results
if all_feedback:
    st.subheader("📘 Editor Feedback")
    for model, feedback in all_feedback.items():
        st.markdown(f"### 💡 Feedback from `{model}`")
        st.write(feedback)
    
    # Generate DOCX file
    doc = Document()
    doc.add_heading('AI Manuscript Editor Feedback', 0)
    for model, feedback in all_feedback.items():
        doc.add_heading(f'Feedback from {model}', level=1)
        doc.add_paragraph(feedback)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    st.download_button(
        label="📥 Download All Feedback as DOCX",
        data=buffer,
        file_name="editor_feedback.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
