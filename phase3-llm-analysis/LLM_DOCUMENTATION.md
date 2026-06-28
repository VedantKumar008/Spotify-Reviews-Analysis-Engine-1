# LLM Analysis Documentation

## Phase 3: LLM Integration & Analysis

### Overview
This document describes the LLM analysis component that uses Groq API to generate insights from cleaned Spotify review data.

---

## LLM Provider: Groq

### Why Groq?
- **Fast inference**: Groq provides extremely fast LLM inference
- **Cost-effective**: Lower cost compared to traditional API providers
- **Open-source models**: Uses Llama models with excellent performance
- **High throughput**: Suitable for processing large datasets

### Model Selection
- **Primary model**: `llama3-70b-8192`
- **Alternative models**: `llama3-8b-8192` (faster, less accurate), `mixtral-8x7b-32768`
- **Context window**: 8192 tokens (sufficient for review analysis)

---

## Research Questions

The system analyzes six predefined research questions:

1. **Why do users struggle to discover new music?**
   - Focus: Discovery challenges, search issues, recommendation gaps

2. **What are the most common frustrations with recommendations?**
   - Focus: Algorithm issues, relevance problems, personalization

3. **What listening behaviors are users trying to achieve?**
   - Focus: User goals, listening patterns, use cases

4. **What causes users to repeatedly listen to the same content?**
   - Focus: Nostalgia, comfort, familiarity, mood-based listening

5. **Which user segments experience different discovery challenges?**
   - Focus: User demographics, experience levels, usage patterns

6. **What unmet needs emerge consistently across reviews?**
   - Focus: Feature requests, missing functionality, user desires

---

## Prompt Engineering

### System Prompt
```
You are a product insights analyst specializing in music streaming services. 
Your task is to analyze Spotify user reviews and extract actionable product insights.

Focus on:
- User pain points and frustrations
- User behaviors and preferences
- Unmet needs and feature requests
- Patterns across different user segments

Provide concise, data-driven insights (3-4 lines per answer) based on the review data.
Avoid technical jargon. Focus on clear product insights that can inform product decisions.
```

### User Prompt Structure
```
Based on the following Spotify user reviews, answer this research question:

RESEARCH QUESTION: [question]

USER REVIEWS:
[review 1]
[review 2]
...

Provide a concise answer (3-4 lines) based on the review data above.
Focus on clear product insights rather than technical analysis.
```

### Prompt Parameters
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Max tokens**: 500 (sufficient for 3-4 line answers)
- **Top P**: 1.0 (no nucleus sampling restriction)
- **Sample size**: 100 reviews per question (balances depth and token limits)

---

## Data Processing

### Review Sampling
- **Strategy**: Take first N reviews from cleaned dataset
- **Default sample size**: 100 reviews per question
- **Rationale**: Provides sufficient context while staying within token limits
- **Customization**: Can adjust `sample_size` parameter

### Token Management
- **Context window**: 8192 tokens
- **System prompt**: ~150 tokens
- **User prompt**: ~2000-4000 tokens (depending on review length)
- **Response**: ~100-200 tokens
- **Safety margin**: ~4000 tokens remaining

### Batch Processing
- **Sequential processing**: Questions analyzed one at a time
- **Parallel potential**: Can be parallelized for faster processing
- **Rate limiting**: Built-in retry logic with exponential backoff

---

## Caching Strategy

### Cache Key Generation
- **Components**: Question text + review sample content
- **Hash function**: MD5
- **Uniqueness**: Ensures different questions/samples have different keys

### Cache Storage
- **Location**: `data/cache/`
- **Format**: JSON files named `{cache_key}.json`
- **Content**: Response, timestamp, metadata

### Cache Benefits
- **Cost reduction**: Avoids redundant API calls
- **Speed improvement**: Cached responses return instantly
- **Consistency**: Same inputs produce same outputs
- **Debugging**: Can inspect cached responses

### Cache Metadata
```json
{
  "response": "LLM response text",
  "timestamp": "2024-06-22T23:30:00",
  "metadata": {
    "question": "Research question text",
    "reviews_count": 100,
    "model": "llama3-70b-8192"
  }
}
```

---

## API Integration

### Authentication
- **Method**: API key
- **Environment variable**: `GROQ_API_KEY`
- **Fallback**: Can pass `api_key` parameter directly

### Retry Logic
- **Max retries**: 3 attempts
- **Backoff strategy**: Exponential (2^attempt seconds)
- **Error handling**: Catches and reports API failures

### API Call Parameters
```python
response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.7,
    max_tokens=500,
    top_p=1,
    stream=False
)
```

### Token Tracking
- **Total tokens used**: Tracked across all API calls
- **Cost estimation**: Can calculate based on Groq pricing
- **Performance monitoring**: Helps optimize prompt design

---

## Response Format

### Individual Question Response
```json
{
  "question": "Research question text",
  "answer": "LLM-generated answer (3-4 lines)",
  "cached": false,
  "reviews_analyzed": 100
}
```

### Complete Results Structure
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
    "q1": { /* question 1 response */ },
    "q2": { /* question 2 response */ },
    ...
  }
}
```

---

## Performance Considerations

### Expected Performance
- **6 questions**: ~30-60 seconds total
- **Per question**: ~5-10 seconds
- **With cache**: <1 second (if cached)

### Bottlenecks
- **API latency**: Network latency to Groq servers
- **Model inference**: Model processing time
- **Token limits**: Large review samples may require batching

### Optimization Strategies
1. **Increase cache hit rate**: Reuse same review samples
2. **Reduce sample size**: Fewer reviews per question
3. **Use smaller model**: `llama3-8b-8192` for faster inference
4. **Parallel processing**: Analyze multiple questions simultaneously

---

## Error Handling

### Common Errors
1. **API key missing**: Set `GROQ_API_KEY` environment variable
2. **Rate limiting**: Built-in retry logic handles this
3. **Token limit exceeded**: Reduce sample size
4. **Network issues**: Retry logic with exponential backoff
5. **Invalid response**: Error message saved to results

### Error Recovery
- **Graceful degradation**: Failed questions marked with error message
- **Partial results**: Successful questions still saved
- **Retry mechanism**: Automatic retries for transient errors
- **Logging**: Detailed error messages for debugging

---

## Quality Assurance

### Answer Quality Checks
- **Length**: Should be 3-4 lines (enforced by prompt)
- **Relevance**: Should directly answer the research question
- **Data-driven**: Should reference review content
- **Actionable**: Should provide product insights

### Validation Steps
1. Review generated answers for consistency
2. Check that answers are based on review data
3. Verify answers are concise (3-4 lines)
4. Ensure no technical jargon
5. Confirm actionable insights

### Human Review
- **Recommended**: Review answers before deployment
- **Focus**: Accuracy, relevance, actionability
- **Iteration**: Adjust prompts if answers are unsatisfactory

---

## Integration with Other Phases

### Phase 2 (Data Cleaning)
- **Input**: Cleaned reviews from `phase2-data-cleaning/data/processed/`
- **Dependency**: Requires Phase 2 to be completed first
- **Format**: JSON file with cleaned review data

### Phase 4 (Backend API)
- **Output**: Analysis results in `data/results/`
- **Usage**: API loads and serves results to frontend
- **Caching**: Results cached for fast API responses

---

## Configuration

### Environment Variables
```bash
export GROQ_API_KEY="your-groq-api-key"
```

### Model Selection
```python
analyzer = GroqAnalyzer(
    model="llama3-70b-8192",  # or "llama3-8b-8192"
    ...
)
```

### Sampling Parameters
```python
results = analyzer.analyze_all_questions(
    reviews,
    use_cache=True,
    sample_size=100  # Adjust based on needs
)
```

---

## Cost Estimation

### Groq Pricing (as of 2024)
- **Llama3-70b**: ~$0.59 per 1M input tokens, ~$0.79 per 1M output tokens
- **Llama3-8b**: ~$0.05 per 1M input tokens, ~$0.08 per 1M output tokens

### Estimated Cost per Analysis
- **6 questions × 100 reviews**: ~15,000 tokens total
- **Llama3-70b**: ~$0.01 per analysis
- **Llama3-8b**: ~$0.001 per analysis
- **With caching**: Near-zero cost after first run

---

## Future Improvements

### Potential Enhancements
1. **Advanced prompting**: Chain-of-thought, few-shot examples
2. **Larger context**: Use models with larger context windows
3. **Multi-turn analysis**: Follow-up questions for deeper insights
4. **Sentiment analysis**: Combine with sentiment scores
5. **Topic modeling**: Identify key themes before analysis

### Scalability
- **Parallel processing**: Analyze multiple questions simultaneously
- **Distributed processing**: Process larger datasets across multiple workers
- **Streaming**: Process reviews in streams for very large datasets
- **Model fine-tuning**: Fine-tune model on domain-specific data

---

## Troubleshooting

### API Key Issues
```
ValueError: Groq API key required
```
**Solution**: Set `GROQ_API_KEY` environment variable

### Slow Performance
**Cause**: Network latency or model inference time
**Solution**: Use smaller model or reduce sample size

### Poor Quality Answers
**Cause**: Prompt design or insufficient review context
**Solution**: Adjust prompts or increase sample size

### Cache Not Working
**Cause**: Cache directory permissions or key collision
**Solution**: Check cache directory and clear old cache files

---

## Security Considerations

### API Key Protection
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Monitor API usage for anomalies

### Data Privacy
- Review data is public (from Google Play Store)
- No personal identifiers in analysis
- Results are aggregated insights only
- Compliance with data usage policies

---

## Monitoring

### Metrics to Track
- Total API calls
- Cache hit rate
- Token usage
- Analysis time
- Error rate
- Cost per analysis

### Logging
- All API calls logged
- Cache hits/misses tracked
- Errors with full stack traces
- Performance metrics recorded

---

## Best Practices

1. **Always use caching** to reduce costs and improve speed
2. **Review answers** before deploying to production
3. **Monitor token usage** to control costs
4. **Test with sample data** before full analysis
5. **Keep API keys secure** using environment variables
6. **Handle errors gracefully** with retry logic
7. **Validate results** for quality and relevance
