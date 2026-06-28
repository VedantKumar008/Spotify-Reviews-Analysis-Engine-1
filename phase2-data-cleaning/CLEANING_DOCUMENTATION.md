# Data Cleaning Documentation

## Phase 2: Data Preprocessing & Cleaning

### Overview
This document describes the data cleaning pipeline used to process raw Spotify review data from Google Play Store.

---

## Cleaning Pipeline Steps

### 1. Duplicate Removal
**Objective**: Remove duplicate reviews based on review ID and content.

**Method**:
- Check for duplicate `review_id` values
- Check for duplicate content (case-insensitive)
- Keep first occurrence, remove subsequent duplicates

**Rationale**: Duplicate reviews can skew analysis results and inflate metrics.

---

### 2. Spam Detection
**Objective**: Identify and remove spam or low-quality reviews.

**Detection Methods**:
- **Keyword Matching**: Reviews containing spam keywords (free, download, hack, crack, premium, mod, click here, visit, subscribe, follow, link)
- **Repetition Detection**: Reviews where 50%+ of words are identical
- **Special Character Ratio**: Reviews with >30% special characters
- **URL Detection**: Reviews containing HTTP/HTTPS URLs

**Spam Keywords List**:
```
free, download, hack, crack, premium, mod, click here, visit, subscribe, follow, link
```

**Rationale**: Spam reviews don't provide genuine user feedback and can bias analysis.

---

### 3. Content Length Filtering
**Objective**: Remove reviews that are too short or too long.

**Thresholds**:
- **Minimum length**: 10 characters
- **Maximum length**: 5,000 characters

**Rationale**:
- Too short: Likely low-value content (e.g., "Good", "Bad")
- Too long: May be automated or contain excessive text that's not representative

---

### 4. Language Detection
**Objective**: Filter non-English reviews to ensure consistent analysis.

**Method**:
- Use `langdetect` library to detect review language
- Keep only reviews detected as English (`en`)
- If language detection fails, keep the review (fail-safe)

**Rationale**: The analysis focuses on English-speaking users for consistency.

---

### 5. Empty Content Removal
**Objective**: Remove reviews with no text content.

**Method**:
- Check if `content` field is empty or contains only whitespace
- Remove reviews without meaningful text

**Rationale**: Reviews without text cannot be analyzed for insights.

---

### 6. Text Normalization
**Objective**: Standardize text format for consistent processing.

**Method**:
- Remove extra whitespace (multiple spaces, tabs, newlines)
- Trim leading/trailing whitespace
- Preserve original case (for sentiment analysis in later phases)

**Rationale**: Normalized text improves downstream processing and analysis.

---

## Cleaning Parameters

### Default Configuration
```python
min_content_length = 10
max_content_length = 5000
target_language = "en"
spam_keywords = [
    "free", "download", "hack", "crack", "premium", "mod",
    "click here", "visit", "subscribe", "follow", "link"
]
```

### Customization
Parameters can be modified in `data_cleaning.py`:
```python
pipeline = DataCleaningPipeline(
    input_dir="../phase1-data-collection/data/raw",
    output_dir="data/processed"
)

# Modify parameters
pipeline.min_content_length = 15
pipeline.max_content_length = 3000
pipeline.target_language = "en"
```

---

## Data Quality Metrics

### Metrics Calculated
- **Total reviews**: Input count
- **Removed duplicates**: Count of duplicate reviews removed
- **Removed spam**: Count of spam reviews removed
- **Removed (too short)**: Count of reviews below minimum length
- **Removed (too long)**: Count of reviews above maximum length
- **Removed (non-English)**: Count of non-English reviews removed
- **Removed (empty content)**: Count of empty reviews removed
- **Final count**: Output count after cleaning
- **Retention rate**: Percentage of reviews retained

### Additional Metrics (via data_quality_metrics.py)
- Basic metrics (total, unique IDs, unique users)
- Content metrics (avg, min, max, median length)
- Rating distribution
- Language distribution
- App version distribution
- Field completeness

---

## Output Format

### Cleaned Review Schema
```json
{
  "review_id": "string",
  "user_name": "string",
  "user_image": "string",
  "content": "string (normalized)",
  "score": "integer",
  "thumbs_up_count": "integer",
  "review_created_version": "string",
  "at": "string (ISO 8601)",
  "reply_content": "string or null",
  "replied_at": "string (ISO 8601) or null",
  "app_version": "string",
  "collected_at": "string (ISO 8601)",
  "cleaned_at": "string (ISO 8601)",
  "language_detected": "string"
}
```

### Additional Fields
- `cleaned_at`: Timestamp when cleaning was performed
- `language_detected`: Detected language code (e.g., "en")

---

## File Naming Convention

### Cleaned Data Files
- Format: `spotify_reviews_cleaned_YYYYMMDD_HHMMSS.json`
- Example: `spotify_reviews_cleaned_20240622_230000.json`
- Location: `data/processed/`

### Statistics Files
- Format: `cleaning_stats_YYYYMMDD_HHMMSS.json`
- Example: `cleaning_stats_20240622_230000.json`
- Location: `data/processed/`

### Quality Report Files
- Format: `data_quality_report_YYYYMMDD_HHMMSS.json`
- Example: `data_quality_report_20240622_230000.json`
- Location: `data/processed/`

---

## Expected Retention Rate

Based on typical Google Play Store review data:
- **Expected retention**: 60-80% of original data
- **Primary removals**: Duplicates (5-10%), Spam (5-15%), Non-English (10-20%), Too short (5-10%)

**Example**: 10,000 raw reviews → 6,000-8,000 cleaned reviews

---

## Performance Considerations

### Processing Time
- **10,000 reviews**: ~30-60 seconds
- **Bottleneck**: Language detection (most time-consuming)
- **Optimization**: Can skip language detection if not needed

### Memory Usage
- **10,000 reviews**: ~50-100 MB RAM
- **Scaling**: Linear memory growth with dataset size

### Caching
- Processed dataset is cached in `data/processed/`
- Reuse cleaned dataset for Phase 3 (LLM Analysis)
- Avoid re-cleaning on subsequent runs

---

## Error Handling

### Common Issues
1. **Missing input data**: Ensure Phase 1 completed successfully
2. **Language detection failure**: Reviews kept as fail-safe
3. **Encoding issues**: UTF-8 encoding used throughout
4. **Memory issues**: Process in batches for very large datasets

### Logging
- Statistics printed to console
- Detailed statistics saved to JSON file
- Error messages indicate specific failure points

---

## Integration with Other Phases

### Phase 1 (Data Collection)
- Input: Raw reviews from `phase1-data-collection/data/raw/`
- Automatically detects most recent file if not specified

### Phase 3 (LLM Analysis)
- Output: Cleaned reviews in `data/processed/`
- Used as input for AI analysis
- Cached to avoid re-cleaning

### Phase 4 (Backend API)
- Cleaned dataset loaded by API for analysis
- Statistics exposed via API endpoints

---

## Validation

### Manual Validation Steps
1. Check retention rate is within expected range (60-80%)
2. Verify no duplicate review IDs in output
3. Spot-check content normalization
4. Verify language distribution (mostly English)
5. Check rating distribution is reasonable

### Automated Validation
- Run `data_quality_metrics.py` to generate quality report
- Review completeness metrics (should be >90% for key fields)
- Check for anomalies in distributions

---

## Troubleshooting

### Low Retention Rate
- **Cause**: Aggressive filtering parameters
- **Solution**: Adjust thresholds (min/max length, spam keywords)

### High Non-English Removal
- **Cause**: Strict language detection
- **Solution**: Relax language filter or improve detection accuracy

### Processing Too Slow
- **Cause**: Language detection on large dataset
- **Solution**: Skip language detection or use faster method

### Missing Reviews After Cleaning
- **Cause**: All reviews filtered out
- **Solution**: Review filtering criteria and adjust parameters

---

## Future Improvements

### Potential Enhancements
1. **Advanced spam detection**: Use ML models instead of heuristics
2. **Sentiment pre-filtering**: Remove extremely positive/negative outliers
3. **Topic modeling**: Group reviews by topic before analysis
4. **User segmentation**: Identify and analyze different user groups
5. **Time-based filtering**: Focus on recent reviews only

### Scalability
- Implement parallel processing for large datasets
- Use database instead of JSON for better performance
- Add incremental cleaning (only process new reviews)
