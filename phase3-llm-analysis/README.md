# Phase 3: LLM Integration & Analysis

## Overview
This phase implements the LLM analysis component using Groq API to generate insights from cleaned Spotify review data. It analyzes six predefined research questions to extract actionable product insights.

## Components

### Files
- `llm_analysis.py` - Main LLM analysis script with Groq integration
- `requirements.txt` - Python dependencies
- `LLM_DOCUMENTATION.md` - Detailed LLM analysis documentation
- `data/results/` - Directory for storing analysis results
- `data/cache/` - Directory for caching LLM responses

## Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Groq API key
- Completed Phase 2 (cleaned data available)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### API Key Setup
Set your Groq API key as an environment variable:
```bash
# On Linux/Mac
export GROQ_API_KEY="your-groq-api-key"

# On Windows (PowerShell)
$env:GROQ_API_KEY="your-groq-api-key"

# On Windows (Command Prompt)
set GROQ_API_KEY=your-groq-api-key
```

Get your API key from: https://console.groq.com/

## Usage

### Basic Usage
```bash
# Run the LLM analysis
python llm_analysis.py
```

### Custom Configuration
Modify parameters in `llm_analysis.py`:

```python
analyzer = GroqAnalyzer(
    model="llama3-70b-8192",  # or "llama3-8b-8192" for faster inference
    input_dir="../phase2-data-cleaning/data/processed",
    output_dir="data/results",
    cache_dir="data/cache"
)

results = analyzer.analyze_all_questions(
    reviews,
    use_cache=True,
    sample_size=100  # Number of reviews per question
)
```

## Research Questions

The system analyzes six predefined research questions:

1. Why do users struggle to discover new music?
2. What are the most common frustrations with recommendations?
3. What listening behaviors are users trying to achieve?
4. What causes users to repeatedly listen to the same content?
5. Which user segments experience different discovery challenges?
6. What unmet needs emerge consistently across reviews?

## Features

- **Groq Integration**: Uses Groq API for fast LLM inference
- **Prompt Engineering**: Optimized prompts for product insights
- **Caching**: Intelligent caching to reduce API costs and improve speed
- **Retry Logic**: Automatic retry with exponential backoff for API failures
- **Token Tracking**: Monitors token usage for cost estimation
- **Batch Processing**: Processes reviews in configurable batches
- **Error Handling**: Graceful handling of API errors and failures

## Output

### Generated Files
- `analysis_results_YYYYMMDD_HHMMSS.json` - Complete analysis results with all answers
- Cache files in `data/cache/` - Cached LLM responses for reuse

### Results Format
```json
{
  "generated_at": "2024-06-22T23:30:00",
  "model_used": "llama3-70b-8192",
  "statistics": {
    "total_reviews_analyzed": 6000,
    "total_api_calls": 6,
    "cache_hits": 0,
    "cache_misses": 6,
    "total_tokens_used": 15000,
    "analysis_time_seconds": 45.5
  },
  "results": {
    "q1": {
      "question": "Why do users struggle to discover new music?",
      "answer": "Users struggle with discovery due to...",
      "cached": false,
      "reviews_analyzed": 100
    },
    ...
  }
}
```

## Performance

### Expected Performance
- **6 questions**: ~30-60 seconds total
- **Per question**: ~5-10 seconds
- **With cache**: <1 second (if cached)

### Cost Estimation
- **Llama3-70b**: ~$0.01 per analysis
- **Llama3-8b**: ~$0.001 per analysis
- **With caching**: Near-zero cost after first run

## Models

### Available Groq Models
- `llama3-70b-8192` - Best quality, slower (recommended)
- `llama3-8b-8192` - Faster, less accurate
- `mixtral-8x7b-32768` - Alternative with larger context

### Model Selection
Choose based on your needs:
- **Quality**: Use `llama3-70b-8192`
- **Speed**: Use `llama3-8b-8192`
- **Large context**: Use `mixtral-8x7b-32768`

## Caching

### How Caching Works
- Cache key generated from question + review sample
- Responses saved to `data/cache/`
- Subsequent runs use cached responses
- Reduces API costs and improves speed

### Cache Management
```bash
# Clear cache
rm -rf data/cache/*

# View cache files
ls data/cache/
```

## Troubleshooting

### API Key Issues
```
ValueError: Groq API key required
```
**Solution**: Set `GROQ_API_KEY` environment variable

### Import Errors
```
groq package not installed
```
**Solution**: Run `pip install -r requirements.txt`

### Missing Input Data
```
FileNotFoundError: No cleaned data files found
```
**Solution**: Ensure Phase 2 has been completed successfully

### Slow Performance
**Cause**: Network latency or model inference time
**Solution**: Use smaller model (`llama3-8b-8192`) or reduce sample size

### Poor Quality Answers
**Cause**: Prompt design or insufficient review context
**Solution**: Adjust prompts in `llm_analysis.py` or increase sample size

## Integration

### Input
- Cleaned reviews from `phase2-data-cleaning/data/processed/`
- Automatically detects most recent file

### Output
- Analysis results in `data/results/`
- Used as input for Phase 4 (Backend API)

## Best Practices

1. **Always use caching** to reduce costs and improve speed
2. **Review answers** before deploying to production
3. **Monitor token usage** to control costs
4. **Test with sample data** before full analysis
5. **Keep API keys secure** using environment variables
6. **Handle errors gracefully** with built-in retry logic

## Next Steps

After LLM analysis:
1. Review generated answers for quality and relevance
2. Verify answers are based on review data
3. Proceed to **Phase 4: Backend API Development**
4. Integrate analysis results into API endpoints

## Documentation

For detailed information about LLM integration, prompt engineering, and configuration, see `LLM_DOCUMENTATION.md`.

## Notes

- Uses Groq API for fast, cost-effective LLM inference
- Default model is `llama3-70b-8192` for best quality
- Caching significantly reduces costs on subsequent runs
- Answers are limited to 3-4 lines per research question
- Focus on product insights rather than technical analysis
