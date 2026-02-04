#!/usr/bin/env python3
"""
Intent-Driven Cold Outreach Agent - MIP-003 Compliant Masumi Integration
Implements all required MIP-003 Agentic Service API Standard endpoints

This is the entry point for the MIP-003 compliant Masumi outreach agent.
Run this file to start the agent server with all required endpoints.
"""
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import os

from agent import (
    start_job, get_job_status, provide_input, check_availability,
    get_input_schema, get_demo_data, process_outreach_job, job_storage
)

# Background task reference
background_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 Starting Intent-Driven Cold Outreach Agent (MIP-003 Compliant)")
    print("📋 This agent processes outreach requests using a 7-step reasoning workflow")
    print("🔗 Connects to the Node.js outreach service for message generation")
    print("📡 MIP-003 Agentic Service API Standard compliant")
    print()
    
    # Start background job processor
    global background_task
    background_task = asyncio.create_task(job_processor())
    
    yield
    
    # Shutdown
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass

# FastAPI app
app = FastAPI(
    title="Intent-Driven Cold Outreach Agent",
    description="MIP-003 Compliant Agentic Service for personalized outreach message generation",
    version="1.0.0",
    lifespan=lifespan
)

# Pydantic models for request/response validation
class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: Dict[str, Any]

class ProvideInputRequest(BaseModel):
    job_id: str
    status_id: str
    input_data: Dict[str, Any]

# MIP-003 Required Endpoints

@app.post("/start_job")
async def start_job_endpoint(request: StartJobRequest):
    """
    MIP-003 Required: Initiates a job on the remote crew
    """
    try:
        if not request.identifier_from_purchaser:
            raise HTTPException(status_code=400, detail="identifier_from_purchaser is required")
        
        if not request.input_data:
            raise HTTPException(status_code=400, detail="input_data is required")
        
        result = await start_job(request.identifier_from_purchaser, request.input_data)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job initiation failed: {str(e)}")

@app.get("/status")
async def get_status_endpoint(job_id: str = Query(..., description="The ID of the job to check")):
    """
    MIP-003 Required: Retrieves the current status of a specific job
    """
    try:
        result = await get_job_status(job_id)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@app.post("/provide_input")
async def provide_input_endpoint(request: ProvideInputRequest):
    """
    MIP-003 Optional: Provides additional input for a job awaiting input
    """
    try:
        result = await provide_input(request.job_id, request.status_id, request.input_data)
        return result
        
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Input processing failed: {str(e)}")

@app.get("/availability")
async def get_availability_endpoint():
    """
    MIP-003 Required: Checks if the server is operational
    """
    try:
        result = await check_availability()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Availability check failed: {str(e)}")

@app.get("/input_schema")
async def get_input_schema_endpoint():
    """
    MIP-003 Required: Returns the expected input format for jobs
    """
    try:
        result = get_input_schema()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema retrieval failed: {str(e)}")

@app.get("/demo")
async def get_demo_endpoint():
    """
    MIP-003 Optional: Returns demo data for marketing purposes
    """
    try:
        result = get_demo_data()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo data retrieval failed: {str(e)}")

# Additional endpoints for monitoring and management

@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    """
    availability = await check_availability()
    return {
        "status": "healthy" if availability["status"] == "available" else "unhealthy",
        "service": "Intent-Driven Cold Outreach Agent",
        "version": "1.0.0",
        "mip003_compliant": True,
        "outreach_service": availability
    }

@app.get("/jobs")
async def list_jobs():
    """
    Development endpoint to list all jobs (remove in production)
    """
    return {
        "jobs": list(job_storage.keys()),
        "total": len(job_storage)
    }

@app.post("/simulate_payment/{job_id}")
async def simulate_payment(job_id: str):
    """
    Development endpoint to simulate payment for a job (remove in production)
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = job_storage[job_id]
    
    if job["status"] != "awaiting_payment":
        raise HTTPException(status_code=400, detail=f"Job {job_id} is not awaiting payment (current status: {job['status']})")
    
    job["status"] = "running"
    job["payment_simulated"] = True
    
    return {
        "message": f"Payment simulated for job {job_id}",
        "status": "running"
    }

# Background task to process jobs
async def job_processor():
    """
    Background task to process jobs that have received payment
    """
    print("🔄 Background job processor started")
    while True:
        try:
            # Find jobs that are ready to process
            for job_id, job in job_storage.items():
                # Simulate payment received for awaiting_payment jobs (in production, this would be handled by payment system)
                if job["status"] == "awaiting_payment" and not job.get("payment_simulated"):
                    print(f"💰 Simulating payment received for job {job_id}")
                    job["status"] = "running"
                    job["payment_simulated"] = True
                
                # Process running jobs
                if job["status"] == "running" and not job.get("processing"):
                    print(f"🔄 Starting processing for job {job_id}")
                    job["processing"] = True
                    asyncio.create_task(process_job_async(job_id))
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"Job processor error: {e}")
            await asyncio.sleep(10)

async def process_job_async(job_id: str):
    """
    Async wrapper for job processing
    """
    try:
        await process_outreach_job(job_id)
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        if job_id in job_storage:
            job_storage[job_id]["status"] = "failed"
            job_storage[job_id]["result"] = f"Processing error: {str(e)}"
    finally:
        if job_id in job_storage:
            job_storage[job_id]["processing"] = False

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🌐 Starting server on {host}:{port}")
    print("📖 API Documentation available at: http://localhost:8080/docs")
    print("🔍 Health check available at: http://localhost:8080/health")
    print()
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
