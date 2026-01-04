"""Tests for RAG pipeline functionality."""

import pytest
from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStoreManager
from src.data_ingestion import DocumentProcessor


class TestRAGPipeline:
    """Test suite for RAG pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create RAG pipeline instance."""
        return RAGPipeline()
    
    def test_pipeline_initialization(self, pipeline):
        """Test that pipeline initializes correctly."""
        assert pipeline is not None
        assert pipeline.llm is not None
        assert pipeline.vector_store is not None
    
    def test_query_basic(self, pipeline):
        """Test basic query functionality."""
        response = pipeline.query("What is the company revenue?")
        
        assert "answer" in response
        assert "sources" in response
        assert "metrics" in response
        assert isinstance(response["answer"], str)
    
    def test_query_with_filters(self, pipeline):
        """Test query with filters."""
        response = pipeline.query(
            "What were Q3 results?",
            filters={"company": "Apple", "year": 2024}
        )
        
        assert response["success"] is True
        assert isinstance(response["sources"], list)
    
    def test_cost_tracking(self, pipeline):
        """Test cost tracking functionality."""
        # Run a query
        pipeline.query("Test query")
        
        # Check cost summary
        summary = pipeline.get_cost_summary()
        
        assert "total_cost" in summary
        assert "query_count" in summary
        assert summary["query_count"] > 0


class TestVectorStore:
    """Test suite for vector store."""
    
    @pytest.fixture
    def vs_manager(self):
        """Create vector store manager instance."""
        return VectorStoreManager()
    
    def test_vs_initialization(self, vs_manager):
        """Test vector store initialization."""
        assert vs_manager is not None
        assert vs_manager.collection is not None
    
    def test_get_stats(self, vs_manager):
        """Test getting collection statistics."""
        stats = vs_manager.get_collection_stats()
        
        assert "collection_name" in stats
        assert "total_documents" in stats
        assert "distance_metric" in stats


class TestDocumentProcessor:
    """Test suite for document processing."""
    
    @pytest.fixture
    def processor(self):
        """Create document processor instance."""
        return DocumentProcessor()
    
    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert processor.text_splitter is not None
    
    def test_clean_text(self, processor):
        """Test text cleaning."""
        dirty_text = "This  has   extra    spaces"
        clean = processor.clean_text(dirty_text)
        
        assert "  " not in clean
        assert clean == "This has extra spaces"
    
    def test_extract_metadata(self, processor):
        """Test metadata extraction from filename."""
        filename = "Apple_2024_Q3.pdf"
        metadata = processor.extract_metadata(filename, "")
        
        assert metadata["company"] == "Apple"
        assert metadata["year"] == 2024
        assert metadata["quarter"] == "Q3"


# Integration Tests
class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_query(self):
        """Test complete query flow from input to output."""
        pipeline = RAGPipeline()
        
        query = "What were the revenue trends?"
        response = pipeline.query(query, top_k=3)
        
        # Verify response structure
        assert response["success"] is True
        assert len(response["answer"]) > 0
        assert len(response["sources"]) <= 3
        
        # Verify metrics
        assert response["metrics"]["latency"] > 0
        assert response["metrics"]["total_cost"] >= 0
        assert response["metrics"]["total_tokens"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
