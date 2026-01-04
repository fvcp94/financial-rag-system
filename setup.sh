#!/bin/bash

# Financial RAG System - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "=================================================="
echo "  Financial RAG System - Setup Script"
echo "  Setting up your production-ready RAG system..."
echo "=================================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "🐍 Creating virtual environment..."
python3 -m venv venv
echo "   ✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "⚡ Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ Pip upgraded"

# Install dependencies
echo ""
echo "📚 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt > /dev/null 2>&1
echo "   ✅ Dependencies installed"

# Create directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/chroma_db
mkdir -p logs
mkdir -p notebooks
echo "   ✅ Directories created"

# Setup environment file
echo ""
echo "🔑 Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✅ .env file created"
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   Example: OPENAI_API_KEY=sk-your-key-here"
else
    echo "   ℹ️  .env file already exists"
fi

# Check for OpenAI API key
echo ""
echo "🔍 Checking for OpenAI API key..."
if grep -q "sk-your-openai-api-key-here" .env 2>/dev/null; then
    echo "   ⚠️  WARNING: Default API key detected. Please update .env with your actual key."
elif grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "   ✅ API key found in .env"
else
    echo "   ⚠️  No API key found. Please add OPENAI_API_KEY to .env"
fi

# Create sample data info
echo ""
echo "📄 Setting up sample data directory..."
cat > data/raw/README.txt << 'EOF'
Financial RAG System - Data Directory
======================================

Place your financial PDF documents here for processing.

Naming Convention:
- Company_YYYY_QX.pdf (e.g., Apple_2024_Q3.pdf)
- Company_Annual_YYYY.pdf (e.g., Microsoft_Annual_2024.pdf)

Examples:
- Apple_2024_Q3.pdf
- Microsoft_2024_Q2.pdf  
- Google_2023_Annual.pdf

After adding PDFs, run:
    python scripts/process_documents.py

Or use the Python API:
    from src.data_ingestion import DocumentProcessor
    from src.vector_store import VectorStoreManager
    
    processor = DocumentProcessor()
    chunks = processor.process_directory('data/raw')
    
    vs = VectorStoreManager()
    vs.add_documents(chunks)
EOF
echo "   ✅ Sample data README created"

# Create helper scripts directory
echo ""
echo "🛠️  Creating helper scripts..."
mkdir -p scripts

cat > scripts/process_documents.py << 'EOF'
"""Process PDF documents and add to vector store."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_ingestion import DocumentProcessor
from src.vector_store import VectorStoreManager

def main():
    print("🔄 Processing documents...")
    
    # Process PDFs
    processor = DocumentProcessor()
    chunks = processor.process_directory('data/raw')
    
    if not chunks:
        print("❌ No documents found in data/raw/")
        print("   Please add PDF files following the naming convention:")
        print("   Company_YYYY_QX.pdf or Company_Annual_YYYY.pdf")
        return
    
    print(f"✅ Processed {len(chunks)} chunks")
    
    # Add to vector store
    print("💾 Adding to vector store...")
    vs = VectorStoreManager()
    vs.add_documents(chunks)
    
    print("✅ Documents successfully indexed!")
    print(f"   Total documents in store: {vs.get_collection_stats()['total_documents']}")

if __name__ == "__main__":
    main()
EOF
chmod +x scripts/process_documents.py
echo "   ✅ Helper scripts created"

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
# Quick run script for Financial RAG System

source venv/bin/activate

case "$1" in
    streamlit)
        echo "🚀 Starting Streamlit UI..."
        streamlit run src/streamlit_app.py
        ;;
    api)
        echo "🚀 Starting FastAPI server..."
        uvicorn src.api:app --reload --port 8000
        ;;
    test)
        echo "🧪 Running tests..."
        pytest tests/ -v
        ;;
    eval)
        echo "📊 Running evaluation..."
        python -m src.evaluation
        ;;
    docker)
        echo "🐳 Starting Docker containers..."
        docker-compose up
        ;;
    *)
        echo "Usage: ./run.sh [streamlit|api|test|eval|docker]"
        echo ""
        echo "Commands:"
        echo "  streamlit  - Run Streamlit UI (port 8501)"
        echo "  api        - Run FastAPI server (port 8000)"
        echo "  test       - Run test suite"
        echo "  eval       - Run evaluation"
        echo "  docker     - Start with Docker Compose"
        ;;
esac
EOF
chmod +x run.sh
echo "   ✅ Run script created"

# Summary
echo ""
echo "=================================================="
echo "  ✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Add your OpenAI API key to .env:"
echo "   nano .env"
echo ""
echo "2. Add PDF documents to data/raw/"
echo "   (Use naming: Company_YYYY_QX.pdf)"
echo ""
echo "3. Process documents:"
echo "   python scripts/process_documents.py"
echo ""
echo "4. Run the application:"
echo "   ./run.sh streamlit    # For UI"
echo "   ./run.sh api          # For API"
echo "   ./run.sh docker       # For both"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: QUICKSTART.md"
echo "   - Full README: README.md"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "=================================================="
echo "  Happy Analyzing! 📊"
echo "=================================================="
