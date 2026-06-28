# API Documentation

## Phase 4: Backend API Development

### Overview
This document describes the REST API for the Spotify Reviews Analysis Engine. The API is built with FastAPI and provides endpoints for executing analysis workflows and retrieving results.

---

## Base URL
```
http://localhost:8000
```

---

## Authentication
Currently, the API does not require authentication. This may be added in future versions for production deployment.

---

## API Endpoints

### 1. Root Endpoint
**GET /**

Get API information and available endpoints.

**Response:**
```json
{
  "name": "Spotify Reviews Analysis API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "POST /api/run-workflow": "Execute analysis workflow",
    "GET /api/results/{workflow_id}": "Get workflow results",
    "GET /api/status/{workflow_id}": "Get workflow status",
    "GET /api/health": "Health check"
  }
}
```

---

### 2. Health Check
**GET /api/health**

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-22T23:35:00",
  "active_workflows": 1
}
```

---

### 3. Run Workflow
**POST /api/run-workflow**

Execute the analysis workflow asynchronously.

**Request Body:**
```json
{
  "use_cache": true,
  "sample_size": 100
}
```

**Parameters:**
- `use_cache` (boolean, optional): Whether to use caching for LLM responses. Default: `true`
- `sample_size` (integer, optional): Number of reviews to analyze per question. Default: `100`

**Response:**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "pending",
  "message": "Workflow started successfully"
}
```

**Status Codes:**
- `200 OK`: Workflow started successfully
- `500 Internal Server Error`: Server error during workflow initialization

---

### 4. Get Results
**GET /api/results/{workflow_id}**

Get analysis results for a specific workflow.

**Path Parameters:**
- `workflow_id` (string, required): Unique workflow identifier

**Response (Completed):**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "completed",
  "results": {
    "generated_at": "2024-06-22T23:35:00",
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
      "q2": {
        "question": "What are the most common frustrations with recommendations?",
        "answer": "Users are frustrated by...",
        "cached": false,
        "reviews_analyzed": 100
      },
      ...
    }
  },
  "metadata": {
    "started_at": "2024-06-22T23:35:00",
    "completed_at": "2024-06-22T23:35:45",
    "statistics": {
      "total_reviews_analyzed": 6000,
      "total_api_calls": 6,
      ...
    }
  }
}
```

**Response (Running):**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "running",
  "metadata": {
    "progress": 50.0,
    "current_step": "Running LLM analysis",
    "started_at": "2024-06-22T23:35:00"
  }
}
```

**Response (Failed):**
```json
{
  "workflow_id": "20240622_233500_123456",
  "status": "failed",
  "error": "GROQ_API_KEY environment variable not set",
  "metadata": {
    "started_at": "2024-06-22T23:35:00",
    "completed_at": "2024-06-22T23:35:01"
  }
}
```

**Status Codes:**
- `200 OK`: Results retrieved successfully
- `404 Not Found`: Workflow not found

---

### 5. Get Status
**GET /api/status/{workflow_id}**

Get the current status and progress of a workflow.

**Path Parameters:**
- `workflow_id` (string, required): Unique workflow identifier

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

**Status Codes:**
- `200 OK`: Status retrieved successfully
- `404 Not Found`: Workflow not found

---

### 6. List Workflows
**GET /api/workflows**

List all workflows with basic information.

**Response:**
```json
{
  "total_workflows": 5,
  "workflows": [
    {
      "workflow_id": "20240622_233500_123456",
      "status": "completed",
      "progress": 100.0,
      "started_at": "2024-06-22T23:35:00",
      "completed_at": "2024-06-22T23:35:45"
    },
    {
      "workflow_id": "20240622_233600_789012",
      "status": "running",
      "progress": 30.0,
      "started_at": "2024-06-22T23:36:00",
      "completed_at": null
    },
    ...
  ]
}
```

---

## Workflow Status Values

| Status | Description |
|--------|-------------|
| `pending` | Workflow has been queued but not started |
| `running` | Workflow is currently executing |
| `completed` | Workflow has completed successfully |
| `failed` | Workflow has failed with an error |

---

## Workflow Steps

The analysis workflow progresses through the following steps:

1. **Loading cleaned data** (10-30%)
   - Loads cleaned reviews from Phase 2 output

2. **Initializing LLM analyzer** (30-40%)
   - Sets up Groq API client and analyzer

3. **Running LLM analysis** (40-80%)
   - Analyzes 6 research questions using LLM

4. **Saving results** (80-100%)
   - Saves results to file and updates workflow state

---

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request**
```json
{
  "detail": "Invalid request parameters"
}
```

**404 Not Found**
```json
{
  "detail": "Workflow 20240622_233500_123456 not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error: GROQ_API_KEY environment variable not set"
}
```

---

## Rate Limiting

Currently, rate limiting is not implemented. This may be added in future versions for production deployment.

---

## CORS

The API supports CORS (Cross-Origin Resource Sharing) and allows requests from any origin. This can be configured in the middleware settings.

---

## OpenAPI/Swagger Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces provide:
- Interactive API exploration
- Request/response examples
- Schema validation
- Try-it-out functionality

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

## Usage Examples

### Example 1: Run Workflow and Poll for Results

```bash
# Step 1: Start workflow
curl -X POST "http://localhost:8000/api/run-workflow" \
  -H "Content-Type: application/json" \
  -d '{"use_cache": true, "sample_size": 100}'

# Response: {"workflow_id": "20240622_233500_123456", "status": "pending", "message": "Workflow started successfully"}

# Step 2: Poll for status
curl "http://localhost:8000/api/status/20240622_233500_123456"

# Step 3: Get results when status is "completed"
curl "http://localhost:8000/api/results/20240622_233500_123456"
```

### Example 2: Using Python Requests

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
    status_response = requests.get(f"http://localhost:8000/api/status/{workflow_id}")
    status = status_response.json()
    
    if status["status"] == "completed":
        break
    elif status["status"] == "failed":
        print(f"Workflow failed: {status['error']}")
        exit(1)
    
    print(f"Progress: {status['progress']}% - {status['current_step']}")
    time.sleep(2)

# Get results
results_response = requests.get(f"http://localhost:8000/api/results/{workflow_id}")
results = results_response.json()
print(results["results"])
```

---

## Best Practices

1. **Poll for status**: Use the status endpoint to check workflow progress before requesting results
2. **Handle errors**: Check for failed status and error messages
3. **Use caching**: Enable caching to reduce costs and improve speed
4. **Adjust sample size**: Increase sample size for more comprehensive analysis, decrease for faster results
5. **Store workflow IDs**: Keep track of workflow IDs for later result retrieval

---

## Integration with Frontend

The API is designed to work with a frontend application:

1. Frontend calls `POST /api/run-workflow` to start analysis
2. Frontend polls `GET /api/status/{workflow_id}` to show progress
3. When status is `completed`, frontend calls `GET /api/results/{workflow_id}` to display results
4. Frontend displays the 6 research questions and their answers

---

## Future Enhancements

Potential improvements for the API:

1. **Authentication**: Add API key or OAuth authentication
2. **Rate limiting**: Implement rate limiting to prevent abuse
3. **WebSocket support**: Use WebSockets for real-time progress updates
4. **Batch processing**: Support multiple workflow executions
5. **Result filtering**: Add filtering and sorting options for results
6. **Webhook notifications**: Send webhook notifications when workflows complete
