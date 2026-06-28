"""
LLM Analysis Module for Spotify Reviews
Phase 3: LLM Integration & Analysis
Uses Groq API for fast inference
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable, Tuple
import hashlib

try:
    from groq import Groq
except ImportError:
    print("groq package not installed. Install with: pip install groq")
    exit(1)


class GroqAnalyzer:
    """Analyze Spotify reviews using Groq LLM API."""
    
    def __init__(
        self,
        api_key: str = None,
        model: str = "llama-3.1-8b-instant",
        input_dir: str = "../phase2-data-cleaning/data/processed",
        output_dir: str = "data/results",
        cache_dir: str = "data/cache"
    ):
        """
        Initialize the Groq analyzer.
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env variable)
            model: Groq model to use
            input_dir: Directory containing cleaned review data
            output_dir: Directory to store analysis results
            cache_dir: Directory for caching LLM responses
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Research questions
        self.research_questions = {
            "q1": "Why do users struggle to discover new music?",
            "q2": "What are the most common frustrations with recommendations?",
            "q3": "What listening behaviors are users trying to achieve?",
            "q4": "What causes users to repeatedly listen to the same content?",
            "q5": "Which user segments experience different discovery challenges?",
            "q6": "What unmet needs emerge consistently across reviews?"
        }
        
        # Statistics
        self.stats = {
            "total_reviews_analyzed": 0,
            "total_api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_tokens_used": 0,
            "analysis_time_seconds": 0,
            "batches_processed": 0,
            "analysis_mode": "sample"
        }
        
        # Rate limiting for TPM (Tokens Per Minute)
        self.tpm_limit = 6000  # Groq's TPM limit for llama-3.1-8b-instant
        self.api_call_times = []  # Track timestamps and tokens for TPM calculation

    DEFAULT_BATCH_SIZE = 10
    SYNTHESIS_GROUP_SIZE = 3
    
    def load_cleaned_data(self, filepath: str = None) -> List[Dict]:
        """
        Load cleaned review data from JSON file.
        
        Args:
            filepath: Path to cleaned data file. If None, uses the most recent file.
            
        Returns:
            List of review dictionaries
        """
        if filepath is None:
            files = list(self.input_dir.glob("spotify_reviews_cleaned_*.json"))
            if not files:
                raise FileNotFoundError(f"No cleaned data files found in {self.input_dir}")
            filepath = max(files, key=lambda f: f.stat().st_mtime)
            print(f"Loading data from: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        
        print(f"Loaded {len(reviews)} cleaned reviews")
        self.stats["total_reviews_analyzed"] = len(reviews)
        return reviews
    
    def create_system_prompt(self) -> str:
        """
        Create the system prompt for the LLM.
        
        Returns:
            System prompt string
        """
        return """You are a product insights analyst specializing in music streaming services. 
Your task is to analyze Spotify user reviews and extract actionable product insights.

Focus on:
- User pain points and frustrations
- User behaviors and preferences
- Unmet needs and feature requests
- Patterns across different user segments

Provide concise, data-driven insights (3-4 lines per answer) based on the review data.
Avoid technical jargon. Focus on clear product insights that can inform product decisions."""
    
    def create_user_prompt(self, question: str, reviews: List[Dict], sample_size: int = 100) -> str:
        """
        Create a user prompt for a specific research question.
        
        Args:
            question: Research question to answer
            reviews: List of review dictionaries
            sample_size: Number of reviews to include in prompt
            
        Returns:
            User prompt string
        """
        # Sample reviews to avoid token limits
        sampled_reviews = reviews[:sample_size]
        
        # Extract review content
        review_texts = []
        for review in sampled_reviews:
            content = review.get("content", "")
            score = review.get("score", "")
            review_texts.append(f"Rating: {score}/5 - {content}")
        
        reviews_text = "\n\n".join(review_texts)
        
        prompt = f"""Based on the following Spotify user reviews, answer this research question:

RESEARCH QUESTION: {question}

USER REVIEWS:
{reviews_text}

Provide a concise answer (3-4 lines) based on the review data above.
Focus on clear product insights rather than technical analysis."""
        
        return prompt

    def _chunk_reviews(self, reviews: List[Dict], batch_size: int) -> List[List[Dict]]:
        return [reviews[i:i + batch_size] for i in range(0, len(reviews), batch_size)]

    def _format_reviews_for_prompt(self, reviews: List[Dict]) -> str:
        review_texts = []
        for review in reviews:
            content = review.get("content", "")
            score = review.get("score", "")
            # Truncate content to reduce token count
            if len(content) > 200:
                content = content[:200] + "..."
            review_texts.append(f"Rating: {score}/5 - {content}")
        return "\n\n".join(review_texts)

    def create_batch_prompt(
        self,
        question: str,
        batch_reviews: List[Dict],
        batch_index: int,
        total_batches: int
    ) -> str:
        reviews_text = self._format_reviews_for_prompt(batch_reviews)

        return f"""You are analyzing batch {batch_index + 1} of {total_batches} from a large Spotify review dataset.

RESEARCH QUESTION: {question}

USER REVIEWS IN THIS BATCH:
{reviews_text}

Extract the key product insights from this batch only.
Return 3-5 short bullet points focused on patterns relevant to the research question.
Do not write a final summary yet."""

    def create_multi_question_batch_prompt(
        self,
        batch_reviews: List[Dict],
        batch_index: int,
        total_batches: int
    ) -> str:
        reviews_text = self._format_reviews_for_prompt(batch_reviews)

        return f"""You are analyzing batch {batch_index + 1} of {total_batches} from a large Spotify review dataset.

USER REVIEWS IN THIS BATCH:
{reviews_text}

For this batch, extract key insights for ALL of the following research questions:

1. Why do users struggle to discover new music?
2. What are the most common frustrations with recommendations?
3. What listening behaviors are users trying to achieve?
4. What causes users to repeatedly listen to the same content?
5. Which user segments experience different discovery challenges?
6. What unmet needs emerge consistently across reviews?

For each question, provide 2-3 short bullet points focused on patterns in this batch.
Format your response as:
Q1: [insights]
Q2: [insights]
Q3: [insights]
Q4: [insights]
Q5: [insights]
Q6: [insights]"""

    def create_synthesis_prompt(self, question: str, insights: List[str], total_reviews: int) -> str:
        # Truncate each insight to reduce token count
        truncated_insights = []
        for insight in insights:
            if len(insight) > 300:
                truncated_insights.append(insight[:300] + "...")
            else:
                truncated_insights.append(insight)
        
        combined_insights = "\n\n".join(
            f"Insight group {index + 1}:\n{insight}"
            for index, insight in enumerate(truncated_insights)
        )

        return f"""You have insights extracted from all {total_reviews} Spotify user reviews, grouped below.

RESEARCH QUESTION: {question}

EXTRACTED INSIGHTS:
{combined_insights}

Synthesize these into one concise answer of 3-4 lines.
Focus on clear product insights rather than technical analysis."""

    def _hash_content(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def get_batch_cache_key(
        self,
        question: str,
        batch_index: int,
        batch_reviews: List[Dict],
        total_reviews: int,
        batch_size: int
    ) -> str:
        batch_signature = "".join(review.get("content", "") for review in batch_reviews)
        content = f"{question}|batch|{batch_index}|{total_reviews}|{batch_size}|{batch_signature}"
        return self._hash_content(content)

    def get_synthesis_cache_key(
        self,
        question: str,
        total_reviews: int,
        batch_size: int,
        batch_count: int
    ) -> str:
        content = f"{question}|synthesis|{total_reviews}|{batch_size}|{batch_count}"
        return self._hash_content(content)
    
    def get_cache_key(self, question: str, reviews_sample: List[str]) -> str:
        """
        Generate a cache key for a specific question and review sample.
        
        Args:
            question: Research question
            reviews_sample: Sample of review texts
            
        Returns:
            Cache key string
        """
        content = question + "".join(reviews_sample)
        return hashlib.md5(content.encode()).hexdigest()
    
    def check_cache(self, cache_key: str) -> Optional[str]:
        """
        Check if response exists in cache.
        
        Args:
            cache_key: Cache key to look up
            
        Returns:
            Cached response if exists, None otherwise
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            self.stats["cache_hits"] += 1
            return cached_data.get("response")
        return None
    
    def save_to_cache(self, cache_key: str, response: str, metadata: Dict = None):
        """
        Save response to cache.
        
        Args:
            cache_key: Cache key
            response: LLM response
            metadata: Additional metadata to store
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        cache_data = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    
    def call_groq_api(self, prompt: str, max_retries: int = 3, max_tokens: int = 500, stage: str = "unknown", batch_num: int = 0, items_count: int = 0) -> str:
        """
        Call Groq API with retry logic.
        
        Args:
            prompt: User prompt
            max_retries: Maximum number of retry attempts
            stage: Current stage (batch_analysis, intermediate_synthesis, final_synthesis)
            batch_num: Batch number
            items_count: Number of reviews or summaries being sent
            
        Returns:
            LLM response
        """
        # Log before API call
        prompt_length = len(prompt)
        estimated_tokens = prompt_length // 4  # Rough estimate: 1 token ≈ 4 characters
        print(f"\n=== GROQ API CALL ===")
        print(f"Stage: {stage}")
        print(f"Batch/Step: {batch_num}")
        print(f"Items being sent: {items_count}")
        print(f"Prompt length: {prompt_length} characters")
        print(f"Estimated tokens: {estimated_tokens}")
        print(f"Max tokens requested: {max_tokens}")
        print(f"=====================\n")
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.create_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=False
                )
                
                self.stats["total_api_calls"] += 1
                self.stats["total_tokens_used"] += response.usage.total_tokens
                
                print(f"API call successful. Tokens used: {response.usage.total_tokens}")
                
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Groq API call failed after {max_retries} attempts: {e}")
    
    def analyze_question(
        self,
        question_key: str,
        question: str,
        reviews: List[Dict],
        use_cache: bool = True,
        sample_size: int = 100
    ) -> Dict:
        """
        Analyze a single research question.
        
        Args:
            question_key: Question identifier (q1, q2, etc.)
            question: Research question text
            reviews: List of review dictionaries
            use_cache: Whether to use caching
            sample_size: Number of reviews to analyze
            
        Returns:
            Dictionary with question and answer
        """
        print(f"\nAnalyzing: {question}")
        
        # Sample reviews
        sampled_reviews = reviews[:sample_size]
        review_texts = [r.get("content", "") for r in sampled_reviews]
        
        # Check cache
        if use_cache:
            cache_key = self.get_cache_key(question, review_texts)
            cached_response = self.check_cache(cache_key)
            if cached_response:
                print("Cache hit - using cached response")
                return {
                    "question": question,
                    "answer": cached_response,
                    "cached": True,
                    "reviews_analyzed": len(sampled_reviews)
                }
        
        self.stats["cache_misses"] += 1
        
        # Create prompt
        prompt = self.create_user_prompt(question, sampled_reviews, sample_size)
        
        # Call API
        print("Calling Groq API...")
        response = self.call_groq_api(prompt, stage="sample_analysis", batch_num=1, items_count=sample_size)
        
        # Cache response
        if use_cache:
            cache_key = self.get_cache_key(question, review_texts)
            self.save_to_cache(
                cache_key,
                response,
                metadata={
                    "question": question,
                    "reviews_count": len(sampled_reviews),
                    "model": self.model
                }
            )
        
        return {
            "question": question,
            "answer": response,
            "cached": False,
            "reviews_analyzed": len(sampled_reviews)
        }

    def _synthesize_insights(
        self,
        question: str,
        insights: List[str],
        total_reviews: int,
        use_cache: bool,
        batch_size: int,
        batch_count: int
    ) -> Tuple[str, bool]:
        cache_key = self.get_synthesis_cache_key(question, total_reviews, batch_size, batch_count)
        if use_cache:
            cached_response = self.check_cache(cache_key)
            if cached_response:
                return cached_response, True

        working_insights = insights

        # Keep synthesizing in groups until we have a manageable number
        while len(working_insights) > 5:
            grouped_insights = []
            for group_index in range(0, len(working_insights), 2):
                group = working_insights[group_index:group_index + 2]
                prompt = self.create_synthesis_prompt(question, group, total_reviews)
                grouped_insights.append(self.call_groq_api(prompt, max_tokens=350, stage="intermediate_synthesis", batch_num=group_index+1, items_count=len(group)))
            working_insights = grouped_insights

        self.stats["cache_misses"] += 1
        # Final synthesis with at most 5 insights
        final_insights = working_insights[:5]
        prompt = self.create_synthesis_prompt(question, final_insights, total_reviews)
        response = self.call_groq_api(prompt, max_tokens=500, stage="final_synthesis", batch_num=1, items_count=len(final_insights))

        if use_cache:
            self.save_to_cache(
                cache_key,
                response,
                metadata={
                    "question": question,
                    "reviews_count": total_reviews,
                    "batch_count": batch_count,
                    "model": self.model,
                    "type": "synthesis"
                }
            )

        return response, False

    def analyze_question_full_dataset(
        self,
        question_key: str,
        question: str,
        reviews: List[Dict],
        use_cache: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        progress_start: float = 0.0,
        progress_end: float = 100.0
    ) -> Dict:
        batches = self._chunk_reviews(reviews, batch_size)
        total_batches = len(batches)
        batch_insights: List[str] = []
        all_cached = True

        print(f"\nAnalyzing full dataset for: {question}")
        print(f"Processing {len(reviews)} reviews in {total_batches} batches")

        for batch_index, batch_reviews in enumerate(batches):
            cache_key = self.get_batch_cache_key(
                question,
                batch_index,
                batch_reviews,
                len(reviews),
                batch_size
            )

            if use_cache:
                cached_response = self.check_cache(cache_key)
                if cached_response:
                    batch_insights.append(cached_response)
                    self.stats["batches_processed"] += 1
                    if progress_callback:
                        progress = progress_start + ((batch_index + 1) / (total_batches + 1)) * (progress_end - progress_start)
                        progress_callback(
                            progress,
                            f"Analyzing reviews batch {batch_index + 1} of {total_batches}"
                        )
                    continue

            all_cached = False
            self.stats["cache_misses"] += 1
            prompt = self.create_batch_prompt(question, batch_reviews, batch_index, total_batches)
            print(f"Calling Groq API for batch {batch_index + 1}/{total_batches}...")
            batch_response = self.call_groq_api(prompt, max_tokens=300, stage="batch_analysis", batch_num=batch_index+1, items_count=len(batch_reviews))
            batch_insights.append(batch_response)
            self.stats["batches_processed"] += 1

            if use_cache:
                self.save_to_cache(
                    cache_key,
                    batch_response,
                    metadata={
                        "question": question,
                        "batch_index": batch_index,
                        "reviews_count": len(batch_reviews),
                        "model": self.model,
                        "type": "batch"
                    }
                )

            if progress_callback:
                progress = progress_start + ((batch_index + 1) / (total_batches + 1)) * (progress_end - progress_start)
                progress_callback(
                    progress,
                    f"Analyzing reviews batch {batch_index + 1} of {total_batches}"
                )

        if progress_callback:
            progress_callback(progress_end - 1, "Synthesizing insights across all reviews")

        final_answer, synthesis_cached = self._synthesize_insights(
            question,
            batch_insights,
            len(reviews),
            use_cache,
            batch_size,
            total_batches
        )

        return {
            "question": question,
            "answer": final_answer,
            "cached": all_cached and synthesis_cached,
            "reviews_analyzed": len(reviews),
            "batches_processed": total_batches
        }
    
    def analyze_all_questions(
        self,
        reviews: List[Dict],
        use_cache: bool = True,
        sample_size: int = 100,
        use_all_reviews: bool = False,
        batch_size: int = DEFAULT_BATCH_SIZE,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict:
        """
        Analyze all research questions.
        
        Args:
            reviews: List of review dictionaries
            use_cache: Whether to use caching
            sample_size: Number of reviews to analyze per question when sampling
            use_all_reviews: Whether to analyze the full dataset in batches
            batch_size: Number of reviews per batch when use_all_reviews is True
            progress_callback: Optional callback for workflow progress updates
            
        Returns:
            Dictionary with all questions and answers
        """
        start_time = time.time()
        question_count = len(self.research_questions)
        
        print(f"Starting analysis of {question_count} research questions...")
        print(f"Using model: {self.model}")

        if use_all_reviews:
            self.stats["analysis_mode"] = "full_dataset"
            print(f"Full dataset mode: {len(reviews)} reviews in batches of {batch_size}")
        else:
            self.stats["analysis_mode"] = "sample"
            print(f"Sample mode: {sample_size} reviews per question")
        
        results = {}
        
        for index, (key, question) in enumerate(self.research_questions.items()):
            progress_start = (index / question_count) * 100
            progress_end = ((index + 1) / question_count) * 100

            def question_progress(progress: float, step: str, start=progress_start, end=progress_end):
                if progress_callback:
                    scaled_progress = start + (progress / 100) * (end - start)
                    progress_callback(scaled_progress, step)

            try:
                if use_all_reviews:
                    result = self.analyze_question_full_dataset(
                        key,
                        question,
                        reviews,
                        use_cache=use_cache,
                        batch_size=batch_size,
                        progress_callback=question_progress
                    )
                else:
                    result = self.analyze_question(key, question, reviews, use_cache, sample_size)
                results[key] = result
                print(f"✓ Completed: {question[:50]}...")
            except Exception as e:
                print(f"✗ Failed: {question[:50]}... - {e}")
                reviewed_count = len(reviews) if use_all_reviews else min(sample_size, len(reviews))
                results[key] = {
                    "question": question,
                    "answer": f"Analysis failed: {str(e)}",
                    "cached": False,
                    "reviews_analyzed": reviewed_count
                }
        
        self.stats["analysis_time_seconds"] = time.time() - start_time
        
        return results
    
    def _analyze_all_questions_batch_consolidate(
        self,
        reviews: List[Dict],
        use_cache: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict:
        """
        New approach: Batch -> Summarize -> Consolidate
        - Process all reviews in batches of 100
        - Each batch extracts insights for ALL 6 questions in ONE API call
        - Then synthesize batch summaries for each question in final API calls
        """
        start_time = time.time()
        batches = self._chunk_reviews(reviews, batch_size)
        total_batches = len(batches)
        
        print(f"\nUsing batch -> summarize -> consolidate approach")
        print(f"Processing {len(reviews)} reviews in {total_batches} batches of {batch_size}")
        
        # Step 1: Process each batch to extract insights for all questions
        batch_summaries = []  # List of dicts with q1-q6 insights for each batch
        all_cached = True
        
        for batch_index, batch_reviews in enumerate(batches):
            # Create cache key for this batch
            batch_signature = "".join(review.get("content", "") for review in batch_reviews)
            cache_key = self._hash_content(f"multi_batch|{batch_index}|{total_batches}|{batch_size}|{batch_signature}")
            
            if use_cache:
                cached_response = self.check_cache(cache_key)
                if cached_response:
                    batch_summaries.append(cached_response)
                    self.stats["batches_processed"] += 1
                    self.stats["cache_hits"] += 1
                    if progress_callback:
                        progress = (batch_index + 1) / total_batches * 50  # First 50% for batching
                        progress_callback(progress, f"Processing batch {batch_index + 1} of {total_batches} (cached)")
                    continue
            
            all_cached = False
            self.stats["cache_misses"] += 1
            
            # Call Groq once to extract insights for ALL 6 questions from this batch
            prompt = self.create_multi_question_batch_prompt(batch_reviews, batch_index, total_batches)
            print(f"Calling Groq API for batch {batch_index + 1}/{total_batches} (multi-question)...")
            batch_response = self.call_groq_api(prompt, max_tokens=800, stage="multi_question_batch", batch_num=batch_index+1, items_count=len(batch_reviews))
            batch_summaries.append(batch_response)
            self.stats["batches_processed"] += 1
            
            if use_cache:
                self.save_to_cache(cache_key, batch_response, metadata={
                    "batch_index": batch_index,
                    "reviews_count": len(batch_reviews),
                    "model": self.model,
                    "type": "multi_batch"
                })
            
            if progress_callback:
                progress = (batch_index + 1) / total_batches * 50  # First 50% for batching
                progress_callback(progress, f"Processing batch {batch_index + 1} of {total_batches}")
        
        # Step 2: Synthesize batch summaries for each question
        results = {}
        question_keys = list(self.research_questions.keys())
        
        for q_index, (key, question) in enumerate(self.research_questions.items()):
            if progress_callback:
                progress = 50 + (q_index / len(question_keys)) * 50  # Last 50% for synthesis
                progress_callback(progress, f"Synthesizing insights for question {q_index + 1} of {len(question_keys)}")
            
            # Extract insights for this question from all batch summaries
            question_insights = []
            for batch_summary in batch_summaries:
                # Parse the batch summary to extract insights for this question
                lines = batch_summary.split('\n')
                for line in lines:
                    if line.startswith(f'Q{q_index + 1}:'):
                        question_insights.append(line.replace(f'Q{q_index + 1}:', '').strip())
                        break
            
            if not question_insights:
                question_insights = ["No insights extracted from batches"]
            
            # Synthesize the insights for this question
            synthesis_prompt = self.create_synthesis_prompt(question, question_insights, len(reviews))
            print(f"Synthesizing insights for question {q_index + 1}/{len(question_keys)}...")
            final_answer = self.call_groq_api(synthesis_prompt, max_tokens=500, stage="multi_question_synthesis", batch_num=q_index+1, items_count=len(question_insights))
            
            results[key] = {
                "question": question,
                "answer": final_answer,
                "cached": all_cached,
                "reviews_analyzed": len(reviews),
                "batches_processed": total_batches
            }
        
        self.stats["analysis_time_seconds"] = time.time() - start_time
        return results
    
    def save_results(self, results: Dict, filename: str = None) -> str:
        """
        Save analysis results to JSON file.
        
        Args:
            results: Analysis results dictionary
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_results_{timestamp}.json"
        
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "model_used": self.model,
            "statistics": self.stats,
            "results": results
        }
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved results to {filepath}")
        return str(filepath)
    
    def print_results(self, results: Dict):
        """
        Print analysis results in a readable format.
        
        Args:
            results: Analysis results dictionary
        """
        print("\n" + "="*70)
        print("SPOTIFY REVIEW ANALYSIS RESULTS")
        print("="*70)
        
        for key, result in results.items():
            print(f"\n{result['question']}")
            print("-" * 70)
            print(result['answer'])
            print(f"(Analyzed {result['reviews_analyzed']} reviews, Cached: {result['cached']})")
        
        print("\n" + "="*70)
        print("STATISTICS")
        print("="*70)
        print(f"Total reviews analyzed:    {self.stats['total_reviews_analyzed']}")
        print(f"Total API calls:           {self.stats['total_api_calls']}")
        print(f"Cache hits:                {self.stats['cache_hits']}")
        print(f"Cache misses:              {self.stats['cache_misses']}")
        print(f"Total tokens used:         {self.stats['total_tokens_used']}")
        print(f"Analysis time:             {self.stats['analysis_time_seconds']:.2f} seconds")
        print("="*70 + "\n")


def main():
    """Main execution function."""
    # Initialize analyzer
    analyzer = GroqAnalyzer(
        model="llama-3.1-8b-instant",
        input_dir="../phase2-data-cleaning/data/processed",
        output_dir="data/results",
        cache_dir="data/cache"
    )
    
    try:
        # Load cleaned data
        reviews = analyzer.load_cleaned_data()
        
        # Analyze all questions with smaller sample size
        results = analyzer.analyze_all_questions(
            reviews,
            use_cache=True,
            sample_size=20
        )
        
        # Print results
        analyzer.print_results(results)
        
        # Save results
        analyzer.save_results(results)
        
        print("\nLLM analysis completed successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure Phase 2 has been completed and cleaned data is available.")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GROQ_API_KEY environment variable.")
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main()
