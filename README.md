# 🏥 Medical Document AI Assistant

A comprehensive AI-powered assistant for managing and analyzing medical documents using **100% free tools and models**. This application enables healthcare organizations to upload multi-format medical documents, interact with them through natural conversation, and generate structured reports.

## ✨ Features

### Core Capabilities
- **📁 Multi-Format Document Support**: Process PDFs, Word documents, Excel files, and images
- **💬 Conversational Q&A**: Ask questions about your documents with multi-turn conversation memory
- **🔍 Retrieval-Augmented Generation (RAG)**: Accurate answers grounded in your documents
- **📊 Data Extraction**: Extract tables, charts, and clinical data automatically
- **📄 PDF Report Generation**: Create structured medical reports with custom sections
- **🤖 Agentic Workflow**: Multiple specialized AI agents working together

### Technical Highlights
- ✅ **100% Free Models**: Uses Google Gemini 2.0 Flash (free tier) and local embeddings
- ✅ **Open Source**: Built with open-source frameworks (LangChain, ChromaDB, Streamlit)
- ✅ **Scalable Architecture**: Modular agentic design
- ✅ **No Cloud Costs**: Local vector database with ChromaDB
- ✅ **Production Ready**: Includes Docker support and deployment guides

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│              (User Interface & File Upload)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────▼──────────────┐
         │  Orchestrator Agent      │
         │  (Central Controller)    │
         └───────────┬──────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
   ┌────▼────┐  ┌───▼────┐  ┌───▼─────┐   ┌───▼──────┐
   │Document │  │   Q&A  │  │Extract  │   │ Report   │
   │ Loader  │  │  Agent │  │ Agent   │   │ Assembly │
   │ Agent   │  │  (RAG) │  │         │   │  Agent   │
   └────┬────┘  └───┬────┘  └────┬────┘   └────┬─────┘
        │           │            │              │
        │      ┌────▼────────────▼──────┐       │
        │      │    Vector Store         │       │
        └─────▶│     (ChromaDB)          │◀──────┘
               └─────────────────────────┘
                     │
               ┌─────▼─────┐
               │  Gemini   │
               │ 2.0 Flash │
               └───────────┘
```

### Agent Responsibilities

1. **Orchestrator Agent**: Routes requests and coordinates agent collaboration
2. **Document Loader Agent**: Processes multi-format documents and creates vector embeddings
3. **Q&A Agent**: Handles conversational queries using RAG pipeline
4. **Extraction Agent**: Extracts specific data, tables, and images
5. **Report Assembly Agent**: Compiles and generates PDF reports
6. **Summarization Agent**: Creates concise summaries of document content

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google API Key (free from https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd medical-doc-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### 1. Upload Documents

- Click on the sidebar "Upload Documents" section
- Select one or multiple files (PDF, DOCX, XLSX, or images)
- Click "Process Documents" to load them into the system
- Wait for processing to complete

### 2. Chat with Documents

- Go to the "Chat" tab
- Ask questions about your uploaded documents
- The AI will retrieve relevant information and provide answers
- Continue the conversation - the system maintains context

Example questions:
- "What are the main clinical findings in these documents?"
- "Summarize the patient data from the uploaded files"
- "What treatment recommendations are mentioned?"

### 3. Generate Reports

- Go to the "Generate Report" tab
- Enter a report title
- Select which sections to include
- Click "Generate Report"
- Download the generated PDF

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t medical-doc-assistant .
```

### Run Container

```bash
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=your_api_key_here \
  medical-doc-assistant
```

Access at `http://localhost:8501`

---

## ☁️ Streamlit Cloud Deployment

### Option 1: Deploy via Streamlit Cloud UI

1. Push your code to GitHub
2. Go to https://share.streamlit.io/
3. Click "New app"
4. Select your repository
5. Add your `GOOGLE_API_KEY` in the Secrets section
6. Click "Deploy"

### Option 2: Deploy via CLI

```bash
# Install Streamlit CLI
pip install streamlit

# Login to Streamlit
streamlit login

# Deploy
streamlit deploy app.py
```

### Secrets Configuration

In Streamlit Cloud, add this to your app's secrets:

```toml
GOOGLE_API_KEY = "your_api_key_here"
```

---

## 🔧 Configuration

Edit `config.py` to customize:

- **Model Settings**: Change Gemini model version
- **Embedding Model**: Switch between Google or local embeddings
- **Chunk Size**: Adjust document chunking parameters
- **Rate Limits**: Configure API request delays
- **Vector Store**: Modify ChromaDB settings

---

## 📊 Tech Stack

| Component | Technology | License |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Apache 2.0 |
| **AI Model** | Google Gemini 2.0 Flash | Free Tier |
| **Embeddings** | Sentence Transformers | Apache 2.0 |
| **Vector DB** | ChromaDB | Apache 2.0 |
| **Framework** | LangChain | MIT |
| **PDF Processing** | PyMuPDF | AGPL |
| **PDF Generation** | ReportLab | BSD |
| **Document Processing** | python-docx, openpyxl | MIT |

---

## 🎯 Project Structure

```
medical-doc-assistant/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── README.md                # This file
├── agents/
│   ├── orchestrator.py      # Central controller
│   ├── document_loader.py   # Document ingestion
│   ├── qa_agent.py          # Q&A with RAG
│   ├── extraction_agent.py  # Data extraction
│   ├── report_assembly_agent.py  # Report generation
│   └── summarization_agent.py    # Summarization
└── utils/
    ├── document_processor.py # Multi-format processing
    ├── vector_store.py       # Vector database ops
    └── pdf_generator.py      # PDF report creation
```

---

## ⚠️ Important Notes

### Rate Limits (Gemini Free Tier)

- **15 requests per minute**
- **1 million tokens per minute**
- The app includes automatic rate limiting (4 seconds between requests)

### Token Management

- Input is chunked to stay under 30K tokens
- Responses limited to 8K tokens
- Conversation history is truncated after 5 turns

### Limitations

- Vector store is local (not shared across deployments)
- Session state is lost on browser refresh
- OCR requires Tesseract installation for image text extraction

---

## 🐛 Troubleshooting

### Issue: "API Key not found"
**Solution**: Ensure `.env` file exists with valid `GOOGLE_API_KEY`

### Issue: "Module not found"
**Solution**: Activate virtual environment and reinstall dependencies

### Issue: "ChromaDB initialization error"
**Solution**: Delete `data/vector_db` folder and restart

### Issue: "Rate limit exceeded"
**Solution**: Wait 60 seconds or increase `REQUEST_DELAY_SECONDS` in config

### Issue: "OCR not working"
**Solution**: Install Tesseract OCR
```bash
# Ubuntu
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- Google for providing free Gemini API access
- Streamlit for the amazing framework
- LangChain for RAG capabilities
- ChromaDB for vector storage
- All open-source contributors

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Made with ❤️ using 100% free and open-source tools**
