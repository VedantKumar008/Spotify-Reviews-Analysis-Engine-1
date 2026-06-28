"""
Deterministic analyzer for processing reviews without LLM calls.
Uses NLP libraries for keyword extraction, sentiment analysis, and pattern detection.
"""

from typing import List, Dict, Any
import re
from collections import Counter
from textblob import TextBlob
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    from vaderSentiment import SentimentIntensityAnalyzer
import spacy

class DeterministicAnalyzer:
    """Process reviews deterministically without LLM calls."""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Common Spotify-related keywords and phrases
        self.spotify_keywords = {
            'discovery': ['discover', 'recommend', 'suggestion', 'new music', 'find songs', 'explore'],
            'recommendation': ['recommend', 'algorithm', 'playlist', 'radio', 'daily mix'],
            'interface': ['ui', 'design', 'layout', 'navigation', 'menu', 'button'],
            'pricing': ['price', 'cost', 'subscription', 'premium', 'free', 'ad'],
            'playback': ['play', 'pause', 'skip', 'buffer', 'loading', 'quality', 'sound'],
            'offline': ['offline', 'download', 'save', 'cache', 'no internet'],
            'social': ['friend', 'share', 'social', 'collaborative', 'playlist'],
            'search': ['search', 'find', 'look for', 'filter']
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        if self.nlp:
            doc = self.nlp(text.lower())
            # Extract nouns and adjectives, filter stop words
            keywords = [
                token.text for token in doc 
                if (token.pos_ in ['NOUN', 'ADJ'] and not token.is_stop and len(token.text) > 2)
            ]
        else:
            # Fallback: simple word extraction
            words = re.findall(r'\b[a-z]{3,}\b', text.lower())
            keywords = [w for w in words if w not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been']]
        
        return keywords[:20]  # Return top 20 keywords
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER."""
        scores = self.sentiment_analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
    
    def detect_themes(self, text: str) -> Dict[str, int]:
        """Detect Spotify-related themes in text."""
        text_lower = text.lower()
        themes = {}
        
        for theme, keywords in self.spotify_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                themes[theme] = count
        
        return themes
    
    def extract_patterns(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Extract patterns from a batch of reviews."""
        all_keywords = []
        all_themes = Counter()
        sentiment_scores = []
        
        for review in reviews:
            content = review.get('content', '')
            score = review.get('score', 0)
            
            # Extract keywords
            keywords = self.extract_keywords(content)
            all_keywords.extend(keywords)
            
            # Detect themes
            themes = self.detect_themes(content)
            for theme, count in themes.items():
                all_themes[theme] += count
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(content)
            sentiment_scores.append({
                'compound': sentiment['compound'],
                'rating': score
            })
        
        # Aggregate results
        top_keywords = Counter(all_keywords).most_common(15)
        avg_sentiment = sum(s['compound'] for s in sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        return {
            'top_keywords': [{'keyword': k, 'count': c} for k, c in top_keywords],
            'themes': dict(all_themes.most_common()),
            'avg_sentiment': avg_sentiment,
            'review_count': len(reviews)
        }
    
    def process_batch(self, reviews: List[Dict], batch_id: int) -> Dict[str, Any]:
        """Process a batch of reviews deterministically."""
        patterns = self.extract_patterns(reviews)
        
        return {
            'batch_id': batch_id,
            'patterns': patterns,
            'review_count': len(reviews)
        }
