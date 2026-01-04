"""Embedding generation module using FREE local sentence-transformers."""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from loguru import logger

from .utils import load_config


class EmbeddingGenerator:
    """Generate embeddings using FREE local sentence-transformers models."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize embedding generator with configuration."""
        self.config = load_config(config_path)
        embedding_config = self.config.get("embeddings", {})
        
        self.model_name = embedding_config.get("model", "sentence-transformers/all-MiniLM-L6-v2")
        self.batch_size = embedding_config.get("batch_size", 100)
        self.dimension = embedding_config.get("dimension", 384)
        
        # Load the local sentence-transformer model (FREE!)
        logger.info(f"Loading FREE local embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        logger.info(f"✅ Initialized FREE EmbeddingGenerator with model={self.model_name}, dimension={self.dimension}")
        logger.info("💰 Cost: $0.00 - Using local embeddings!")
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        try:
            embedding = self.model.encode(query, convert_to_numpy=True).tolist()
            logger.debug(f"Generated embedding for query: '{query[:50]}...'")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding for query: {e}")
            return []
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents in batches."""
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        
        logger.info(f"Embedding {len(texts)} documents in {total_batches} batches (FREE - no cost!)")
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            try:
                # Encode batch
                embeddings = self.model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
                all_embeddings.extend([emb.tolist() for emb in embeddings])
                logger.info(f"Batch {batch_num}/{total_batches} completed ({len(batch)} documents)")
            except Exception as e:
                logger.error(f"Error embedding batch {batch_num}: {e}")
                # Add zero embeddings for failed batch
                all_embeddings.extend([[0.0] * self.dimension] * len(batch))
        
        return all_embeddings
    
    def estimate_embedding_cost(self, texts: List[str]) -> float:
        """
        Estimate cost of embedding generation.
        
        Note: Always returns $0.00 for local sentence-transformers!
        """
        logger.info(f"💰 Estimated embedding cost: $0.00 for {len(texts)} documents (FREE local embeddings!)")
        return 0.0
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to document chunks."""
        texts = [chunk["content"] for chunk in chunks]
        
        # Cost is always $0 for local embeddings
        logger.info(f"💰 Cost for embedding {len(chunks)} chunks: $0.00 (FREE!)")
        
        # Generate embeddings
        embeddings = self.embed_documents(texts)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
        
        logger.info(f"✅ Successfully added FREE embeddings to {len(chunks)} chunks")
        return chunks


def demo():
    """Demo function to test embedding generation."""
    generator = EmbeddingGenerator()
    
    # Test single query
    query = "What were the revenue drivers in Q3?"
    query_embedding = generator.embed_query(query)
    print(f"\n✅ Query embedding dimension: {len(query_embedding)}")
    print(f"First 5 values: {query_embedding[:5]}")
    
    # Test batch embedding
    documents = [
        "Revenue increased by 15% year-over-year.",
        "Operating expenses decreased due to cost optimization.",
        "Net income reached $2.5 billion in Q3 2024."
    ]
    
    doc_embeddings = generator.embed_documents(documents)
    print(f"\n✅ Embedded {len(doc_embeddings)} documents")
    print(f"Embedding dimension: {len(doc_embeddings[0])}")
    print(f"💰 Total cost: $0.00 (FREE!)")


if __name__ == "__main__":
    demo()
