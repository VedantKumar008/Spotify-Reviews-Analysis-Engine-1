# Phase 4: Backend API Development

## Overview
This phase implements the backend API for the Spotify Reviews Analysis Engine using FastAPI. The API provides endpoints for executing analysis workflows and retrieving results.

## Components

### Files
- `api/main.py` - Main FastAPI application with workflow orchestration
- `api/cache.py` - Caching module for results
- `api/middleware.py` - Rate limiting and error handling middleware
- `requirements.txt` - Python dependencies
- `API_DOCUMENTATION.md` - Detailed API endpoint documentation
- `BACKEND_DOCUMENTATION.md` - Backend architecture and implementation details
- `data/results/` - Directory for storing workflow results
- `data/cache/` - Directory for API cache

## Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Groq API key
- Completed Phase 2 and Phase 3

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

## Usage

### Start the Server
```bash
# Run the API server
python -m api.main
```

The server will start on `http://localhost:8000`

### Access API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### POST /api/run-workflow
Execute the analysis workflow asynchronously.

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
Get analysis results for a workflow.

**Response:**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "completed",
  "results": { ... },
  "metadata": { ... }
}
```

### GET /api/status/{workflow_id}
Get the current status and progress of a workflow.

**Response:**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "running",
  "progress": 50.0,
  "current_step": "Running LLM analysis"
}
```

### GET /api/health
Health check endpoint.

### GET /api/workflows
List all workflows.

## Features

- **FastAPI Framework**: Modern, fast Python web framework
- **Async Processing**: Background tasks for long-running workflows
- **Workflow Orchestration**: Manages analysis workflow lifecycle
- **Caching**: In-memory and file-based caching for results
- **Rate Limiting**: 60 requests per minute per IP
- **Error Handling**: Comprehensive error handling middleware
- **Auto Documentation**: Interactive API documentation (Swagger/ReDoc)
- **CORS Support**: Cross-origin resource sharing enabled

## Workflow Lifecycle

1. **Pending** - Workflow queued but not started
2. **Running** - Workflow executing (progress updates available)
3. **Completed** - Workflow finished successfully
4. **Failed** - Workflow failed with error

## Example Usage

### Using curl
```bash
# Start workflow
curl -X POST "http://localhost:8000/api/run-workflow" \
  -H "Content-Type: application/json" \
  -d '{"use_cache": true, "sample_size": 100}'

# Check status
curl "http://localhost:8000/api/status/20240622_233500_123456"

# Get results
curl "http://localhost:8000/api/results/20240622_233500_123456"
```

### Using Python
```python
import requests
import time

# Start workflow
response = requests.post(
    "http://localhost:8000/api/run-workflow",
    json={"use_cache": True, "sample_size": 100}
)
workflow_id = response.json()["workflow_id"]

# Poll for completion
while True:
    status = requests.get(f"http://localhost:8000/api/status/{workflow_id}").json()
    if status["status"] == "completed":
        break
    print(f"Progress: {status['progress']}%")
    time.sleep(2)

# Get results
results = requests.get(f"http://localhost:8000/api/results/{workflow_id}").json()
print(results["results"])
```

## Configuration

### Rate Limiting
Default: 60 requests per minute per IP

To modify, edit `api/middleware.py`:
```python
rate_limiter = RateLimiter(requests_per_minute=60)
```

### Cache TTL
Default: 1 hour

To modify, edit `api/cache.py`:
```python
result_cache = ResultCache(ttl_seconds=3600)
```

### CORS
Currently allows all origins. To restrict, edit `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

## Performance

- **Workflow execution**: 30-60 seconds
- **API response time**: <100ms (non-workflow endpoints)
- **Status polling**: <50ms
- **Results retrieval**: <200ms

## Integration

### Input
- Cleaned reviews from Phase 2 (`phase2-data-cleaning/data/processed/`)
- LLM analysis from Phase 3 (`phase3-llm-analysis/`)

### Output
- Workflow results in `data/results/`
- API endpoints for frontend consumption

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'data_cleaning'
```
**Solution**: Ensure Phase 2 and Phase 3 are in the parent directory

### API Key Issues
```
ValueError: GROQ_API_KEY environment variable not set
```
**Solution**: Set the `GROQ_API_KEY` environment variable

### Missing Data
```
FileNotFoundError: No cleaned data found
```
**Solution**: Complete Phase 2 data cleaning first

### Rate Limit Errors
```
429 Too Many Requests
```
**Solution**: Reduce request frequency or increase rate limit

## Development

### Running in Development Mode
```bash
python -m api.main
```

### Running in Production Mode
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

### Manual Testing
1. Start the server
2. Access Swagger UI at `http://localhost:8000/docs`
3. Test endpoints using the interactive interface

### Automated Testing
```bash
# Run tests (if implemented)
pytest tests/
```

## Security Considerations

### Current State
- No authentication (for simplicity)
- CORS enabled for all origins
- Rate limiting to prevent abuse

### Production Recommendations
- Add API key authentication
- Implement OAuth2
- Restrict CORS origins
- Use HTTPS only
- Add input validation
- Implement audit logging

## Next Steps

After backend API:
1. Test all API endpoints
2. Verify workflow execution
3. Proceed to **Phase 5: Frontend Development**
4. Integrate frontend with API

## Documentation

- **API Documentation**: See `API_DOCUMENTATION.md` for detailed endpoint documentation
- **Backend Documentation**: See `BACKEND_DOCUMENTATION.md` for architecture details

## Notes

- Uses FastAPI for modern async API development
- Background tasks prevent blocking during workflow execution
- In-memory state is lost on restart (results persisted to disk)
- Rate limiting helps prevent API abuse
- Auto-generated documentation available at `/docs`
