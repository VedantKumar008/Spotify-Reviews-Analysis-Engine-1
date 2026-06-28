"""
Data Cleaning Pipeline for Spotify Reviews
Phase 2: Data Preprocessing & Cleaning
"""

import json
import re
import string
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import Counter

try:
    import pandas as pd
    from langdetect import detect, LangDetectException
except ImportError:
    print("Required packages not installed. Install with: pip install pandas langdetect")
    exit(1)


class DataCleaningPipeline:
    """Pipeline for cleaning and preprocessing Spotify review data."""
    
    def __init__(self, input_dir: str = "../phase1-data-collection/data/raw", output_dir: str = "data/processed"):
        """
        Initialize the data cleaning pipeline.
        
        Args:
            input_dir: Directory containing raw review data
            output_dir: Directory to store cleaned data
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cleaning parameters
        self.min_content_length = 10
        self.max_content_length = 5000
        self.target_language = "en"
        self.spam_keywords = [
            "free", "download", "hack", "crack", "premium", "mod",
            "click here", "visit", "subscribe", "follow", "link"
        ]
        
        # Statistics
        self.stats = {
            "total_reviews": 0,
            "removed_duplicates": 0,
            "removed_spam": 0,
            "removed_too_short": 0,
            "removed_too_long": 0,
            "removed_non_english": 0,
            "removed_empty_content": 0,
            "final_count": 0
        }
    
    def load_raw_data(self, filepath: str = None) -> List[Dict]:
        """
        Load raw review data from JSON file.
        
        Args:
            filepath: Path to raw data file. If None, uses the most recent file.
            
        Returns:
            List of review dictionaries
        """
        if filepath is None:
            # Find the most recent raw data file
            files = list(self.input_dir.glob("spotify_reviews_raw_*.json"))
            if not files:
                raise FileNotFoundError(f"No raw data files found in {self.input_dir}")
            filepath = max(files, key=lambda f: f.stat().st_mtime)
            print(f"Loading data from: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        
        print(f"Loaded {len(reviews)} raw reviews")
        self.stats["total_reviews"] = len(reviews)
        return reviews
    
    def remove_duplicates(self, reviews: List[Dict]) -> List[Dict]:
        """
        Remove duplicate reviews based on review_id and content.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            List of unique reviews
        """
        seen_ids = set()
        seen_content = set()
        unique_reviews = []
        
        for review in reviews:
            review_id = review.get("review_id")
            content = review.get("content", "").strip().lower()
            
            # Check for duplicate IDs
            if review_id in seen_ids:
                self.stats["removed_duplicates"] += 1
                continue
            
            # Check for duplicate content (same text from different users)
            if content and content in seen_content:
                self.stats["removed_duplicates"] += 1
                continue
            
            seen_ids.add(review_id)
            if content:
                seen_content.add(content)
            unique_reviews.append(review)
        
        print(f"Removed {self.stats['removed_duplicates']} duplicate reviews")
        return unique_reviews
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of a text string.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en' for English)
        """
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"
    
    def is_spam(self, review: Dict) -> bool:
        """
        Detect spam reviews using heuristics.
        
        Args:
            review: Review dictionary
            
        Returns:
            True if review is likely spam
        """
        content = review.get("content", "").lower()
        
        # Check for spam keywords
        for keyword in self.spam_keywords:
            if keyword in content:
                return True
        
        # Check for excessive repetition
        words = content.split()
        if len(words) > 5:
            word_counts = Counter(words)
            max_count = max(word_counts.values())
            if max_count > len(words) * 0.5:  # If 50%+ of words are the same
                return True
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in content if c in string.punctuation) / max(len(content), 1)
        if special_char_ratio > 0.3:  # More than 30% special characters
            return True
        
        # Check for URL patterns
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        if url_pattern.search(content):
            return True
        
        return False
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by removing extra whitespace and special characters.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def clean_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """
        Apply all cleaning steps to the reviews.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            List of cleaned reviews
        """
        cleaned_reviews = []
        
        print("Starting data cleaning pipeline...")
        print(f"Target language: {self.target_language}")
        print(f"Min content length: {self.min_content_length}")
        print(f"Max content length: {self.max_content_length}")
        
        for review in reviews:
            content = review.get("content", "")
            
            # Check for empty content
            if not content or not content.strip():
                self.stats["removed_empty_content"] += 1
                continue
            
            # Check content length
            content_length = len(content.strip())
            if content_length < self.min_content_length:
                self.stats["removed_too_short"] += 1
                continue
            
            if content_length > self.max_content_length:
                self.stats["removed_too_long"] += 1
                continue
            
            # Check for spam
            if self.is_spam(review):
                self.stats["removed_spam"] += 1
                continue
            
            # Check language
            try:
                detected_lang = self.detect_language(content)
                if detected_lang != self.target_language:
                    self.stats["removed_non_english"] += 1
                    continue
            except:
                # If language detection fails, keep the review
                pass
            
            # Normalize text
            review["content"] = self.normalize_text(content)
            
            # Add cleaning metadata
            review["cleaned_at"] = datetime.now().isoformat()
            review["language_detected"] = detected_lang if 'detected_lang' in locals() else "unknown"
            
            cleaned_reviews.append(review)
        
        self.stats["final_count"] = len(cleaned_reviews)
        print(f"Cleaning complete. Final count: {len(cleaned_reviews)} reviews")
        
        return cleaned_reviews
    
    def save_cleaned_data(self, reviews: List[Dict], filename: str = None) -> str:
        """
        Save cleaned reviews to JSON file.
        
        Args:
            reviews: List of cleaned review dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spotify_reviews_cleaned_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(reviews)} cleaned reviews to {filepath}")
        return str(filepath)
    
    def print_statistics(self):
        """Print cleaning statistics."""
        print("\n" + "="*50)
        print("DATA CLEANING STATISTICS")
        print("="*50)
        print(f"Total reviews (input):     {self.stats['total_reviews']}")
        print(f"Removed duplicates:        {self.stats['removed_duplicates']}")
        print(f"Removed spam:              {self.stats['removed_spam']}")
        print(f"Removed (too short):       {self.stats['removed_too_short']}")
        print(f"Removed (too long):        {self.stats['removed_too_long']}")
        print(f"Removed (non-English):    {self.stats['removed_non_english']}")
        print(f"Removed (empty content):   {self.stats['removed_empty_content']}")
        print("-" * 50)
        print(f"Total removed:             {sum(self.stats[k] for k in ['removed_duplicates', 'removed_spam', 'removed_too_short', 'removed_too_long', 'removed_non_english', 'removed_empty_content'])}")
        print(f"Final reviews (output):    {self.stats['final_count']}")
        print(f"Retention rate:            {(self.stats['final_count'] / self.stats['total_reviews'] * 100):.2f}%")
        print("="*50 + "\n")
    
    def save_statistics(self, filename: str = None):
        """
        Save cleaning statistics to JSON file.
        
        Args:
            filename: Optional custom filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cleaning_stats_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"Saved statistics to {filepath}")


def main():
    """Main execution function."""
    # Initialize pipeline
    pipeline = DataCleaningPipeline(
        input_dir="../phase1-data-collection/data/raw",
        output_dir="data/processed"
    )
    
    try:
        # Load raw data
        reviews = pipeline.load_raw_data()
        
        # Remove duplicates
        reviews = pipeline.remove_duplicates(reviews)
        
        # Clean reviews
        cleaned_reviews = pipeline.clean_reviews(reviews)
        
        # Save cleaned data
        pipeline.save_cleaned_data(cleaned_reviews)
        
        # Print and save statistics
        pipeline.print_statistics()
        pipeline.save_statistics()
        
        print("\nData cleaning pipeline completed successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure Phase 1 has been completed and raw data is available.")
    except Exception as e:
        print(f"Error during cleaning: {e}")
        raise


if __name__ == "__main__":
    main()
