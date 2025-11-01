"""
Medical Document AI Assistant - Main Streamlit Application
"""
import streamlit as st
import os
from pathlib import Path
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import OrchestratorAgent
from agents.extraction_agent import ExtractionAgent
from agents.report_assembly_agent import ReportAssemblyAgent
import config

# Page configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    
    if 'extraction_agent' not in st.session_state:
        st.session_state.extraction_agent = None
    
    if 'report_agent' not in st.session_state:
        st.session_state.report_agent = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
    
    if 'api_key_configured' not in st.session_state:
        st.session_state.api_key_configured = False


def check_api_key():
    """Check if Google API key is configured"""
    api_key = os.getenv("GOOGLE_API_KEY", "")

    
    if not api_key:
        st.sidebar.error("⚠️ Google API Key not found!")
        st.sidebar.info("""
        Please set your Google API Key:
        1. Create a `.env` file in the project root
        2. Add: `GOOGLE_API_KEY=your_api_key_here`
        3. Get your free API key from: https://aistudio.google.com/app/apikey
        """)
        return False
    
    return True


def initialize_agents():
    """Initialize all agents"""
    try:
        if st.session_state.orchestrator is None:
            with st.spinner("Initializing AI agents..."):
                st.session_state.orchestrator = OrchestratorAgent()
                st.session_state.extraction_agent = ExtractionAgent()
                st.session_state.report_agent = ReportAssemblyAgent()
            st.success("✅ AI agents initialized successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error initializing agents: {e}")
        return False


def handle_file_upload(uploaded_files):
    """Handle document upload and processing"""
    if not uploaded_files:
        return
    
    # Save uploaded files
    saved_paths = []
    
    for uploaded_file in uploaded_files:
        # Create uploads directory if it doesn't exist
        os.makedirs(config.UPLOADS_DIR, exist_ok=True)
        
        # Save file
        file_path = os.path.join(config.UPLOADS_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        saved_paths.append(file_path)
        
        if uploaded_file.name not in st.session_state.uploaded_files:
            st.session_state.uploaded_files.append(uploaded_file.name)
    
    # Process documents
    with st.spinner("Processing documents... This may take a moment."):
        results = st.session_state.orchestrator.load_documents(saved_paths)
    
    # Display results
    if results['success']:
        st.success(f"✅ Successfully processed {len(results['success'])} documents!")
        st.session_state.documents_loaded = True
        
        # Show details
        with st.expander("📊 Processing Details"):
            st.write(f"**Total chunks created:** {results['total_chunks']}")
            for doc in results['processed_docs']:
                st.write(f"- {doc['filename']}: {doc['chunks']} chunks")
    
    if results['failed']:
        st.error(f"❌ Failed to process {len(results['failed'])} documents")
        for failed in results['failed']:
            st.write(f"- {failed['file']}: {failed['error']}")


def display_chat_interface():
    """Display chat interface"""
    st.subheader("💬 Chat with Your Documents")
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message['role']
        content = message['content']
        
        if role == 'user':
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)
                
                # Show sources if available
                if 'sources' in message and message['sources']:
                    with st.expander("📚 Sources"):
                        for source in message['sources']:
                            st.write(f"- {source['filename']}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        if not st.session_state.documents_loaded:
            st.warning("⚠️ Please upload documents first!")
            return
        
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response from orchestrator
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.orchestrator.process_request(
                    user_input=prompt,
                    chat_history=st.session_state.chat_history
                )
            
            # Display response
            st.write(response['content'])
            
            # Add to history
            assistant_message = {
                'role': 'assistant',
                'content': response['content']
            }
            
            if 'sources' in response:
                assistant_message['sources'] = response['sources']
                
                # Show sources
                with st.expander("📚 Sources"):
                    for source in response['sources']:
                        st.write(f"- {source['filename']}")
            
            st.session_state.chat_history.append(assistant_message)


def display_report_generation():
    """Display report generation interface"""
    st.subheader("📄 Generate Medical Report")
    
    if not st.session_state.documents_loaded:
        st.warning("⚠️ Please upload documents first!")
        return
    
    # Initialize report state if not exists
    if 'generated_report' not in st.session_state:
        st.session_state.generated_report = None
    
    with st.form("report_form"):
        st.write("### Report Configuration")
        
        report_title = st.text_input("Report Title", value="Medical Document Analysis Report")
        
        sections = st.multiselect(
            "Select Report Sections",
            ["Introduction", "Clinical Findings", "Patient Data", "Summary"],
            default=["Introduction", "Clinical Findings", "Summary"]
        )
        
        submitted = st.form_submit_button("🚀 Generate Report")
    
    # Handle form submission outside the form
    if submitted:
        with st.spinner("Generating report... This may take a minute."):
            try:
                # Generate report
                report_data = st.session_state.report_agent.generate_report(
                    title=report_title,
                    sections=sections
                )
                
                # Store report in session state
                if report_data['success']:
                    st.session_state.generated_report = report_data
                    st.success("✅ Report generated successfully!")
                else:
                    st.error(f"❌ Error generating report: {report_data.get('error', 'Unknown error')}")
                    st.session_state.generated_report = None
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.session_state.generated_report = None
    
    # Display download button if report exists (outside the form)
    if st.session_state.generated_report:
        st.write("---")
        st.write("### 📥 Download Your Report")
        
        try:
            with open(st.session_state.generated_report['pdf_path'], "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Report (PDF)",
                    data=pdf_file,
                    file_name=f"medical_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_report_btn"
                )
        except Exception as e:
            st.error(f"❌ Error loading report file: {e}")


def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🏥 Medical Document AI Assistant</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # API Key check
        if check_api_key():
            st.success("✅ API Key Configured")
            st.session_state.api_key_configured = True
        else:
            st.session_state.api_key_configured = False
            return
        
        # Initialize agents
        if not initialize_agents():
            return
        
        st.markdown("---")
        
        # File upload section
        st.subheader("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload medical documents",
            type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            help="Supported formats: PDF, Word, Excel, Images"
        )
        
        if uploaded_files:
            if st.button("🔄 Process Documents"):
                handle_file_upload(uploaded_files)
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.write("**Uploaded Files:**")
            for filename in st.session_state.uploaded_files:
                st.write(f"✓ {filename}")
        
        st.markdown("---")
        
        # Clear documents button
        if st.button("🗑️ Clear All Documents"):
            if st.session_state.orchestrator:
                st.session_state.orchestrator.clear_documents()
                st.session_state.uploaded_files = []
                st.session_state.chat_history = []
                st.session_state.documents_loaded = False
                st.success("✅ All documents cleared!")
                st.rerun()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Generate Report", "ℹ️ About"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_report_generation()
    
    with tab3:
        st.markdown("""
        ## About This Application
        
        This AI-powered medical document assistant helps healthcare organizations:
        
        - **📁 Process Multiple Formats**: Upload PDFs, Word documents, Excel files, and images
        - **💬 Conversational Q&A**: Ask questions and get answers from your documents
        - **📊 Extract Data**: Pull tables, charts, and clinical data
        - **📄 Generate Reports**: Create structured medical reports automatically
        
        ### Technology Stack
        
        - **Frontend**: Streamlit
        - **AI Model**: Google Gemini 2.0 Flash (Free Tier)
        - **Vector Database**: ChromaDB
        - **Embeddings**: Sentence Transformers (Local)
        - **Framework**: LangChain
        
        ### Features
        
        ✅ Multi-format document support
        ✅ RAG-powered Q&A
        ✅ Multi-turn conversations with memory
        ✅ Agentic workflow
        ✅ PDF report generation
        ✅ 100% Free models
        
        ---
        
        **Made with ❤️ using only free and open-source tools**
        """)


if __name__ == "__main__":
    main()
