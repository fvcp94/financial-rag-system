"""Vector store management using ChromaDB."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from loguru import logger

from .utils import load_config, ensure_dir
from .embeddings import EmbeddingGenerator


class VectorStoreManager:
    """Manage vector storage and retrieval using ChromaDB."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize vector store with configuration."""
        self.config = load_config(config_path)
        vs_config = self.config.get("vector_store", {})
        
        self.collection_name = vs_config.get("collection_name", "financial_docs")
        self.persist_directory = vs_config.get("persist_directory", "./data/chroma_db")
        self.distance_metric = vs_config.get("distance_metric", "cosine")
        
        # Ensure persist directory exists
        ensure_dir(self.persist_directory)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding generator (FREE local embeddings!)
        self.embedding_generator = EmbeddingGenerator(config_path)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": self.distance_metric}
        )
        
        logger.info(f"Initialized VectorStore with collection={self.collection_name}, "
                   f"metric={self.distance_metric}, count={self.collection.count()}")
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Add document chunks to vector store."""
        if not chunks:
            logger.warning("No chunks to add to vector store")
            return
        
        # Generate embeddings if not present
        if "embedding" not in chunks[0]:
            logger.info("Generating embeddings for chunks...")
            chunks = self.embedding_generator.embed_chunks(chunks)
        
        # Prepare data for ChromaDB
        ids = [f"doc_{i}" for i in range(len(chunks))]
        embeddings = [chunk["embedding"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        try:
            # Add to collection in batches
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                end_idx = min(i + batch_size, len(chunks))
                
                self.collection.add(
                    ids=ids[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx]
                )
                
                logger.info(f"Added batch {i // batch_size + 1}: {end_idx - i} documents")
            
            logger.info(f"Successfully added {len(chunks)} documents to vector store")
            logger.info(f"Total documents in collection: {self.collection.count()}")
        
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def query(
        self,
        query_text: str,
        top_k: int = 4,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query vector store for similar documents."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.embed_query(query_text)
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Prepare where clause for filtering
            where_clause = None
            if filters:
                where_clause = {}
                for key, value in filters.items():
                    where_clause[key] = value
            
            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            if results and results["documents"] and results["documents"][0]:
                for idx in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][idx],
                        "metadata": results["metadatas"][0][idx],
                        "distance": results["distances"][0][idx] if "distances" in results else None
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} documents for query: '{query_text[:50]}...'")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection."""
        count = self.collection.count()
        
        # Get sample to check metadata fields
        sample = self.collection.peek(limit=1)
        
        stats = {
            "collection_name": self.collection_name,
            "total_documents": count,
            "distance_metric": self.distance_metric,
            "persist_directory": self.persist_directory
        }
        
        if sample and sample["metadatas"]:
            stats["metadata_fields"] = list(sample["metadatas"][0].keys())
        
        return stats
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.warning(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
    
    def reset_collection(self) -> None:
        """Reset collection (delete and recreate)."""
        self.delete_collection()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": self.distance_metric}
        )
        logger.info(f"Reset collection: {self.collection_name}")


def demo():
    """Demo function to test vector store."""
    vs_manager = VectorStoreManager()
    
    # Sample chunks
    sample_chunks = [
        {
            "content": "Revenue increased 15% year-over-year to $95.3 billion.",
            "metadata": {"company": "Apple", "year": 2024, "quarter": "Q3", "page": 1}
        },
        {
            "content": "Operating expenses were reduced by 8% through cost optimization initiatives.",
            "metadata": {"company": "Apple", "year": 2024, "quarter": "Q3", "page": 2}
        },
        {
            "content": "Net income reached $25.5 billion, exceeding analyst expectations.",
            "metadata": {"company": "Apple", "year": 2024, "quarter": "Q3", "page": 3}
        }
    ]
    
    # Add documents
    print("\nAdding documents to vector store...")
    vs_manager.add_documents(sample_chunks)
    
    # Get stats
    print("\nCollection stats:")
    stats = vs_manager.get_collection_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Query
    print("\nQuerying vector store...")
    query = "What was the revenue performance?"
    results = vs_manager.query(query, top_k=2)
    
    print(f"\nResults for query: '{query}'")
    for idx, result in enumerate(results, 1):
        print(f"\n{idx}. {result['content']}")
        print(f"   Metadata: {result['metadata']}")
        print(f"   Distance: {result['distance']:.4f}")


if __name__ == "__main__":
    demo()
