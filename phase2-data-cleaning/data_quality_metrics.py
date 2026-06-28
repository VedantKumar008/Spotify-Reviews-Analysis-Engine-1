"""
Data Quality Metrics Module for Spotify Reviews
Phase 2: Data Preprocessing & Cleaning
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    print("Optional packages not installed. Install with: pip install pandas matplotlib")


class DataQualityMetrics:
    """Calculate and report data quality metrics for review datasets."""
    
    def __init__(self, data_dir: str = "data/processed"):
        """
        Initialize the data quality metrics calculator.
        
        Args:
            data_dir: Directory containing review data files
        """
        self.data_dir = Path(data_dir)
    
    def load_data(self, filepath: str = None) -> List[Dict]:
        """
        Load review data from JSON file.
        
        Args:
            filepath: Path to data file. If None, uses the most recent file.
            
        Returns:
            List of review dictionaries
        """
        if filepath is None:
            files = list(self.data_dir.glob("spotify_reviews_*.json"))
            if not files:
                raise FileNotFoundError(f"No review files found in {self.data_dir}")
            filepath = max(files, key=lambda f: f.stat().st_mtime)
            print(f"Loading data from: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        
        return reviews
    
    def calculate_basic_metrics(self, reviews: List[Dict]) -> Dict:
        """
        Calculate basic data quality metrics.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "total_reviews": len(reviews),
            "unique_review_ids": len(set(r.get("review_id") for r in reviews if r.get("review_id"))),
            "unique_users": len(set(r.get("user_name") for r in reviews if r.get("user_name"))),
            "reviews_with_content": sum(1 for r in reviews if r.get("content") and r.get("content").strip()),
            "reviews_with_rating": sum(1 for r in reviews if r.get("score")),
            "reviews_with_reply": sum(1 for r in reviews if r.get("reply_content")),
        }
        
        return metrics
    
    def calculate_content_metrics(self, reviews: List[Dict]) -> Dict:
        """
        Calculate content-related metrics.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary of content metrics
        """
        content_lengths = [len(r.get("content", "")) for r in reviews if r.get("content")]
        
        if content_lengths:
            metrics = {
                "avg_content_length": sum(content_lengths) / len(content_lengths),
                "min_content_length": min(content_lengths),
                "max_content_length": max(content_lengths),
                "median_content_length": sorted(content_lengths)[len(content_lengths) // 2],
            }
        else:
            metrics = {
                "avg_content_length": 0,
                "min_content_length": 0,
                "max_content_length": 0,
                "median_content_length": 0,
            }
        
        return metrics
    
    def calculate_rating_metrics(self, reviews: List[Dict]) -> Dict:
        """
        Calculate rating distribution metrics.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary of rating metrics
        """
        ratings = [r.get("score") for r in reviews if r.get("score")]
        
        if ratings:
            rating_counts = Counter(ratings)
            metrics = {
                "avg_rating": sum(ratings) / len(ratings),
                "rating_distribution": dict(rating_counts),
                "total_rated_reviews": len(ratings),
            }
        else:
            metrics = {
                "avg_rating": 0,
                "rating_distribution": {},
                "total_rated_reviews": 0,
            }
        
        return metrics
    
    def calculate_language_metrics(self, reviews: List[Dict]) -> Dict:
        """
        Calculate language distribution metrics.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary of language metrics
        """
        languages = [r.get("language_detected") for r in reviews if r.get("language_detected")]
        
        if languages:
            lang_counts = Counter(languages)
            metrics = {
                "language_distribution": dict(lang_counts),
                "total_detected_languages": len(lang_counts),
            }
        else:
            metrics = {
                "language_distribution": {},
                "total_detected_languages": 0,
            }
        
        return metrics
    
    def calculate_version_metrics(self, reviews: List[Dict]) -> Dict:
        """
        Calculate app version distribution metrics.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary of version metrics
        """
        versions = [r.get("review_created_version") for r in reviews if r.get("review_created_version")]
        
        if versions:
            version_counts = Counter(versions)
            metrics = {
                "version_distribution": dict(version_counts.most_common(10)),
                "total_unique_versions": len(version_counts),
            }
        else:
            metrics = {
                "version_distribution": {},
                "total_unique_versions": 0,
            }
        
        return metrics
    
    def calculate_completeness_metrics(self, reviews: List[Dict]) -> Dict:
        """
        Calculate field completeness metrics.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary of completeness metrics
        """
        fields = [
            "review_id", "user_name", "content", "score", 
            "review_created_version", "at", "app_version"
        ]
        
        completeness = {}
        for field in fields:
            filled = sum(1 for r in reviews if r.get(field))
            completeness[field] = {
                "filled": filled,
                "missing": len(reviews) - filled,
                "completeness_percentage": (filled / len(reviews) * 100) if reviews else 0
            }
        
        return completeness
    
    def generate_report(self, reviews: List[Dict]) -> Dict:
        """
        Generate comprehensive data quality report.
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Dictionary containing all metrics
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "basic_metrics": self.calculate_basic_metrics(reviews),
            "content_metrics": self.calculate_content_metrics(reviews),
            "rating_metrics": self.calculate_rating_metrics(reviews),
            "language_metrics": self.calculate_language_metrics(reviews),
            "version_metrics": self.calculate_version_metrics(reviews),
            "completeness_metrics": self.calculate_completeness_metrics(reviews),
        }
        
        return report
    
    def print_report(self, report: Dict):
        """
        Print data quality report in a readable format.
        
        Args:
            report: Data quality report dictionary
        """
        print("\n" + "="*60)
        print("DATA QUALITY REPORT")
        print("="*60)
        
        # Basic Metrics
        print("\n[BASIC METRICS]")
        basic = report["basic_metrics"]
        print(f"Total reviews:              {basic['total_reviews']}")
        print(f"Unique review IDs:          {basic['unique_review_ids']}")
        print(f"Unique users:               {basic['unique_users']}")
        print(f"Reviews with content:       {basic['reviews_with_content']}")
        print(f"Reviews with rating:        {basic['reviews_with_rating']}")
        print(f"Reviews with reply:         {basic['reviews_with_reply']}")
        
        # Content Metrics
        print("\n[CONTENT METRICS]")
        content = report["content_metrics"]
        print(f"Average content length:     {content['avg_content_length']:.2f} chars")
        print(f"Min content length:         {content['min_content_length']} chars")
        print(f"Max content length:         {content['max_content_length']} chars")
        print(f"Median content length:      {content['median_content_length']} chars")
        
        # Rating Metrics
        print("\n[RATING METRICS]")
        rating = report["rating_metrics"]
        print(f"Average rating:             {rating['avg_rating']:.2f}")
        print(f"Total rated reviews:        {rating['total_rated_reviews']}")
        print("Rating distribution:")
        for score, count in sorted(rating['rating_distribution'].items()):
            print(f"  {score} stars: {count} reviews")
        
        # Language Metrics
        print("\n[LANGUAGE METRICS]")
        lang = report["language_metrics"]
        print(f"Total detected languages:   {lang['total_detected_languages']}")
        print("Language distribution:")
        for language, count in sorted(lang['language_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {language}: {count} reviews")
        
        # Version Metrics
        print("\n[VERSION METRICS]")
        version = report["version_metrics"]
        print(f"Total unique versions:      {version['total_unique_versions']}")
        print("Top 10 versions:")
        for ver, count in version['version_distribution'].items():
            print(f"  {ver}: {count} reviews")
        
        # Completeness Metrics
        print("\n[FIELD COMPLETENESS]")
        completeness = report["completeness_metrics"]
        for field, metrics in completeness.items():
            print(f"  {field}: {metrics['completeness_percentage']:.1f}% complete")
        
        print("\n" + "="*60 + "\n")
    
    def save_report(self, report: Dict, filename: str = None):
        """
        Save data quality report to JSON file.
        
        Args:
            report: Data quality report dictionary
            filename: Optional custom filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_quality_report_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Saved data quality report to {filepath}")


def main():
    """Main execution function."""
    # Initialize metrics calculator
    calculator = DataQualityMetrics(data_dir="data/processed")
    
    try:
        # Load data
        reviews = calculator.load_data()
        
        # Generate report
        report = calculator.generate_report(reviews)
        
        # Print report
        calculator.print_report(report)
        
        # Save report
        calculator.save_report(report)
        
        print("Data quality metrics generated successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure data is available in the specified directory.")
    except Exception as e:
        print(f"Error generating metrics: {e}")
        raise


if __name__ == "__main__":
    main()
