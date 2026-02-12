#!/usr/bin/env python3
"""
Intent-Driven Cold Outreach Agent - Masumi Integration (MIP-003 Compliant)
Implements the MIP-003 Agentic Service API Standard

This file contains the agent logic that processes outreach requests
using the Intent-Driven Cold Outreach Agent system with full MIP-003 compliance.
"""
import os
import json
import aiohttp
import asyncio
import logging
import hashlib
import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OUTREACH_SERVICE_URL = os.getenv("OUTREACH_SERVICE_URL", "http://localhost:3000")
OUTREACH_TIMEOUT = int(os.getenv("OUTREACH_TIMEOUT", "30"))
AGENT_IDENTIFIER = os.getenv("AGENT_IDENTIFIER", "intent-driven-outreach-agent-v1")
SELLER_VKEY = os.getenv("SELLER_VKEY", "")

# In-memory job storage (in production, use a proper database)
job_storage = {}

def generate_job_id() -> str:
    """Generate a unique job ID"""
    return str(uuid.uuid4())

def generate_blockchain_identifier() -> str:
    """Generate a blockchain identifier for payment tracking"""
    return f"block_{uuid.uuid4().hex[:12]}"

def hash_input_data(input_data: dict) -> str:
    """Generate hash of input data for integrity verification"""
    data_str = json.dumps(input_data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()

def generate_signature(data: str) -> str:
    """Generate Ed25519 signature (placeholder - implement with actual crypto)"""
    # In production, implement proper Ed25519 signing
    return hashlib.sha256(f"signature_{data}".encode()).hexdigest()

async def start_job(identifier_from_purchaser: str, input_data: dict) -> Dict[str, Any]:
    """
    MIP-003 Compliant: Start a job on the remote crew
    
    Args:
        identifier_from_purchaser: Purchaser-defined identifier
        input_data: Input data matching the schema
    
    Returns:
        Job details with payment information
    """
    try:
        logger.info(f"Starting job for purchaser {identifier_from_purchaser}")
        
        # Generate job details
        job_id = generate_job_id()
        blockchain_identifier = generate_blockchain_identifier()
        current_time = int(time.time())
        
        # Payment timing (example values - adjust for production)
        pay_by_time = current_time + 3600  # 1 hour to pay
        submit_result_time = current_time + 7200  # 2 hours to submit result
        unlock_time = current_time + 10800  # 3 hours to unlock payment
        external_dispute_unlock_time = current_time + 86400  # 24 hours for disputes
        
        # Hash input data for integrity
        input_hash = hash_input_data(input_data)
        
        # Store job information
        job_storage[job_id] = {
            "id": job_id,
            "identifier_from_purchaser": identifier_from_purchaser,
            "input_data": input_data,
            "input_hash": input_hash,
            "status": "awaiting_payment",
            "created_at": current_time,
            "blockchain_identifier": blockchain_identifier,
            "result": None
        }
        
        logger.info(f"Job {job_id} created successfully")
        
        # Return MIP-003 compliant response
        return {
            "id": job_id,
            "blockchainIdentifier": blockchain_identifier,
            "payByTime": pay_by_time,
            "submitResultTime": submit_result_time,
            "unlockTime": unlock_time,
            "externalDisputeUnlockTime": external_dispute_unlock_time,
            "agentIdentifier": AGENT_IDENTIFIER,
            "sellerVKey": SELLER_VKEY,
            "identifierFromPurchaser": identifier_from_purchaser,
            "inputHash": input_hash
        }
        
    except Exception as e:
        logger.error(f"Error starting job: {e}")
        raise

async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    MIP-003 Compliant: Get job status
    
    Args:
        job_id: The ID of the job to check
        
    Returns:
        Job status information
    """
    if job_id not in job_storage:
        raise ValueError(f"Job {job_id} not found")
    
    job = job_storage[job_id]
    status_id = str(uuid.uuid4())
    
    response = {
        "id": status_id,
        "status": job["status"]
    }
    
    # Add result if completed
    if job["status"] == "completed" and job.get("result"):
        response["result"] = job["result"]
    
    # Add input schema if awaiting input (not used in our current implementation)
    if job["status"] == "awaiting_input":
        response["input_schema"] = get_input_schema()
    
    return response

async def provide_input(job_id: str, status_id: str, input_data: dict) -> Dict[str, Any]:
    """
    MIP-003 Compliant: Provide additional input for a job
    
    Args:
        job_id: Job ID awaiting input
        status_id: Status ID awaiting input
        input_data: Additional input data
        
    Returns:
        Input confirmation with hash and signature
    """
    if job_id not in job_storage:
        raise ValueError(f"Job {job_id} not found")
    
    job = job_storage[job_id]
    
    if job["status"] != "awaiting_input":
        raise ValueError(f"Job {job_id} is not awaiting input")
    
    # Hash the input data
    input_hash = hash_input_data(input_data)
    
    # Generate signature
    signature = generate_signature(f"{job_id}_{status_id}_{input_hash}")
    
    # Update job with additional input
    job["additional_input"] = input_data
    job["status"] = "running"
    
    return {
        "inputHash": input_hash,
        "signature": signature
    }

async def check_availability() -> Dict[str, Any]:
    """
    MIP-003 Compliant: Check server availability
    
    Returns:
        Server availability status
    """
    try:
        # Check if outreach service is available
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{OUTREACH_SERVICE_URL}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    return {
                        "status": "available",
                        "type": "masumi-agent",
                        "message": "Intent-Driven Cold Outreach Agent is ready to accept jobs"
                    }
                else:
                    return {
                        "status": "unavailable",
                        "type": "masumi-agent",
                        "message": "Outreach service is not responding"
                    }
    except Exception as e:
        logger.error(f"Availability check failed: {e}")
        return {
            "status": "unavailable",
            "type": "masumi-agent",
            "message": f"Service unavailable: {str(e)}"
        }

def get_input_schema() -> list:
    """
    MIP-003 Compliant: Get input schema for the service
    New schema-validator format with direct list return (not wrapped)
    
    Returns:
        Input schema definition as a list
    """
    return [
        {
            "id": "name",
            "type": "text",
            "name": "Full Name",
            "data": {
                "placeholder": "Enter your full name",
                "description": "Your complete name as it appears on official documents"
            },
            "validations": [
                {"validation": "min", "value": "2"},
                {"validation": "max", "value": "100"}
            ]
        },
        {
            "id": "email",
            "type": "email",
            "name": "Email Address",
            "data": {
                "placeholder": "your.email@example.com",
                "description": "Your primary email address"
            },
            "validations": [
                {"validation": "format", "value": "email"}
            ]
        },
        {
            "id": "age",
            "type": "number",
            "name": "Age",
            "data": {
                "description": "Your current age (optional)"
            },
            "validations": [
                {"validation": "optional", "value": "boolean"},
                {"validation": "min", "value": "18"},
                {"validation": "max", "value": "120"},
                {"validation": "format", "value": "integer"}
            ]
        },
        {
            "id": "interests",
            "type": "option",
            "name": "Interests",
            "data": {
                "description": "Select your areas of interest",
                "values": ["Technology", "Sports", "Music", "Art", "Science", "Travel"]
            },
            "validations": [
                {"validation": "min", "value": "1"},
                {"validation": "max", "value": "3"}
            ]
        },
        {
            "id": "newsletter",
            "type": "boolean",
            "name": "Newsletter Subscription",
            "data": {
                "description": "Subscribe to our newsletter for updates (optional)"
            },
            "validations": [
                {"validation": "optional", "value": "boolean"}
            ]
        }
    ]

def get_demo_data() -> Dict[str, Any]:
    """
    MIP-003 Compliant: Get demo data for marketing purposes
    Uses new schema-validator format fields
    
    Returns:
        Example input and output data
    """
    return {
        "input": {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "age": 35,
            "interests": ["Technology", "Science"],
            "newsletter": True
        },
        "output": {
            "result": "Demo output: User profile created successfully for John Smith with interests in Technology and Science."
        }
    }

async def process_outreach_job(job_id: str) -> None:
    """
    Process the job with new schema-validator format input
    Handles the new flat input fields: name, email, age, interests, newsletter
    
    Args:
        job_id: The job ID to process
    """
    if job_id not in job_storage:
        logger.error(f"Job {job_id} not found for processing")
        return
    
    job = job_storage[job_id]
    
    try:
        # Update status to running
        job["status"] = "running"
        logger.info(f"Processing job {job_id}")
        
        # Extract input data with new schema fields
        input_data = job["input_data"]
        
        # Validate required fields from new schema
        name = input_data.get("name", "")
        email = input_data.get("email", "")
        age = input_data.get("age")
        interests = input_data.get("interests", [])
        newsletter = input_data.get("newsletter", False)
        
        if not name or not email:
            job["status"] = "failed"
            job["result"] = "Invalid input data: name and email are required"
            logger.error(f"Job {job_id} failed: missing required fields")
            return
        
        # Process the job (simplified demo processing)
        # In a real implementation, this would call the appropriate service
        result = {
            "success": True,
            "message": f"Profile created for {name}",
            "data": {
                "name": name,
                "email": email,
                "age": age,
                "interests": interests,
                "newsletter_subscribed": newsletter,
                "processed_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        job["status"] = "completed"
        job["result"] = json.dumps(result)
        logger.info(f"Job {job_id} completed successfully")
                    
    except Exception as e:
        job["status"] = "failed"
        job["result"] = f"Processing error: {str(e)}"
        logger.error(f"Job {job_id} failed with exception: {e}")

# Legacy function for backward compatibility
async def process_job(identifier_from_purchaser: str, input_data: dict) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility with existing Masumi SDK
    """
    try:
        # Start the job
        job_response = await start_job(identifier_from_purchaser, input_data)
        job_id = job_response["id"]
        
        # Simulate payment received (in production, this would be handled by payment system)
        if job_id in job_storage:
            job_storage[job_id]["status"] = "running"
        
        # Process the job
        await process_outreach_job(job_id)
        
        # Get the result
        if job_id in job_storage:
            job = job_storage[job_id]
            if job["status"] == "completed":
                return {
                    "success": True,
                    "data": json.loads(job["result"]) if job["result"] else {},
                    "processingMetadata": {
                        "jobId": job_id,
                        "purchaserIdentifier": identifier_from_purchaser,
                        "processedAt": datetime.utcnow().isoformat(),
                        "serviceUrl": OUTREACH_SERVICE_URL
                    }
                }
            else:
                return {
                    "success": False,
                    "error": job.get("result", "Job processing failed"),
                    "code": "PROCESSING_FAILED"
                }
        
        return {
            "success": False,
            "error": "Job not found after processing",
            "code": "JOB_NOT_FOUND"
        }
        
    except Exception as e:
        logger.error(f"Legacy process_job failed: {e}")
        return {
            "success": False,
            "error": f"Processing error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the MIP-003 compliant agent
    import asyncio
    
    async def test_mip003_agent():
        print("🧪 Testing MIP-003 Compliant Agent")
        
        # Test availability
        availability = await check_availability()
        print(f"Availability: {availability}")
        
        # Test input schema
        schema = get_input_schema()
        print(f"Input Schema: {json.dumps(schema, indent=2)}")
        
        # Test demo data
        demo = get_demo_data()
        print(f"Demo Data: {json.dumps(demo, indent=2)}")
        
        # Test job workflow
        test_input = demo["input"]
        job_response = await start_job("test-purchaser", test_input)
        print(f"Job Started: {job_response}")
        
        job_id = job_response["id"]
        
        # Check initial status
        status = await get_job_status(job_id)
        print(f"Initial Status: {status}")
        
        # Simulate payment and process job
        if job_id in job_storage:
            job_storage[job_id]["status"] = "running"
        
        await process_outreach_job(job_id)
        
        # Check final status
        final_status = await get_job_status(job_id)
        print(f"Final Status: {final_status}")
    
    asyncio.run(test_mip003_agent())

