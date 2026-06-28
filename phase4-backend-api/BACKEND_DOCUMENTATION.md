# Backend API Documentation

## Phase 4: Backend API Development

### Overview
This document describes the backend API implementation for the Spotify Reviews Analysis Engine, including architecture, components, and technical details.

---

## Architecture

### Technology Stack
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Async Processing**: FastAPI Background Tasks
- **Caching**: In-memory + File-based caching
- **Rate Limiting**: Custom middleware
- **Error Handling**: Custom middleware
- **API Documentation**: Auto-generated OpenAPI/Swagger

### Components

#### 1. Main Application (`api/main.py`)
- FastAPI application setup
- API endpoint definitions
- Workflow orchestration
- Background task management
- Global workflow state storage

#### 2. Caching Module (`api/cache.py`)
- In-memory cache for fast access
- File-based cache for persistence
- TTL (Time-To-Live) support
- Cache key generation
- Cache statistics

#### 3. Middleware (`api/middleware.py`)
- Rate limiting middleware
- Error handling middleware
- Request tracking
- Response headers

---

## Workflow Orchestration

### Workflow Lifecycle

1. **Initialization**
   - Generate unique workflow ID
   - Initialize workflow state
   - Set status to `pending`

2. **Execution**
   - Background task starts
   - Status changes to `running`
   - Progress updates at each step

3. **Completion**
   - Status changes to `completed` or `failed`
   - Results saved to file
   - Workflow state updated

### Workflow Steps

| Step | Progress | Description |
|------|----------|-------------|
| Loading cleaned data | 10-30% | Load reviews from Phase 2 |
| Initializing LLM analyzer | 30-40% | Set up Groq API client |
| Running LLM analysis | 40-80% | Analyze 6 research questions |
| Saving results | 80-100% | Save results to file |

---

## API Endpoints

### POST /api/run-workflow
Starts a new analysis workflow.

**Request:**
```json
{
  "use_cache": true,
  "sample_size": 100
}
```

**Response:**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "pending",
  "message": "Workflow started successfully"
}
```

### GET /api/results/{workflow_id}
Retrieves analysis results for a workflow.

**Response (Completed):**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "completed",
  "results": {
    "generated_at": "2024-06-22T23:35:00",
    "model_used": "llama3-70b-8192",
    "statistics": { ... },
    "results": { ... }
  },
  "metadata": { ... }
}
```

### GET /api/status/{workflow_id}
Gets the current status and progress of a workflow.

**Response:**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "running",
  "progress": 50.0,
  "current_step": "Running LLM analysis",
  "started_at": "2024-06-22T23:35:00",
  "completed_at": null,
  "error": null
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-22T23:35:00",
  "active_workflows": 1
}
```

### GET /api/workflows
Lists all workflows.

**Response:**
```json
{
  "total_workflows": 5,
  "workflows": [ ... ]
}
```

---

## Caching Strategy

### Cache Implementation
- **Memory Cache**: Fast access for recent requests
- **File Cache**: Persistent storage across restarts
- **TTL**: 1 hour default (configurable)
- **Cache Key**: MD5 hash of workflow parameters

### Cache Benefits
- Reduces API costs (fewer LLM calls)
- Improves response time
- Provides consistent results
- Enables offline testing

### Cache Management
```python
# Get cached result
result = result_cache.get(workflow_params)

# Cache result
result_cache.set(workflow_params, data)

# Clear all cache
result_cache.clear()

# Clear expired cache
result_cache.clear_expired()

# Get cache statistics
stats = result_cache.get_stats()
```

---

## Rate Limiting

### Implementation
- **In-memory tracking**: Per-IP request counting
- **Sliding window**: 1-minute window
- **Default limit**: 60 requests per minute
- **Headers**: X-RateLimit-Limit, X-RateLimit-Remaining

### Rate Limit Response
```json
{
  "detail": "Rate limit exceeded",
  "remaining_requests": 0,
  "limit": 60
}
```

### Configuration
```python
# In middleware.py
rate_limiter = RateLimiter(requests_per_minute=60)
```

---

## Error Handling

### Error Types
- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Workflow not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server errors

### Error Response Format
```json
{
  "detail": "Error message"
}
```

### Error Handling Middleware
- Catches all exceptions
- Converts to appropriate HTTP status
- Provides user-friendly error messages
- Logs errors for debugging

---

## Data Models

### WorkflowRequest
```python
class WorkflowRequest(BaseModel):
    use_cache: bool = True
    sample_size: int = 100
```

### WorkflowResponse
```python
class WorkflowResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    message: str
```

### ResultsResponse
```python
class ResultsResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    results: Optional[Dict] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None
```

### StatusResponse
```python
class StatusResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    progress: float
    current_step: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
```

---

## State Management

### Workflow State
```python
workflows[workflow_id] = {
    "workflow_id": str,
    "status": WorkflowStatus,
    "progress": float,
    "current_step": str,
    "started_at": str,
    "completed_at": Optional[str],
    "error": Optional[str],
    "results": Optional[Dict],
    "request": Dict
}
```

### State Storage
- **In-memory**: Fast access during runtime
- **File-based**: Results persisted to disk
- **No database**: Simplified for this implementation

### State Limitations
- Lost on server restart (except persisted results)
- Not suitable for distributed deployments
- Can be replaced with Redis/Database for production

---

## Async Processing

### Background Tasks
- FastAPI Background Tasks for async execution
- Non-blocking API responses
- Progress tracking during execution

### Implementation
```python
@app.post("/api/run-workflow")
async def run_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    workflow_id = generate_workflow_id()
    background_tasks.add_task(run_workflow_async, workflow_id, ...)
    return WorkflowResponse(workflow_id=workflow_id, status="pending")
```

---

## Integration Points

### Phase 2 (Data Cleaning)
- **Input**: Cleaned reviews from `phase2-data-cleaning/data/processed/`
- **Dependency**: Must be completed before API can run
- **Format**: JSON file with cleaned review data

### Phase 3 (LLM Analysis)
- **Integration**: Imports and uses GroqAnalyzer class
- **Configuration**: Uses same cache directory
- **Output**: Results saved to API results directory

### Phase 5 (Frontend)
- **API Endpoints**: Frontend calls API endpoints
- **Polling**: Frontend polls status endpoint
- **Results**: Frontend displays results from API

---

## Security Considerations

### Current Implementation
- No authentication (for simplicity)
- CORS enabled for all origins
- No input validation beyond Pydantic models
- Rate limiting to prevent abuse

### Production Recommendations
- Add API key authentication
- Implement OAuth2
- Restrict CORS origins
- Add input sanitization
- Use HTTPS only
- Implement request signing
- Add audit logging

---

## Performance Considerations

### Expected Performance
- **Workflow execution**: 30-60 seconds
- **API response time**: <100ms (non-workflow endpoints)
- **Status polling**: <50ms
- **Results retrieval**: <200ms

### Bottlenecks
- LLM API calls (longest operation)
- File I/O for large datasets
- Network latency to Groq API

### Optimization Strategies
- Enable caching to reduce LLM calls
- Use smaller sample size for faster results
- Implement parallel processing for multiple questions
- Use CDN for static assets (if added)

---

## Deployment

### Local Development
```bash
cd phase4-backend-api
pip install -r requirements.txt
export GROQ_API_KEY="your-key"
python -m api.main
```

### Production Deployment
- Use Gunicorn with Uvicorn workers
- Implement proper logging
- Add monitoring and alerting
- Use environment variables for configuration
- Implement health checks
- Use reverse proxy (nginx)

### Environment Variables
```bash
GROQ_API_KEY=your-groq-api-key
```

---

## Monitoring

### Metrics to Track
- Active workflows count
- Workflow success/failure rate
- Average workflow duration
- API response times
- Rate limit violations
- Cache hit rate
- Error rates

### Logging
- All workflow state changes
- API errors with stack traces
- Performance metrics
- Cache operations

---

## Testing

### Unit Tests
- Test individual endpoint logic
- Test caching functionality
- Test rate limiting
- Test error handling

### Integration Tests
- Test full workflow execution
- Test API integration with Phase 2/3
- Test error scenarios

### Load Tests
- Test concurrent workflow executions
- Test rate limiting effectiveness
- Test memory usage under load

---

## Troubleshooting

### Common Issues

1. **Workflow not starting**
   - Check GROQ_API_KEY is set
   - Verify Phase 2 data exists
   - Check API logs for errors

2. **Workflow stuck in running**
   - Check for background task errors
   - Verify Groq API is accessible
   - Check network connectivity

3. **Rate limit errors**
   - Reduce request frequency
   - Increase rate limit if needed
   - Check for abusive patterns

4. **Cache not working**
   - Check cache directory permissions
   - Verify cache TTL settings
   - Clear cache and retry

---

## Future Improvements

### Potential Enhancements
1. **Database**: Replace in-memory state with Redis/PostgreSQL
2. **Authentication**: Add API key or OAuth2
3. **WebSocket**: Real-time progress updates
4. **Queue System**: Use Celery for better task management
5. **Monitoring**: Add Prometheus metrics
6. **Logging**: Structured logging with ELK stack
7. **Testing**: Comprehensive test suite
8. **Documentation**: API versioning and deprecation policy

### Scalability
- Horizontal scaling with load balancer
- Distributed task queue (Celery + Redis)
- Database sharding for large datasets
- CDN for static assets
- Geographic distribution

---

## Best Practices

1. **Always use caching** to reduce costs
2. **Monitor workflow execution** for errors
3. **Implement proper logging** for debugging
4. **Use environment variables** for configuration
5. **Test error scenarios** before deployment
6. **Monitor rate limits** to prevent abuse
7. **Keep API keys secure** using secrets management
8. **Implement health checks** for monitoring
