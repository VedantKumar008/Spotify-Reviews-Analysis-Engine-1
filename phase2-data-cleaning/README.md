# Phase 2: Data Preprocessing & Cleaning

## Overview
This phase implements the data cleaning pipeline for the Spotify Reviews Analysis Engine. It processes raw review data from Phase 1 to remove noise, duplicates, spam, and low-value content.

## Components

### Files
- `data_cleaning.py` - Main data cleaning pipeline script
- `data_quality_metrics.py` - Data quality metrics calculator
- `requirements.txt` - Python dependencies
- `CLEANING_DOCUMENTATION.md` - Detailed cleaning process documentation
- `data/processed/` - Directory for storing cleaned data

## Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Completed Phase 1 (raw data available)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Run the data cleaning pipeline
python data_cleaning.py
```

### Generate Quality Metrics
```bash
# Generate data quality report
python data_quality_metrics.py
```

### Custom Configuration
Modify parameters in `data_cleaning.py`:

```python
pipeline = DataCleaningPipeline(
    input_dir="../phase1-data-collection/data/raw",
    output_dir="data/processed"
)

# Adjust cleaning parameters
pipeline.min_content_length = 10
pipeline.max_content_length = 5000
pipeline.target_language = "en"
```

## Cleaning Process

The pipeline applies the following steps in order:

1. **Duplicate Removal** - Removes duplicate reviews based on ID and content
2. **Spam Detection** - Filters spam using keywords, repetition, and URL patterns
3. **Content Length Filtering** - Removes reviews too short (<10 chars) or too long (>5000 chars)
4. **Language Detection** - Keeps only English reviews
5. **Empty Content Removal** - Removes reviews without text
6. **Text Normalization** - Standardizes whitespace and formatting

## Output

### Generated Files
- `spotify_reviews_cleaned_YYYYMMDD_HHMMSS.json` - Cleaned review data
- `cleaning_stats_YYYYMMDD_HHMMSS.json` - Cleaning statistics
- `data_quality_report_YYYYMMDD_HHMMSS.json` - Quality metrics report

### Statistics
The pipeline tracks and reports:
- Total reviews (input)
- Removed duplicates
- Removed spam
- Removed (too short)
- Removed (too long)
- Removed (non-English)
- Removed (empty content)
- Final count (output)
- Retention rate

## Expected Results

### Retention Rate
- **Expected**: 60-80% of original data retained
- **Example**: 10,000 raw reviews → 6,000-8,000 cleaned reviews

### Processing Time
- **10,000 reviews**: ~30-60 seconds
- Bottleneck: Language detection

## Features

- **Configurable Parameters**: Adjust filtering thresholds as needed
- **Comprehensive Statistics**: Track what was removed and why
- **Quality Metrics**: Generate detailed quality reports
- **Error Handling**: Graceful handling of edge cases
- **Caching**: Cleaned data cached for reuse in Phase 3

## Data Quality Metrics

The `data_quality_metrics.py` script provides:

- Basic metrics (total, unique IDs, unique users)
- Content metrics (avg, min, max, median length)
- Rating distribution
- Language distribution
- App version distribution
- Field completeness

## Integration

### Input
- Raw reviews from `phase1-data-collection/data/raw/`
- Automatically detects most recent file

### Output
- Cleaned reviews in `data/processed/`
- Used as input for Phase 3 (LLM Analysis)

## Troubleshooting

### Missing Input Data
```
Error: No raw data files found in ../phase1-data-collection/data/raw
```
**Solution**: Ensure Phase 1 has been completed successfully.

### Low Retention Rate
**Cause**: Aggressive filtering parameters
**Solution**: Adjust thresholds in `data_cleaning.py`

### Import Errors
```
Error: Required packages not installed
```
**Solution**: Run `pip install -r requirements.txt`

### Processing Too Slow
**Cause**: Language detection on large dataset
**Solution**: Skip language detection or use smaller dataset

## Next Steps

After data cleaning:
1. Review cleaning statistics and quality metrics
2. Verify retention rate is within expected range
3. Proceed to **Phase 3: LLM Integration & Analysis**
4. Use cleaned dataset for AI-powered analysis

## Documentation

For detailed information about the cleaning process, see `CLEANING_DOCUMENTATION.md`.

## Notes

- The pipeline uses the `langdetect` library for language detection
- Spam detection uses heuristic methods (keywords, patterns)
- Text normalization preserves original case for sentiment analysis
- Cleaned data is cached to avoid re-processing
