"""
Data Collection Script for Spotify Reviews from Google Play Store
Phase 1: Data Collection & Storage
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from google_play_scraper import app, reviews, Sort
except ImportError:
    print("google-play-scraper not installed. Install with: pip install google-play-scraper")
    exit(1)


class SpotifyReviewCollector:
    """Collects Spotify reviews from Google Play Store."""
    
    def __init__(self, package_name: str = "com.spotify.music", output_dir: str = "data/raw"):
        """
        Initialize the review collector.
        
        Args:
            package_name: Spotify package name on Google Play
            output_dir: Directory to store raw data
        """
        self.package_name = package_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_reviews(
        self,
        target_count: int = 10000,
        batch_size: int = 100,
        sort_by: Sort = Sort.NEWEST,
        sleep_between_batches: float = 1.0
    ) -> List[Dict]:
        """
        Collect reviews from Google Play Store.
        
        Args:
            target_count: Target number of reviews to collect
            batch_size: Number of reviews per batch
            sort_by: Sort order (NEWEST, RATING, etc.)
            sleep_between_batches: Sleep time between batches to avoid rate limiting
            
        Returns:
            List of review dictionaries
        """
        all_reviews = []
        continuation_token = None
        collected_count = 0
        
        print(f"Starting collection of {target_count} reviews...")
        print(f"Package: {self.package_name}")
        print(f"Sort by: {sort_by}")
        
        while collected_count < target_count:
            try:
                # Fetch reviews in batches
                result, continuation_token = reviews(
                    self.package_name,
                    count=batch_size,
                    sort=sort_by,
                    continuation_token=continuation_token
                )
                
                if not result:
                    print("No more reviews available.")
                    break
                
                # Process and add reviews
                processed_reviews = self._process_reviews(result)
                all_reviews.extend(processed_reviews)
                collected_count += len(processed_reviews)
                
                print(f"Collected {collected_count}/{target_count} reviews...")
                
                # Stop if we've reached target
                if collected_count >= target_count:
                    break
                
                # Stop if no continuation token
                if continuation_token is None:
                    print("Reached end of available reviews.")
                    break
                
                # Sleep to avoid rate limiting
                time.sleep(sleep_between_batches)
                
            except Exception as e:
                print(f"Error collecting reviews: {e}")
                print(f"Collected {collected_count} reviews before error.")
                break
        
        print(f"Collection complete. Total reviews: {len(all_reviews)}")
        return all_reviews
    
    def _process_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """
        Process and standardize review data.
        
        Args:
            reviews: Raw review data from Google Play scraper
            
        Returns:
            Processed review dictionaries
        """
        processed = []
        
        for review in reviews:
            processed_review = {
                "review_id": review.get("reviewId"),
                "user_name": review.get("userName"),
                "user_image": review.get("userImage"),
                "content": review.get("content"),
                "score": review.get("score"),
                "thumbs_up_count": review.get("thumbsUpCount"),
                "review_created_version": review.get("reviewCreatedVersion"),
                "at": review.get("at").isoformat() if review.get("at") else None,
                "reply_content": review.get("replyContent"),
                "replied_at": review.get("repliedAt").isoformat() if review.get("repliedAt") else None,
                "app_version": review.get("appVersion"),
                "collected_at": datetime.now().isoformat()
            }
            processed.append(processed_review)
        
        return processed
    
    def save_reviews(self, reviews: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save reviews to JSON file.
        
        Args:
            reviews: List of review dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spotify_reviews_raw_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(reviews)} reviews to {filepath}")
        return str(filepath)
    
    def get_app_info(self) -> Dict:
        """
        Get app information from Google Play Store.
        
        Returns:
            App information dictionary
        """
        try:
            app_info = app(self.package_name)
            return {
                "title": app_info.get("title"),
                "description": app_info.get("description"),
                "score": app_info.get("score"),
                "ratings": app_info.get("ratings"),
                "reviews": app_info.get("reviews"),
                "installs": app_info.get("installs"),
                "version": app_info.get("version"),
                "updated": app_info.get("updated"),
                "category": app_info.get("category"),
                "developer": app_info.get("developer")
            }
        except Exception as e:
            print(f"Error getting app info: {e}")
            return {}


def main():
    """Main execution function."""
    # Initialize collector
    collector = SpotifyReviewCollector(
        package_name="com.spotify.music",
        output_dir="data/raw"
    )
    
    # Get app info
    print("Fetching Spotify app information...")
    app_info = collector.get_app_info()
    print(f"App: {app_info.get('title')}")
    print(f"Version: {app_info.get('version')}")
    print(f"Rating: {app_info.get('score')}")
    print(f"Total reviews: {app_info.get('reviews')}")
    print()
    
    # Collect reviews
    reviews = collector.collect_reviews(
        target_count=10000,
        batch_size=100,
        sort_by=Sort.NEWEST,
        sleep_between_batches=1.0
    )
    
    # Save reviews
    if reviews:
        filepath = collector.save_reviews(reviews)
        print(f"\nData collection complete!")
        print(f"File saved to: {filepath}")
        print(f"Total reviews collected: {len(reviews)}")
    else:
        print("No reviews collected.")


if __name__ == "__main__":
    main()
