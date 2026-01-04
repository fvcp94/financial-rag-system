# Financial RAG System - Project Structure

## 📁 Complete Directory Structure

```
financial-rag-system/
│
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 LICENSE                      # MIT License
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 Dockerfile                   # Docker container config
├── 📄 docker-compose.yml           # Multi-container setup
├── 🔧 setup.sh                     # Automated setup script
├── 🔧 run.sh                       # Quick run commands
│
├── 📂 src/                         # Source code
│   ├── __init__.py                 # Package initialization
│   ├── utils.py                    # Helper functions & utilities
│   ├── data_ingestion.py           # PDF processing & chunking
│   ├── embeddings.py               # Embedding generation
│   ├── vector_store.py             # ChromaDB management
│   ├── rag_pipeline.py             # Core RAG logic
│   ├── evaluation.py               # Metrics & evaluation
│   ├── api.py                      # FastAPI REST endpoints
│   └── streamlit_app.py            # Streamlit UI dashboard
│
├── 📂 config/                      # Configuration files
│   └── config.yaml                 # System configuration
│
├── 📂 data/                        # Data storage
│   ├── raw/                        # Original PDF files
│   │   └── README.txt              # Data directory guide
│   ├── processed/                  # Processed chunks
│   └── chroma_db/                  # Vector database
│
├── 📂 tests/                       # Test suite
│   ├── __init__.py
│   ├── test_pipeline.py            # Pipeline tests
│   └── test_api.py                 # API endpoint tests
│
├── 📂 scripts/                     # Helper scripts
│   └── process_documents.py        # Document processing script
│
├── 📂 notebooks/                   # Jupyter notebooks
│   └── evaluation.ipynb            # Analysis notebook
│
└── 📂 logs/                        # Application logs
    └── (auto-generated log files)
```

## 📋 File Descriptions

### Core Application Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `src/rag_pipeline.py` | Main RAG system | Query processing, LLM integration, cost tracking |
| `src/vector_store.py` | Vector database | ChromaDB management, similarity search |
| `src/data_ingestion.py` | Document processing | PDF parsing, chunking, metadata extraction |
| `src/embeddings.py` | Embedding generation | OpenAI embeddings, batch processing |
| `src/evaluation.py` | System evaluation | Metrics calculation, testing framework |

### User Interfaces

| File | Purpose | Access |
|------|---------|--------|
| `src/streamlit_app.py` | Web dashboard | http://localhost:8501 |
| `src/api.py` | REST API | http://localhost:8000/docs |

### Configuration

| File | Purpose |
|------|---------|
| `config/config.yaml` | System settings (models, parameters) |
| `.env` | Environment variables (API keys) |
| `requirements.txt` | Python dependencies |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete project documentation |
| `QUICKSTART.md` | 5-minute setup guide |
| `PROJECT_STRUCTURE.md` | This file - project organization |

### Deployment

| File | Purpose |
|------|---------|
| `Dockerfile` | Container definition |
| `docker-compose.yml` | Multi-service orchestration |
| `setup.sh` | Automated setup script |
| `run.sh` | Quick launch commands |

## 🔧 Key Components Breakdown

### 1. RAG Pipeline (`src/rag_pipeline.py`)

**What it does:**
- Processes user queries
- Retrieves relevant documents from vector store
- Generates answers using LLM
- Tracks costs and performance metrics

**Key Classes:**
- `RAGPipeline`: Main pipeline orchestrator

**Methods:**
- `query()`: Execute RAG query
- `get_cost_summary()`: Get cost tracking data

### 2. Vector Store (`src/vector_store.py`)

**What it does:**
- Manages ChromaDB vector database
- Stores document embeddings
- Performs similarity search
- Handles filtering and retrieval

**Key Classes:**
- `VectorStoreManager`: Database management

**Methods:**
- `add_documents()`: Index new documents
- `query()`: Search for similar documents
- `get_collection_stats()`: Get database stats

### 3. Data Ingestion (`src/data_ingestion.py`)

**What it does:**
- Loads PDF files
- Extracts text and metadata
- Chunks documents intelligently
- Prepares data for embedding

**Key Classes:**
- `DocumentProcessor`: PDF processing pipeline

**Methods:**
- `load_pdf()`: Read PDF files
- `chunk_document()`: Split into chunks
- `process_directory()`: Batch processing

### 4. Embeddings (`src/embeddings.py`)

**What it does:**
- Generates vector embeddings
- Batch processing for efficiency
- Cost estimation
- Manages OpenAI API calls

**Key Classes:**
- `EmbeddingGenerator`: Embedding creation

**Methods:**
- `embed_query()`: Single text embedding
- `embed_documents()`: Batch embedding
- `estimate_embedding_cost()`: Cost calculation

### 5. Evaluation (`src/evaluation.py`)

**What it does:**
- Automated testing suite
- Metrics calculation
- Performance benchmarking
- Quality assessment

**Key Classes:**
- `RAGEvaluator`: System evaluation

**Metrics:**
- Answer Relevance (0.0-1.0)
- Context Precision (0.0-1.0)
- Faithfulness Score (0.0-1.0)
- Latency & Cost

## 🎯 Data Flow

```
1. User Query
   ↓
2. Query Embedding (embeddings.py)
   ↓
3. Vector Search (vector_store.py)
   ↓
4. Document Retrieval
   ↓
5. Context Formation
   ↓
6. LLM Generation (rag_pipeline.py)
   ↓
7. Answer + Sources + Metrics
```

## 📊 Configuration Options

### `config/config.yaml`

```yaml
embeddings:
  model: "text-embedding-3-small"  # Embedding model
  dimension: 1536                  # Vector dimension
  batch_size: 100                  # Batch processing size

llm:
  model: "gpt-4-turbo-preview"     # LLM model
  temperature: 0.1                 # Randomness (0-1)
  max_tokens: 1000                 # Max response length

retrieval:
  top_k: 4                         # Documents to retrieve
  similarity_threshold: 0.7        # Minimum similarity

chunking:
  chunk_size: 1000                 # Characters per chunk
  chunk_overlap: 200               # Overlap between chunks

cost_limits:
  daily_max: 10.0                  # Max daily cost (USD)
  per_query_max: 0.10              # Max per query
```

## 🚀 Quick Commands

### Setup
```bash
./setup.sh                    # Automated setup
```

### Run Applications
```bash
./run.sh streamlit            # Web UI
./run.sh api                  # REST API
./run.sh docker               # Both with Docker
```

### Development
```bash
./run.sh test                 # Run tests
./run.sh eval                 # Run evaluation
```

### Process Documents
```bash
python scripts/process_documents.py
```

## 📈 Extending the System

### Add a New LLM Provider

1. Install provider SDK in `requirements.txt`
2. Add configuration in `config/config.yaml`
3. Modify `src/rag_pipeline.py` to support new provider
4. Update tests

### Add New Evaluation Metrics

1. Add metric function in `src/evaluation.py`
2. Update `RAGEvaluator` class
3. Add to config `evaluation.metrics`
4. Run evaluation

### Add New API Endpoints

1. Define endpoint in `src/api.py`
2. Add request/response models
3. Update API documentation
4. Add tests in `tests/test_api.py`

## 🔐 Security Notes

### Sensitive Files (Never Commit)
- `.env` - Contains API keys
- `data/chroma_db/` - Vector database
- `logs/` - May contain query data
- `*.pdf` in `data/raw/` - Source documents

### Protected by `.gitignore`
All sensitive files are already excluded from Git.

## 📦 Production Deployment

### Docker Production
```bash
docker build -t financial-rag:prod .
docker run -p 8501:8501 -e OPENAI_API_KEY=$KEY financial-rag:prod
```

### Cloud Deployment
- **Streamlit Cloud**: Push to GitHub, connect at share.streamlit.io
- **AWS ECS**: Use Dockerfile with ECS task definition
- **Google Cloud Run**: Deploy container with `gcloud run deploy`
- **Azure Container Apps**: Deploy with Azure CLI

## 🤝 Contributing

When adding features:
1. Follow existing code structure
2. Add tests in `tests/`
3. Update relevant documentation
4. Ensure all tests pass
5. Add to CHANGELOG

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

**Built by Febin Varghese**
Data Scientist | ML Engineer | RAG Systems Expert
