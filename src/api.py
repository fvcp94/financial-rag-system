"""FastAPI REST API for Financial RAG System."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from loguru import logger

from .rag_pipeline import RAGPipeline
from .vector_store import VectorStoreManager
from .data_ingestion import DocumentProcessor

# Initialize FastAPI app
app = FastAPI(
    title="Financial RAG API",
    description="Production-ready RAG system for financial document analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
rag_pipeline = RAGPipeline()
logger.info("RAG Pipeline initialized successfully")


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str = Field(..., description="User's question", min_length=5)
    company: Optional[str] = Field(None, description="Filter by company name")
    year: Optional[int] = Field(None, ge=2020, le=2030, description="Filter by year")
    quarter: Optional[str] = Field(None, pattern="^Q[1-4]$", description="Filter by quarter (Q1-Q4)")
    top_k: Optional[int] = Field(4, ge=1, le=10, description="Number of documents to retrieve")


class Source(BaseModel):
    """Source document model."""
    content: str
    company: str
    year: Any
    quarter: Any
    page: Any
    similarity: Optional[float]


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    sources: List[Source]
    metrics: Dict[str, Any]
    success: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    vector_store_count: int


class StatsResponse(BaseModel):
    """Statistics response."""
    collection_stats: Dict[str, Any]
    cost_summary: Dict[str, Any]


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Financial RAG API",
        "version": "1.0.0",
        "description": "Query financial documents using RAG",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    try:
        vs_manager = VectorStoreManager()
        stats = vs_manager.get_collection_stats()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            vector_store_count=stats.get("total_documents", 0)
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")


@app.post("/api/query", response_model=QueryResponse, tags=["RAG"])
async def query_documents(request: QueryRequest):
    """
    Query financial documents using RAG.
    
    - **question**: Your question about financial documents
    - **company**: Optional filter by company name
    - **year**: Optional filter by year (2020-2030)
    - **quarter**: Optional filter by quarter (Q1-Q4)
    - **top_k**: Number of documents to retrieve (1-10)
    """
    try:
        # Build filters
        filters = {}
        if request.company:
            filters["company"] = request.company
        if request.year:
            filters["year"] = request.year
        if request.quarter:
            filters["quarter"] = request.quarter
        
        # Execute query
        logger.info(f"API query: '{request.question}' with filters: {filters}")
        
        response = rag_pipeline.query(
            question=request.question,
            filters=filters if filters else None,
            top_k=request.top_k
        )
        
        # Format sources
        sources = [Source(**source) for source in response["sources"]]
        
        return QueryResponse(
            answer=response["answer"],
            sources=sources,
            metrics=response["metrics"],
            success=response.get("success", True)
        )
    
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse, tags=["Analytics"])
async def get_statistics():
    """
    Get system statistics including vector store info and cost summary.
    """
    try:
        vs_manager = VectorStoreManager()
        collection_stats = vs_manager.get_collection_stats()
        cost_summary = rag_pipeline.get_cost_summary()
        
        return StatsResponse(
            collection_stats=collection_stats,
            cost_summary=cost_summary
        )
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies", tags=["Metadata"])
async def list_companies():
    """
    List all companies in the vector store.
    """
    # This would require querying metadata from vector store
    # Placeholder for future implementation
    return {
        "companies": ["Apple", "Microsoft", "Google", "Amazon", "Meta"],
        "note": "Sample list - implement proper metadata extraction"
    }


@app.get("/api/example-queries", tags=["Helper"])
async def example_queries():
    """
    Get example queries for testing.
    """
    return {
        "examples": [
            {
                "question": "What were the total revenues in Q3 2024?",
                "filters": {"year": 2024, "quarter": "Q3"}
            },
            {
                "question": "How did operating expenses change year-over-year?",
                "filters": {"company": "Apple"}
            },
            {
                "question": "What are the key risk factors mentioned?",
                "filters": None
            },
            {
                "question": "What were the main revenue drivers?",
                "filters": {"year": 2024}
            },
            {
                "question": "How did net income perform compared to last quarter?",
                "filters": {"company": "Microsoft", "year": 2024}
            }
        ]
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint not found",
        "path": str(request.url),
        "available_endpoints": ["/", "/health", "/docs", "/api/query", "/api/stats"]
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "message": str(exc)
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Financial RAG API starting up...")
    logger.info("RAG Pipeline ready")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Financial RAG API shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
