"""Evaluation module for RAG system performance testing."""

import json
import time
from typing import List, Dict, Any, Tuple
from loguru import logger

from .rag_pipeline import RAGPipeline
from .utils import load_config


class RAGEvaluator:
    """Evaluate RAG system performance with various metrics."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize evaluator with RAG pipeline."""
        self.config = load_config(config_path)
        self.pipeline = RAGPipeline(config_path)
        
        # Define test queries
        self.test_queries = [
            {
                "question": "What were the total revenues in Q3 2024?",
                "filters": {"year": 2024, "quarter": "Q3"},
                "expected_keywords": ["revenue", "billion", "Q3", "2024"]
            },
            {
                "question": "How did operating expenses change year-over-year?",
                "filters": {"year": 2024},
                "expected_keywords": ["operating expenses", "year-over-year", "percent"]
            },
            {
                "question": "What are the key risk factors mentioned?",
                "filters": None,
                "expected_keywords": ["risk", "factor"]
            },
            {
                "question": "What were the main growth drivers?",
                "filters": None,
                "expected_keywords": ["growth", "increase", "revenue"]
            },
            {
                "question": "How did net income perform compared to previous quarter?",
                "filters": {"year": 2024},
                "expected_keywords": ["net income", "quarter", "compared"]
            }
        ]
        
        logger.info(f"Initialized RAGEvaluator with {len(self.test_queries)} test queries")
    
    def calculate_answer_relevance(self, question: str, answer: str, expected_keywords: List[str]) -> float:
        """
        Calculate answer relevance score based on keyword presence.
        
        Returns score between 0.0 and 1.0
        """
        if not answer or not expected_keywords:
            return 0.0
        
        answer_lower = answer.lower()
        keywords_found = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        
        relevance_score = keywords_found / len(expected_keywords)
        return round(relevance_score, 3)
    
    def calculate_context_precision(self, sources: List[Dict[str, Any]], top_k: int = 4) -> float:
        """
        Calculate context precision - how many retrieved docs are relevant.
        
        Returns score between 0.0 and 1.0
        """
        if not sources:
            return 0.0
        
        # Assume docs with similarity > 0.7 are relevant
        relevant_docs = sum(1 for source in sources if source.get("similarity", 0) > 0.7)
        
        precision = relevant_docs / len(sources)
        return round(precision, 3)
    
    def calculate_faithfulness(self, answer: str, sources: List[Dict[str, Any]]) -> float:
        """
        Calculate faithfulness - whether answer is grounded in sources.
        
        Simple heuristic: check if answer contains phrases from sources.
        """
        if not answer or not sources:
            return 0.0
        
        answer_lower = answer.lower()
        source_texts = [source.get("content", "").lower() for source in sources]
        
        # Extract key phrases (3+ word sequences) from sources
        matches = 0
        total_checks = 0
        
        for source_text in source_texts:
            words = source_text.split()
            for i in range(len(words) - 2):
                phrase = " ".join(words[i:i+3])
                total_checks += 1
                if phrase in answer_lower:
                    matches += 1
        
        if total_checks == 0:
            return 0.5  # Neutral score if can't calculate
        
        faithfulness = min(matches / (total_checks * 0.1), 1.0)  # Normalize
        return round(faithfulness, 3)
    
    def evaluate_single_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single query."""
        question = test_case["question"]
        filters = test_case.get("filters")
        expected_keywords = test_case.get("expected_keywords", [])
        
        logger.info(f"Evaluating: '{question}'")
        
        # Run query
        start_time = time.time()
        response = self.pipeline.query(question=question, filters=filters)
        latency = time.time() - start_time
        
        # Calculate metrics
        answer_relevance = self.calculate_answer_relevance(
            question, 
            response.get("answer", ""), 
            expected_keywords
        )
        
        context_precision = self.calculate_context_precision(
            response.get("sources", [])
        )
        
        faithfulness = self.calculate_faithfulness(
            response.get("answer", ""),
            response.get("sources", [])
        )
        
        # Compile results
        result = {
            "question": question,
            "answer": response.get("answer", ""),
            "sources_count": len(response.get("sources", [])),
            "metrics": {
                "answer_relevance": answer_relevance,
                "context_precision": context_precision,
                "faithfulness": faithfulness,
                "latency": round(latency, 3),
                "cost": response.get("metrics", {}).get("total_cost", 0),
                "tokens": response.get("metrics", {}).get("total_tokens", 0)
            },
            "success": response.get("success", False)
        }
        
        return result
    
    def run_evaluation(self, save_results: bool = True) -> Dict[str, Any]:
        """Run full evaluation suite."""
        logger.info("Starting RAG system evaluation...")
        
        results = []
        total_latency = 0
        total_cost = 0
        
        for test_case in self.test_queries:
            result = self.evaluate_single_query(test_case)
            results.append(result)
            
            total_latency += result["metrics"]["latency"]
            total_cost += result["metrics"]["cost"]
        
        # Calculate aggregate metrics
        avg_relevance = sum(r["metrics"]["answer_relevance"] for r in results) / len(results)
        avg_precision = sum(r["metrics"]["context_precision"] for r in results) / len(results)
        avg_faithfulness = sum(r["metrics"]["faithfulness"] for r in results) / len(results)
        avg_latency = total_latency / len(results)
        
        summary = {
            "total_queries": len(results),
            "successful_queries": sum(1 for r in results if r["success"]),
            "aggregate_metrics": {
                "avg_answer_relevance": round(avg_relevance, 3),
                "avg_context_precision": round(avg_precision, 3),
                "avg_faithfulness": round(avg_faithfulness, 3),
                "avg_latency": round(avg_latency, 3),
                "total_cost": round(total_cost, 4)
            },
            "detailed_results": results
        }
        
        # Print summary
        self._print_summary(summary)
        
        # Save results
        if save_results:
            self._save_results(summary)
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print evaluation summary."""
        print("\n" + "="*60)
        print("RAG SYSTEM EVALUATION SUMMARY")
        print("="*60)
        
        print(f"\nTotal Queries: {summary['total_queries']}")
        print(f"Successful: {summary['successful_queries']}")
        
        print("\nAggregate Metrics:")
        for metric, value in summary["aggregate_metrics"].items():
            print(f"  {metric}: {value}")
        
        print("\n" + "="*60)
        print("DETAILED RESULTS")
        print("="*60)
        
        for idx, result in enumerate(summary["detailed_results"], 1):
            print(f"\n{idx}. {result['question']}")
            print(f"   Relevance: {result['metrics']['answer_relevance']}")
            print(f"   Precision: {result['metrics']['context_precision']}")
            print(f"   Faithfulness: {result['metrics']['faithfulness']}")
            print(f"   Latency: {result['metrics']['latency']}s")
            print(f"   Cost: ${result['metrics']['cost']:.6f}")
    
    def _save_results(self, summary: Dict[str, Any], filepath: str = "evaluation_results.json") -> None:
        """Save evaluation results to JSON file."""
        try:
            with open(filepath, "w") as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Evaluation results saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def compare_models(self, models: List[str]) -> Dict[str, Any]:
        """Compare performance across different LLM models."""
        # This would require modifying the pipeline to support model switching
        # Placeholder for future implementation
        logger.info("Model comparison feature - coming soon")
        return {}


def demo():
    """Demo function to run evaluation."""
    evaluator = RAGEvaluator()
    
    # Run evaluation
    results = evaluator.run_evaluation(save_results=True)
    
    # Print cost tracking summary
    print("\n" + "="*60)
    print("COST TRACKING SUMMARY")
    print("="*60)
    cost_summary = evaluator.pipeline.get_cost_summary()
    for key, value in cost_summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    demo()
