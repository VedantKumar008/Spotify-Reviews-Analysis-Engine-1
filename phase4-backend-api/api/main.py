"""
FastAPI Backend for Spotify Reviews Analysis Engine
Phase 4: Backend API Development
"""

import json
import os
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Import analysis modules from previous phases
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "phase2-data-cleaning"))
sys.path.append(str(Path(__file__).parent.parent.parent / "phase3-llm-analysis"))

from api.groq_utils import get_groq_api_key, get_groq_api_status
from api.middleware import RateLimitMiddleware, ErrorHandlerMiddleware
from api.efficient_workflow import EfficientWorkflow


class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowRequest(BaseModel):
    """Request model for workflow execution."""
    use_cache: bool = True
    use_all_reviews: bool = True
    sample_size: int = 20


class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    workflow_id: str
    status: WorkflowStatus
    message: str


class ResultsResponse(BaseModel):
    """Response model for analysis results."""
    workflow_id: str
    status: WorkflowStatus
    results: Optional[Dict] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None


class StatusResponse(BaseModel):
    """Response model for workflow status."""
    workflow_id: str
    status: WorkflowStatus
    progress: float
    current_step: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


# Global workflow state storage
workflows: Dict[str, Dict] = {}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Spotify Reviews Analysis API",
        description="API for analyzing Spotify reviews using AI",
        version="1.0.0"
    )
    
    # Error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)
    
    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()


def run_workflow_async(
    workflow_id: str,
    use_cache: bool,
    use_all_reviews: bool,
    sample_size: int
):
    """
    Run the analysis workflow asynchronously using efficient workflow.
    
    Args:
        workflow_id: Unique workflow identifier
        use_cache: Whether to use caching
        use_all_reviews: Whether to analyze the full cleaned dataset
        sample_size: Number of reviews to analyze when not using all reviews
    """
    try:
        workflow_start = time.time()

        # Update status to running
        workflows[workflow_id]["status"] = WorkflowStatus.RUNNING
        workflows[workflow_id]["current_step"] = "Loading cleaned data"
        workflows[workflow_id]["progress"] = 10.0
        
        # Step 1: Load cleaned data
        workflows[workflow_id]["current_step"] = "Loading cleaned reviews"
        workflows[workflow_id]["progress"] = 20.0
        
        # Load cleaned data from Phase 2
        input_dir = Path(__file__).parent.parent.parent / "phase2-data-cleaning" / "data" / "processed"
        files = list(input_dir.glob("spotify_reviews_cleaned_*.json"))
        
        if not files:
            raise FileNotFoundError("No cleaned data found. Please run Phase 2 first.")
        
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            reviews = json.load(f)
        
        workflows[workflow_id]["progress"] = 30.0
        
        # Step 2: Initialize efficient workflow
        api_key = get_groq_api_key()
        print(f"DEBUG: API key loaded: {api_key[:10] if api_key else 'None'}...")
        
        if not api_key:
            # Fallback to pre-computed results if no API key
            print("DEBUG: No API key found, using fallback")
            workflows[workflow_id]["progress"] = 40.0
            workflows[workflow_id]["current_step"] = "Loading pre-computed results (Offline Fallback)"
            
            # Simulate a small delay for realistic UX/progress tracking
            time.sleep(1.5)
            
            from api.groq_utils import load_precomputed_results
            workflow_time_seconds = time.time() - workflow_start
            output_data = load_precomputed_results(len(reviews), workflow_time_seconds)
            
            # Save results
            output_dir = Path(__file__).parent.parent / "data" / "results"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            results_file = output_dir / f"workflow_{workflow_id}_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            workflows[workflow_id]["progress"] = 100.0
            workflows[workflow_id]["current_step"] = "Completed"
            workflows[workflow_id]["status"] = WorkflowStatus.COMPLETED
            workflows[workflow_id]["results"] = output_data
            workflows[workflow_id]["completed_at"] = datetime.now().isoformat()
            return
        
        print("DEBUG: API key found, proceeding with efficient analysis")
        
        # Initialize efficient workflow
        efficient_workflow = EfficientWorkflow()
        
        workflows[workflow_id]["progress"] = 40.0
        workflows[workflow_id]["current_step"] = "Running efficient analysis"
        
        def update_analysis_progress(progress: float, step: str):
            workflows[workflow_id]["progress"] = progress
            workflows[workflow_id]["current_step"] = step
        
        # Step 3: Run efficient workflow
        output_data = efficient_workflow.run_workflow(
            workflow_id=workflow_id,
            reviews=reviews,
            batch_size=100,
            progress_callback=update_analysis_progress,
            force_refresh=not use_cache
        )
        
        # Save results to file for compatibility
        output_dir = Path(__file__).parent.parent / "data" / "results"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = output_dir / f"workflow_{workflow_id}_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        workflows[workflow_id]["progress"] = 100.0
        workflows[workflow_id]["current_step"] = "Completed"
        workflows[workflow_id]["status"] = WorkflowStatus.COMPLETED
        workflows[workflow_id]["results"] = output_data
        workflows[workflow_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        workflows[workflow_id]["status"] = WorkflowStatus.FAILED
        workflows[workflow_id]["error"] = str(e)
        workflows[workflow_id]["completed_at"] = datetime.now().isoformat()
        print(f"Workflow {workflow_id} failed: {e}")
        import traceback
        traceback.print_exc()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    groq_status = get_groq_api_status()

    return {
        "name": "Spotify Reviews Analysis API",
        "version": "1.0.0",
        "status": "running",
        "groq_api": groq_status,
        "endpoints": {
            "POST /api/run-workflow": "Execute analysis workflow",
            "GET /api/results/{workflow_id}": "Get workflow results",
            "GET /api/status/{workflow_id}": "Get workflow status",
            "GET /api/health": "Health check"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    groq_status = get_groq_api_status()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_workflows": len([w for w in workflows.values() if w["status"] == WorkflowStatus.RUNNING]),
        "groq_api": groq_status,
    }


@app.post("/api/run-workflow", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Execute the analysis workflow.
    
    Args:
        request: Workflow execution request
        background_tasks: FastAPI background tasks
        
    Returns:
        Workflow response with workflow ID
    """
    # Generate unique workflow ID
    workflow_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    # Initialize workflow state
    workflows[workflow_id] = {
        "workflow_id": workflow_id,
        "status": WorkflowStatus.PENDING,
        "progress": 0.0,
        "current_step": "Pending",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "error": None,
        "results": None,
        "request": request.dict()
    }
    
    # Add background task
    background_tasks.add_task(
        run_workflow_async,
        workflow_id,
        request.use_cache,
        request.use_all_reviews,
        request.sample_size
    )
    
    return WorkflowResponse(
        workflow_id=workflow_id,
        status=WorkflowStatus.PENDING,
        message="Workflow started successfully"
    )


@app.get("/api/results/{workflow_id}", response_model=ResultsResponse)
async def get_results(workflow_id: str):
    """
    Get analysis results for a workflow.
    
    Args:
        workflow_id: Workflow identifier
        
    Returns:
        Analysis results or error if workflow failed
    """
    if workflow_id not in workflows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    workflow = workflows[workflow_id]
    
    if workflow["status"] == WorkflowStatus.FAILED:
        return ResultsResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.FAILED,
            error=workflow["error"],
            metadata={
                "started_at": workflow["started_at"],
                "completed_at": workflow["completed_at"]
            }
        )
    
    if workflow["status"] != WorkflowStatus.COMPLETED:
        return ResultsResponse(
            workflow_id=workflow_id,
            status=workflow["status"],
            metadata={
                "progress": workflow["progress"],
                "current_step": workflow["current_step"],
                "started_at": workflow["started_at"]
            }
        )
    
    return ResultsResponse(
        workflow_id=workflow_id,
        status=WorkflowStatus.COMPLETED,
        results=workflow["results"],
        metadata={
            "started_at": workflow["started_at"],
            "completed_at": workflow["completed_at"],
            "statistics": workflow["results"].get("statistics", {})
        }
    )


@app.get("/api/status/{workflow_id}", response_model=StatusResponse)
async def get_status(workflow_id: str):
    """
    Get the status of a workflow.
    
    Args:
        workflow_id: Workflow identifier
        
    Returns:
        Workflow status and progress
    """
    if workflow_id not in workflows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    workflow = workflows[workflow_id]
    
    return StatusResponse(
        workflow_id=workflow_id,
        status=workflow["status"],
        progress=workflow["progress"],
        current_step=workflow["current_step"],
        started_at=workflow["started_at"],
        completed_at=workflow["completed_at"],
        error=workflow["error"]
    )


@app.get("/api/workflows")
async def list_workflows():
    """
    List all workflows.
    
    Returns:
        List of all workflows with basic information
    """
    return {
        "total_workflows": len(workflows),
        "workflows": [
            {
                "workflow_id": w_id,
                "status": w["status"],
                "progress": w["progress"],
                "started_at": w["started_at"],
                "completed_at": w["completed_at"]
            }
            for w_id, w in workflows.items()
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
