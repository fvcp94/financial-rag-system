"""Core RAG pipeline for financial document analysis using FREE OpenRouter models."""

import time
from typing import Dict, Any, List, Optional
from openai import OpenAI
from loguru import logger

from .utils import load_config, get_api_key, count_tokens, estimate_cost, CostTracker
from .vector_store import VectorStoreManager


class RAGPipeline:
    """Main RAG pipeline for querying financial documents using FREE OpenRouter models."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize RAG pipeline with configuration."""
        self.config = load_config(config_path)
        
        # Initialize vector store
        self.vector_store = VectorStoreManager(config_path)
        
        # Initialize LLM with OpenRouter
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openrouter")
        
        if provider == "openrouter":
            api_key = get_api_key("openrouter")
            
            # OpenRouter uses OpenAI-compatible API
            self.llm = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            self.model_name = llm_config.get("model", "meta-llama/llama-3.2-3b-instruct:free")
            logger.info(f"✅ Using FREE OpenRouter model: {self.model_name}")
            logger.info("💰 Cost: $0.00 per query! ⚡ Fastest free model available!")
        else:
            # Fallback to OpenAI if specified
            from langchain_openai import ChatOpenAI
            api_key = get_api_key("openai")
            self.llm = ChatOpenAI(
                model=llm_config.get("model", "gpt-4-turbo-preview"),
                temperature=llm_config.get("temperature", 0.1),
                max_tokens=llm_config.get("max_tokens", 1000),
                openai_api_key=api_key
            )
            self.model_name = llm_config.get("model", "gpt-4-turbo-preview")
            logger.info(f"Using OpenAI model: {self.model_name}")
        
        self.temperature = llm_config.get("temperature", 0.1)
        self.max_tokens = llm_config.get("max_tokens", 1000)
        
        # Get retrieval config
        retrieval_config = self.config.get("retrieval", {})
        self.default_top_k = retrieval_config.get("top_k", 4)
        self.similarity_threshold = retrieval_config.get("similarity_threshold", 0.7)
        
        # Initialize cost tracker (FREE models have $0 limit)
        cost_limits = self.config.get("cost_limits", {})
        self.cost_tracker = CostTracker(daily_limit=0.0 if ":free" in self.model_name else cost_limits.get("daily_max", 10.0))
        
        # Define system prompt
        self.system_prompt = """You are a financial analyst assistant helping users understand earnings reports and financial documents.

Your task is to answer questions based ONLY on the provided context from financial documents.

Guidelines:
1. Provide accurate, concise answers based on the context
2. If the context doesn't contain enough information, say so
3. Include specific numbers, percentages, and metrics when available
4. Cite which document or quarter the information comes from
5. If comparing data, clearly state the time periods
6. Do not make assumptions or add information not in the context"""
        
        logger.info(f"Initialized RAGPipeline with model={self.model_name}, top_k={self.default_top_k}")
    
    def query(
        self,
        question: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: User's question
            filters: Optional filters (e.g., {"company": "Apple", "year": 2024})
            top_k: Number of documents to retrieve (default from config)
        
        Returns:
            Dictionary with answer, sources, and metrics
        """
        start_time = time.time()
        
        # Use default top_k if not specified
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Querying with: '{question[:100]}...'")
            retrieved_docs = self.vector_store.query(
                query_text=question,
                top_k=top_k,
                filters=filters
            )
            
            if not retrieved_docs:
                logger.warning("No documents retrieved from vector store")
                return {
                    "answer": "I couldn't find relevant information in the available documents to answer your question.",
                    "sources": [],
                    "metrics": {
                        "latency": time.time() - start_time,
                        "retrieved_docs": 0
                    }
                }
            
            # Filter by similarity threshold
            filtered_docs = [
                doc for doc in retrieved_docs
                if doc.get("distance", 1.0) <= (1.0 - self.similarity_threshold)
            ]
            
            if not filtered_docs:
                filtered_docs = retrieved_docs  # Use all if none meet threshold
            
            # Step 2: Format context
            context = self._format_context(filtered_docs)
            
            # Step 3: Generate answer using OpenRouter
            prompt = f"{self.system_prompt}\n\nContext:\n{context}\n\nQuestion: {question}\n\nProvide a clear, professional answer:"
            
            # Count tokens
            prompt_tokens = count_tokens(prompt, model="gpt-4")
            
            # Get LLM response from OpenRouter
            logger.info("Generating answer with FREE OpenRouter model...")
            response = self.llm.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            # Count completion tokens
            completion_tokens = count_tokens(answer, model="gpt-4")
            
            # Calculate cost (FREE for OpenRouter free models!)
            cost = estimate_cost(prompt_tokens, completion_tokens, model=self.model_name)
            
            # Track cost
            self.cost_tracker.add_cost(cost, question)
            
            # Calculate latency
            latency = time.time() - start_time
            
            # Format sources
            sources = self._format_sources(filtered_docs)
            
            # Compile metrics
            metrics = {
                "latency": round(latency, 3),
                "retrieved_docs": len(filtered_docs),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "total_cost": round(cost, 6),
                "model": self.model_name,
                "is_free": ":free" in self.model_name
            }
            
            logger.info(f"✅ Query completed in {latency:.2f}s, cost: ${cost:.4f} (FREE!)")
            
            return {
                "answer": answer,
                "sources": sources,
                "metrics": metrics,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "sources": [],
                "metrics": {
                    "latency": time.time() - start_time,
                    "error": str(e)
                },
                "success": False
            }
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string."""
        context_parts = []
        
        for idx, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")
            
            context_parts.append(
                f"[Document {idx}]\n"
                f"Source: {metadata.get('company', 'Unknown')} - "
                f"{metadata.get('quarter', 'N/A')} {metadata.get('year', 'N/A')}\n"
                f"Content: {content}\n"
            )
        
        return "\n\n".join(context_parts)
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source documents for output."""
        sources = []
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            sources.append({
                "content": doc.get("content", "")[:300] + "...",
                "company": metadata.get("company", "Unknown"),
                "year": metadata.get("year", "N/A"),
                "quarter": metadata.get("quarter", "N/A"),
                "page": metadata.get("page", "N/A"),
                "similarity": round(1.0 - doc.get("distance", 0), 3) if doc.get("distance") is not None else None
            })
        
        return sources
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary."""
        return self.cost_tracker.get_summary()


def demo():
    """Demo function to test RAG pipeline."""
    pipeline = RAGPipeline()
    
    # Sample queries
    queries = [
        "What were the revenue drivers in Q3 2024?",
        "How did operating expenses change?",
        "What are the key risk factors mentioned?"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        response = pipeline.query(query, filters={"company": "Apple", "year": 2024})
        
        print(f"\nAnswer:\n{response['answer']}")
        print(f"\nSources: {len(response['sources'])}")
        print(f"\nMetrics:")
        for key, value in response['metrics'].items():
            print(f"  {key}: {value}")
    
    # Cost summary
    print(f"\n{'='*60}")
    print("💰 Cost Summary (FREE!)")
    print('='*60)
    summary = pipeline.get_cost_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    demo()
