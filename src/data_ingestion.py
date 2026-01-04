"""Document ingestion and processing module."""

import re
from typing import List, Dict, Any
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from loguru import logger

from .utils import load_config, ensure_dir


class DocumentProcessor:
    """Process and chunk PDF documents for RAG system."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize document processor with configuration."""
        self.config = load_config(config_path)
        chunking_config = self.config.get("chunking", {})
        
        self.chunk_size = chunking_config.get("chunk_size", 1000)
        self.chunk_overlap = chunking_config.get("chunk_overlap", 200)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=chunking_config.get("separators", ["\n\n", "\n", ".", " "]),
            length_function=len
        )
        
        logger.info(f"Initialized DocumentProcessor with chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def load_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Load and parse PDF file."""
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {pdf_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {e}")
            return []
    
    def extract_metadata(self, pdf_path: str, content: str) -> Dict[str, Any]:
        """Extract metadata from PDF filename and content."""
        filename = Path(pdf_path).stem
        
        # Try to extract company, year, quarter from filename
        # Expected format: Company_YYYY_QX.pdf or Company_Annual_YYYY.pdf
        metadata = {
            "source": filename,
            "company": "Unknown",
            "year": None,
            "quarter": None,
            "doc_type": "earnings_report"
        }
        
        # Extract company name (first part before underscore)
        parts = filename.split("_")
        if parts:
            metadata["company"] = parts[0].replace("-", " ").title()
        
        # Extract year
        year_match = re.search(r'(20\d{2})', filename)
        if year_match:
            metadata["year"] = int(year_match.group(1))
        
        # Extract quarter
        quarter_match = re.search(r'Q([1-4])', filename, re.IGNORECASE)
        if quarter_match:
            metadata["quarter"] = f"Q{quarter_match.group(1)}"
        elif "annual" in filename.lower():
            metadata["quarter"] = "Annual"
        
        return metadata
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'Page \d+ of \d+', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-$%@#]', '', text)
        
        return text.strip()
    
    def chunk_document(self, documents: List[Any]) -> List[Dict[str, Any]]:
        """Split documents into chunks with metadata."""
        chunks = []
        
        for doc in documents:
            # Clean text
            clean_content = self.clean_text(doc.page_content)
            
            # Split into chunks
            text_chunks = self.text_splitter.split_text(clean_content)
            
            # Add metadata to each chunk
            for chunk_text in text_chunks:
                chunk = {
                    "content": chunk_text,
                    "metadata": {
                        **doc.metadata,
                        "chunk_size": len(chunk_text)
                    }
                }
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Process all PDFs in a directory."""
        directory = Path(directory_path)
        pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        all_chunks = []
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}...")
            
            # Load PDF
            documents = self.load_pdf(str(pdf_file))
            if not documents:
                continue
            
            # Extract metadata
            base_metadata = self.extract_metadata(str(pdf_file), documents[0].page_content)
            
            # Add metadata to all pages
            for doc in documents:
                doc.metadata.update(base_metadata)
            
            # Chunk documents
            chunks = self.chunk_document(documents)
            all_chunks.extend(chunks)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def process_single_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process a single PDF file."""
        logger.info(f"Processing {pdf_path}...")
        
        # Load PDF
        documents = self.load_pdf(pdf_path)
        if not documents:
            return []
        
        # Extract metadata
        base_metadata = self.extract_metadata(pdf_path, documents[0].page_content)
        
        # Add metadata to all pages
        for doc in documents:
            doc.metadata.update(base_metadata)
        
        # Chunk documents
        chunks = self.chunk_document(documents)
        
        return chunks


def demo():
    """Demo function to test document processing."""
    processor = DocumentProcessor()
    
    # Example: Process a directory
    chunks = processor.process_directory("data/raw")
    
    if chunks:
        print(f"\nProcessed {len(chunks)} chunks")
        print(f"\nSample chunk:")
        print(f"Content: {chunks[0]['content'][:200]}...")
        print(f"Metadata: {chunks[0]['metadata']}")


if __name__ == "__main__":
    demo()
