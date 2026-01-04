# Financial RAG System - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/financial-rag-system.git
cd financial-rag-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Add Financial Documents

Place your PDF earnings reports in the `data/raw/` directory:

```
data/raw/
├── Apple_2024_Q3.pdf
├── Microsoft_2024_Q2.pdf
└── Google_2024_Annual.pdf
```

**Naming Convention**: `Company_YYYY_QX.pdf` or `Company_Annual_YYYY.pdf`

### Step 4: Process Documents

```bash
python -c "
from src.data_ingestion import DocumentProcessor
from src.vector_store import VectorStoreManager

# Process PDFs
processor = DocumentProcessor()
chunks = processor.process_directory('data/raw')

# Add to vector store
vs = VectorStoreManager()
vs.add_documents(chunks)

print(f'Successfully indexed {len(chunks)} document chunks!')
"
```

### Step 5: Run the Application

**Option A: Streamlit UI (Recommended for demo)**

```bash
streamlit run src/streamlit_app.py
```

Visit: `http://localhost:8501`

**Option B: FastAPI Backend**

```bash
uvicorn src.api:app --reload --port 8000
```

API Docs: `http://localhost:8000/docs`

**Option C: Both with Docker**

```bash
docker-compose up
```

- Streamlit: `http://localhost:8501`
- API: `http://localhost:8000`

## 📝 Sample Queries to Try

1. "What were the total revenues in Q3 2024?"
2. "How did operating expenses change year-over-year?"
3. "What are the key risk factors mentioned?"
4. "Summarize the main revenue drivers"
5. "What are the company's future growth plans?"

## 🧪 Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Evaluate System

```bash
python -m src.evaluation
```

This will:
- Run test queries
- Calculate metrics (relevance, precision, faithfulness)
- Generate evaluation report
- Save results to `evaluation_results.json`

## 🔧 Troubleshooting

### Issue: "No module named 'src'"

**Solution**: Make sure you're in the project root directory and have activated the virtual environment.

### Issue: "OpenAI API key not found"

**Solution**: 
1. Ensure `.env` file exists in project root
2. Verify `OPENAI_API_KEY` is set correctly
3. Don't include quotes around the key

### Issue: "No documents found in vector store"

**Solution**: 
1. Check if PDFs are in `data/raw/`
2. Run the document processing script (Step 4)
3. Verify ChromaDB directory exists: `data/chroma_db/`

### Issue: "ChromaDB collection error"

**Solution**: Reset the collection:

```bash
python -c "
from src.vector_store import VectorStoreManager
vs = VectorStoreManager()
vs.reset_collection()
"
```

Then re-run document processing.

## 📈 Next Steps

1. **Add More Documents**: Place more earnings PDFs in `data/raw/`
2. **Customize Configuration**: Edit `config/config.yaml`
3. **Experiment with Models**: Try different LLM models in config
4. **Deploy to Cloud**: Use provided Dockerfile
5. **Build Features**: Add custom filters or analytics

## 🌐 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `OPENAI_API_KEY` in Secrets
5. Deploy!

### Deploy to AWS/GCP

```bash
# Build Docker image
docker build -t financial-rag-system .

# Tag for registry
docker tag financial-rag-system:latest your-registry/financial-rag-system:latest

# Push to registry
docker push your-registry/financial-rag-system:latest

# Deploy to your cloud platform
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **Full README**: [README.md](README.md)
- **Configuration Guide**: See `config/config.yaml`

## 💡 Tips for Best Results

1. **Use Specific Queries**: "Q3 2024 revenue growth" > "tell me about revenue"
2. **Apply Filters**: Use company/year/quarter filters for precise results
3. **Check Sources**: Always verify answers against source documents
4. **Monitor Costs**: Track spending in Analytics tab
5. **Experiment with top_k**: Try different retrieval amounts (1-10)

## 🎯 Key Features to Showcase

When demoing to recruiters/hiring managers:

1. **Real-time Analytics**: Show cost tracking and latency metrics
2. **Source Citations**: Demonstrate answer provenance
3. **Filtering System**: Show company/year/quarter filtering
4. **Evaluation Framework**: Run evaluation to show quality metrics
5. **Production Ready**: Point to Docker, tests, API docs

## 🤝 Need Help?

- Check the [README](README.md) for detailed documentation
- Review code comments in source files
- Run tests to verify functionality
- Open an issue on GitHub

---

**Built by Febin Varghese** | [LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/yourusername)
