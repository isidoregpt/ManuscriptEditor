import streamlit as st
import openai
import anthropic
import os
from io import BytesIO
from docx import Document

# Set up Streamlit
st.set_page_config(page_title="AI Manuscript Editor", layout="wide")
st.title("✍️ AI Manuscript Editor")

# Instructions dropdown that remains persistent
with st.expander("📖 How to Use This App & Get API Keys", expanded=False):
    st.markdown("""
    ### 🚀 How to Use This App
    
    1. **Get API Keys** (see links below)
    2. **Enter your API keys** in the fields below
    3. **Select models** you want to use for feedback
    4. **Set an editor persona** (optional - defaults to Nan Graham)
    5. **Input your manuscript** by pasting text or uploading a .txt file
    6. **Write your feedback request** (e.g., "Is the dialogue realistic?", "Does the opening hook the reader?")
    7. **Click "Get Feedback"** to receive AI-powered editorial feedback
    8. **Download results** as a Word document for easy sharing and reference
    
    ### 🔑 Where to Get API Keys
    
    **OpenAI API Key** (for GPT models):
    - Sign up at: https://platform.openai.com/
    - Go to API Keys section and create a new key
    - Models available: GPT-4o, o3, GPT-4.1
    
    **Anthropic API Key** (for Claude models):
    - Sign up at: https://console.anthropic.com/
    - Create an API key in your account settings
    - Models available: Claude Sonnet 4
    
    ### 💡 Tips for Best Results
    
    - **Be specific** in your feedback requests (e.g., "Focus on character development in chapter 3")
    - **Provide context** about your genre, target audience, or specific concerns
    - **Use multiple models** to get diverse perspectives on your work
    - **Try different editor personas** to match your writing style or genre needs
    - **Submit manageable chunks** (1-3 pages work best for detailed feedback)
    
    ### 🎯 Example Feedback Requests
    
    - "Does this opening chapter effectively hook the reader?"
    - "Is the dialogue between these characters believable and distinct?"
    - "How is the pacing in this action sequence?"
    - "Are there any plot holes or inconsistencies in this scene?"
    - "Does this character's motivation feel authentic?"
    """)

# API key inputs
st.subheader("🔑 API Configuration")
col1, col2 = st.columns(2)

with col1:
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    st.session_state.openai_api_key = st.text_input(
        "🤖 Enter your OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password",
        help="Get your key at: https://platform.openai.com/"
    )

with col2:
    if "anthropic_api_key" not in st.session_state:
        st.session_state.anthropic_api_key = ""
    st.session_state.anthropic_api_key = st.text_input(
        "🧠 Enter your Anthropic API Key",
        value=st.session_state.anthropic_api_key,
        type="password",
        help="Get your key at: https://console.anthropic.com/"
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
    st.warning("⚠️ Please enter at least one API key to continue.")
    st.info("💡 Don't have API keys? Check the instructions above for sign-up links!")
    st.stop()

st.subheader("⚙️ Model Selection")
selected_models = st.multiselect(
    "🧠 Choose one or more models to use for feedback:",
    options=available_models,
    default=available_models,
    help="Select multiple models to get diverse editorial perspectives on your manuscript."
)

if not selected_models:
    st.warning("Please select at least one model.")
    st.stop()

# Editor configuration
st.subheader("👤 Editor Configuration")
editor_name = st.text_input(
    "Editor Persona", 
    value="Nan Graham",
    help="Name your editor persona (e.g., 'Nan Graham', 'Literary Editor', 'Genre Specialist')"
)

# Manuscript input
st.subheader("📄 Manuscript Input")
manuscript_input = st.text_area(
    "Paste a portion of your manuscript:", 
    height=300,
    help="Paste your text here. For best results, submit 1-3 pages at a time."
)

uploaded_file = st.file_uploader(
    "Or upload a .txt file", 
    type="txt",
    help="Upload a plain text file containing your manuscript excerpt."
)

if uploaded_file:
    manuscript_input = uploaded_file.read().decode("utf-8")
    st.success("✅ Manuscript text loaded from file!")

# Feedback prompt
st.subheader("🎯 Feedback Request")
editor_prompt = st.text_area(
    "What specific feedback would you like?", 
    placeholder="e.g., 'Is the pacing too fast in this chapter?', 'Does the dialogue sound natural?', 'How compelling is this opening?'",
    help="Be specific about what aspects you want feedback on for the most helpful results."
)

# Run feedback
st.subheader("🚀 Generate Feedback")
run_button = st.button("📝 Get Editorial Feedback", type="primary")

# Store results
all_feedback = {}

if run_button:
    if not manuscript_input or not editor_prompt:
        st.error("❌ Both manuscript text and feedback request are required.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, model in enumerate(selected_models):
            status_text.text(f"Getting feedback from {model}...")
            progress_bar.progress((i) / len(selected_models))
            
            try:
                if model in openai_models:
                    # Use OpenAI API
                    response = openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": f"You are a brilliant fiction editor named {editor_name}. Provide constructive, detailed feedback on the user's manuscript. Be specific, actionable, and encouraging while identifying areas for improvement."},
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
                        system=f"You are a brilliant fiction editor named {editor_name}. Provide constructive, detailed feedback on the user's manuscript. Be specific, actionable, and encouraging while identifying areas for improvement.",
                        messages=[
                            {"role": "user", "content": f"Manuscript:\n{manuscript_input}\n\nFeedback Request:\n{editor_prompt}"}
                        ]
                    )
                    all_feedback[model] = response.content[0].text.strip()
            
            except Exception as e:
                all_feedback[model] = f"❌ Error: {str(e)}"
        
        progress_bar.progress(1.0)
        status_text.text("✅ Feedback generation complete!")

# Show results
if all_feedback:
    st.subheader("📘 Editorial Feedback")
    
    for model, feedback in all_feedback.items():
        with st.expander(f"💡 Feedback from {model}", expanded=True):
            if feedback.startswith("❌ Error:"):
                st.error(feedback)
            else:
                st.write(feedback)
    
    # Generate DOCX file
    doc = Document()
    doc.add_heading('AI Manuscript Editor Feedback', 0)
    doc.add_paragraph(f'Editor Persona: {editor_name}')
    doc.add_paragraph(f'Feedback Request: {editor_prompt}')
    doc.add_paragraph('')
    doc.add_heading('Original Manuscript Excerpt', level=1)
    doc.add_paragraph(manuscript_input)
    doc.add_paragraph('')
    
    for model, feedback in all_feedback.items():
        if not feedback.startswith("❌ Error:"):
            doc.add_heading(f'Feedback from {model}', level=1)
            doc.add_paragraph(feedback)
            doc.add_paragraph('')
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.download_button(
            label="📥 Download as Word Doc",
            data=buffer,
            file_name="manuscript_feedback.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )
    with col2:
        st.success("✨ Feedback ready! Download the Word document to save your results.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Made with ❤️ for writers everywhere | Powered by OpenAI & Anthropic APIs</p>
    </div>
    """, 
    unsafe_allow_html=True
)
