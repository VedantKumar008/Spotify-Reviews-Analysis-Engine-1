# Phase 1: Data Collection & Storage

## Overview
This phase implements the data collection component for the Spotify Reviews Analysis Engine. It collects real Spotify reviews from the Google Play Store.

## Components

### Files
- `data_collection.py` - Main script for collecting reviews
- `requirements.txt` - Python dependencies
- `DATA_SCHEMA.md` - Data schema documentation
- `data/raw/` - Directory for storing raw review data

## Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Run the data collection script
python data_collection.py
```

### Custom Configuration
You can modify the parameters in the `main()` function of `data_collection.py`:

```python
collector = SpotifyReviewCollector(
    package_name="com.spotify.music",
    output_dir="data/raw"
)

reviews = collector.collect_reviews(
    target_count=10000,        # Number of reviews to collect
    batch_size=100,            # Reviews per batch
    sort_by=Sort.NEWEST,      # Sort order (NEWEST, RATING, etc.)
    sleep_between_batches=1.0  # Delay between batches (seconds)
)
```

## Output

### Generated Files
- `spotify_reviews_raw_YYYYMMDD_HHMMSS.json` - Raw review data
- App information is printed to console

### Data Format
Reviews are stored in JSON format with the following structure:
- `review_id` - Unique identifier
- `user_name` - Reviewer's display name
- `content` - Review text
- `score` - Rating (1-5)
- `at` - Timestamp of review
- And more (see DATA_SCHEMA.md for full schema)

## Features

- **Batch Collection**: Collects reviews in configurable batches
- **Rate Limiting**: Built-in delays to avoid API rate limits
- **Error Handling**: Graceful handling of errors during collection
- **Timestamp Tracking**: Records when data was collected
- **Incremental Collection**: Supports continuation tokens for large datasets

## Data Quality

The collected data may include:
- Duplicate reviews
- Non-English content
- Spam or low-quality reviews
- Empty reviews (rating only)

These issues will be addressed in **Phase 2: Data Preprocessing & Cleaning**

## Notes

- The script uses the `google-play-scraper` library to access Google Play Store data
- Collection time depends on network speed and rate limiting
- Target is ~10,000 reviews, but actual count may vary based on availability
- Reviews are sorted by newest first to prioritize recency

## Next Steps

After data collection:
1. Review the collected data in `data/raw/`
2. Proceed to **Phase 2: Data Preprocessing & Cleaning**
3. Clean the dataset to remove noise, duplicates, and spam

## Troubleshooting

### Import Error
If you get an import error for `google-play-scraper`:
```bash
pip install google-play-scraper
```

### No Reviews Collected
- Check your internet connection
- Verify the package name is correct
- Try reducing `sleep_between_batches` if rate limiting is too aggressive

### Slow Collection
- Increase `batch_size` to fetch more reviews per request
- Reduce `sleep_between_batches` (but be careful of rate limits)
