"""Financial RAG System - Production-Ready RAG for Financial Analysis."""

__version__ = "1.0.0"
__author__ = "Febin Varghese"

from .rag_pipeline import RAGPipeline
from .data_ingestion import DocumentProcessor
from .vector_store import VectorStoreManager

__all__ = ["RAGPipeline", "DocumentProcessor", "VectorStoreManager"]
