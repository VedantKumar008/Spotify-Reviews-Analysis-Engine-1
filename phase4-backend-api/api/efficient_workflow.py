"""
Efficient workflow for large-scale review analysis.
Uses deterministic processing for intermediate steps and LLM only for final synthesis.
"""

from typing import List, Dict, Callable, Optional
from datetime import datetime
import time
from pathlib import Path
import json

from .deterministic_analyzer import DeterministicAnalyzer
from .database import DatabaseManager
from .groq_utils import get_groq_api_key
from groq import Groq

class EfficientWorkflow:
    """Efficient workflow with minimal LLM calls."""
    
    def __init__(self, database_url: str = None):
        self.db = DatabaseManager(database_url)
        self.deterministic_analyzer = DeterministicAnalyzer()
        self.api_key = get_groq_api_key()
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.1-8b-instant"
        
        self.research_questions = {
            "q1": "Why do users struggle to discover new music?",
            "q2": "What are the most common frustrations with recommendations?",
            "q3": "What listening behaviors are users trying to achieve?",
            "q4": "What causes users to repeatedly listen to the same content?",
            "q5": "Which user segments experience different discovery challenges?",
            "q6": "What unmet needs emerge consistently across reviews?"
        }
    
    def run_workflow(
        self,
        workflow_id: str,
        reviews: List[Dict],
        batch_size: int = 100,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        force_refresh: bool = False
    ) -> Dict:
        """
        Run efficient workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            reviews: List of review dictionaries
            batch_size: Number of reviews per batch
            progress_callback: Optional progress callback
            force_refresh: Force re-analysis even if cached results exist
            
        Returns:
            Final insights
        """
        start_time = time.time()
        total_reviews = len(reviews)
        total_batches = (total_reviews + batch_size - 1) // batch_size
        
        # Check if cached results exist
        if not force_refresh:
            cached_insights = self.db.get_cached_insights(workflow_id)
            if cached_insights and cached_insights.total_reviews == total_reviews:
                print(f"Returning cached insights for workflow {workflow_id}")
                if progress_callback:
                    progress_callback(100.0, "Loading cached insights")
                return {
                    "generated_at": cached_insights.generated_at.isoformat(),
                    "model_used": self.model,
                    "statistics": {
                        "total_reviews_analyzed": total_reviews,
                        "total_api_calls": 0,
                        "cache_hits": 1,
                        "cache_misses": 0,
                        "analysis_time_seconds": 0,
                        "batches_processed": total_batches,
                        "analysis_mode": "cached"
                    },
                    "results": cached_insights.insights,
                    "cached": True
                }
        
        # Create workflow record
        self.db.create_workflow(workflow_id, total_reviews, total_batches)
        
        if progress_callback:
            progress_callback(5.0, "Starting deterministic analysis")
        
        # Step 1: Deterministic batch processing (no LLM calls)
        print(f"Processing {total_reviews} reviews in {total_batches} batches deterministically")
        batch_analyses = []
        
        for batch_index in range(total_batches):
            start_idx = batch_index * batch_size
            end_idx = min(start_idx + batch_size, total_reviews)
            batch_reviews = reviews[start_idx:end_idx]
            
            # Process batch deterministically
            batch_result = self.deterministic_analyzer.process_batch(batch_reviews, batch_index)
            batch_analyses.append(batch_result)
            
            # Save to database
            self.db.save_batch_analysis(
                workflow_id,
                batch_index,
                batch_result['patterns'],
                len(batch_reviews)
            )
            
            # Update progress
            progress = 5.0 + ((batch_index + 1) / total_batches) * 40.0
            if progress_callback:
                progress_callback(progress, f"Processing batch {batch_index + 1} of {total_batches} deterministically")
            
            # Update workflow
            self.db.update_workflow(
                workflow_id,
                batches_processed=batch_index + 1,
                progress=progress,
                current_step=f"Processing batch {batch_index + 1} of {total_batches}"
            )
        
        if progress_callback:
            progress_callback(45.0, "Aggregating batch patterns")
        
        # Step 2: Aggregate patterns from all batches
        aggregated_patterns = self._aggregate_patterns(batch_analyses)
        
        if progress_callback:
            progress_callback(50.0, "Generating final insights with LLM")
        
        # Step 3: Single LLM call for final synthesis (6 questions, 1 call each = 6 total)
        final_insights = self._synthesize_with_llm(aggregated_patterns, total_reviews)
        
        if progress_callback:
            progress_callback(95.0, "Caching final insights")
        
        # Step 4: Cache final insights
        self.db.cache_final_insights(workflow_id, final_insights, total_reviews)
        
        # Mark workflow as complete
        self.db.update_workflow(
            workflow_id,
            status='completed',
            progress=100.0,
            current_step='Completed',
            completed_at=datetime.utcnow()
        )
        
        analysis_time = time.time() - start_time
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "model_used": self.model,
            "statistics": {
                "total_reviews_analyzed": total_reviews,
                "total_api_calls": 6,  # Only 6 LLM calls (one per question)
                "cache_hits": 0,
                "cache_misses": 6,
                "analysis_time_seconds": analysis_time,
                "batches_processed": total_batches,
                "analysis_mode": "efficient"
            },
            "results": final_insights,
            "cached": False
        }
    
    def _aggregate_patterns(self, batch_analyses: List[Dict]) -> Dict:
        """Aggregate patterns from all batches."""
        from collections import Counter
        
        all_keywords = Counter()
        all_themes = Counter()
        total_sentiment = 0
        total_reviews = 0
        
        for batch in batch_analyses:
            patterns = batch['patterns']
            
            # Aggregate keywords
            for kw in patterns.get('top_keywords', []):
                all_keywords[kw['keyword']] += kw['count']
            
            # Aggregate themes
            for theme, count in patterns.get('themes', {}).items():
                all_themes[theme] += count
            
            # Aggregate sentiment
            total_sentiment += patterns.get('avg_sentiment', 0) * patterns.get('review_count', 0)
            total_reviews += patterns.get('review_count', 0)
        
        avg_sentiment = total_sentiment / total_reviews if total_reviews > 0 else 0
        
        return {
            'top_keywords': [{'keyword': k, 'count': c} for k, c in all_keywords.most_common(30)],
            'themes': dict(all_themes.most_common()),
            'avg_sentiment': avg_sentiment,
            'total_reviews': total_reviews
        }
    
    def _synthesize_with_llm(self, aggregated_patterns: Dict, total_reviews: int) -> Dict:
        """Synthesize final insights using LLM (one call per question)."""
        results = {}
        
        patterns_text = self._format_patterns_for_llm(aggregated_patterns)
        
        for key, question in self.research_questions.items():
            prompt = f"""Based on the following aggregated analysis of {total_reviews} Spotify reviews, answer this research question:

RESEARCH QUESTION: {question}

AGGREGATED PATTERNS:
{patterns_text}

Provide a concise answer (3-4 lines) based on the patterns above.
Focus on clear product insights rather than technical analysis."""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a product analyst specializing in music streaming apps."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=300,
                    top_p=1,
                    stream=False
                )
                
                results[key] = {
                    "question": question,
                    "answer": response.choices[0].message.content,
                    "cached": False,
                    "reviews_analyzed": total_reviews
                }
                
                print(f"✓ Synthesized answer for {key}")
                
            except Exception as e:
                print(f"✗ Failed to synthesize {key}: {e}")
                results[key] = {
                    "question": question,
                    "answer": f"Analysis failed: {str(e)}",
                    "cached": False,
                    "reviews_analyzed": total_reviews
                }
        
        return results
    
    def _format_patterns_for_llm(self, patterns: Dict) -> str:
        """Format aggregated patterns for LLM prompt."""
        lines = []
        
        # Keywords
        lines.append("TOP KEYWORDS:")
        for kw in patterns['top_keywords'][:20]:
            lines.append(f"- {kw['keyword']}: {kw['count']} mentions")
        
        lines.append("\nTHEMES:")
        for theme, count in patterns['themes'].items():
            lines.append(f"- {theme}: {count} mentions")
        
        lines.append(f"\nAVERAGE SENTIMENT: {patterns['avg_sentiment']:.2f}")
        lines.append(f"TOTAL REVIEWS: {patterns['total_reviews']}")
        
        return "\n".join(lines)
    
    def resume_workflow(self, workflow_id: str, progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict:
        """Resume a workflow from database checkpoint."""
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow.status == 'completed':
            cached_insights = self.db.get_cached_insights(workflow_id)
            if cached_insights:
                return {
                    "generated_at": cached_insights.generated_at.isoformat(),
                    "model_used": self.model,
                    "statistics": {
                        "total_reviews_analyzed": workflow.total_reviews,
                        "total_api_calls": 0,
                        "cache_hits": 1,
                        "cache_misses": 0,
                        "analysis_time_seconds": 0,
                        "batches_processed": workflow.batches_processed,
                        "analysis_mode": "resumed_cached"
                    },
                    "results": cached_insights.insights,
                    "cached": True
                }
        
        # Resume from last checkpoint
        batch_analyses = self.db.get_batch_analyses(workflow_id)
        
        if progress_callback:
            progress_callback(workflow.progress, workflow.current_step)
        
        # Continue with synthesis if all batches are processed
        if len(batch_analyses) == workflow.total_batches:
            aggregated_patterns = self._aggregate_patterns(
                [{'batch_id': b.batch_id, 'patterns': b.patterns} for b in batch_analyses]
            )
            final_insights = self._synthesize_with_llm(aggregated_patterns, workflow.total_reviews)
            self.db.cache_final_insights(workflow_id, final_insights, workflow.total_reviews)
            
            self.db.update_workflow(
                workflow_id,
                status='completed',
                progress=100.0,
                current_step='Completed',
                completed_at=datetime.utcnow()
            )
            
            return {
                "generated_at": datetime.utcnow().isoformat(),
                "model_used": self.model,
                "statistics": {
                    "total_reviews_analyzed": workflow.total_reviews,
                    "total_api_calls": 6,
                    "cache_hits": 0,
                    "cache_misses": 6,
                    "analysis_time_seconds": 0,
                    "batches_processed": workflow.total_batches,
                    "analysis_mode": "resumed"
                },
                "results": final_insights,
                "cached": False
            }
        
        raise ValueError(f"Workflow {workflow_id} cannot be resumed from current state")
