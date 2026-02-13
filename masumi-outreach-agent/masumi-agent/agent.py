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
        
        # Load and validate environment variables with strict MIP-003 compliance
        agent_identifier = os.getenv("AGENT_IDENTIFIER", "").strip()
        seller_vkey = os.getenv("SELLER_VKEY", "").strip()
        
        # Validate required environment variables
        if not agent_identifier:
            raise ValueError("AGENT_IDENTIFIER environment variable is not set or empty")
        if not seller_vkey:
            raise ValueError("SELLER_VKEY environment variable is not set or empty")
        
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
        
        # Return MIP-003 compliant response with cleaned values
        return {
            "id": job_id,
            "blockchainIdentifier": blockchain_identifier,
            "payByTime": pay_by_time,
            "submitResultTime": submit_result_time,
            "unlockTime": unlock_time,
            "externalDisputeUnlockTime": external_dispute_unlock_time,
            "agentIdentifier": agent_identifier,
            "sellerVKey": seller_vkey,
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
    New schema-validator format compatible with https://docs.masumi.network/documentation/technical-documentation/schema-validator-component
    Returns a list directly (not wrapped in {"input_data": [...]})
    
    Returns:
        Input schema definition as a list
    """
    return [
        {
            "id": "prospect_name",
            "type": "text",
            "name": "Prospect Name",
            "data": {
                "placeholder": "Enter full name",
                "description": "Full name of the prospect"
            },
            "validations": [
                {"validation": "min", "value": "2"},
                {"validation": "max", "value": "100"}
            ]
        },
        {
            "id": "prospect_email",
            "type": "email",
            "name": "Prospect Email",
            "data": {
                "placeholder": "name@company.com"
            },
            "validations": [
                {"validation": "format", "value": "email"}
            ]
        },
        {
            "id": "prospect_role",
            "type": "text",
            "name": "Prospect Role",
            "data": {
                "placeholder": "VP of Engineering"
            }
        },
        {
            "id": "company_name",
            "type": "text",
            "name": "Company Name"
        },
        {
            "id": "company_industry",
            "type": "text",
            "name": "Company Industry"
        },
        {
            "id": "company_size",
            "type": "option",
            "name": "Company Size",
            "data": {
                "values": ["startup", "small", "medium", "large", "enterprise"]
            }
        },
        {
            "id": "intent_signal",
            "type": "option",
            "name": "Primary Intent Signal",
            "data": {
                "values": [
                    "job_change",
                    "funding_event",
                    "technology_adoption",
                    "company_growth",
                    "industry_trend"
                ]
            }
        },
        {
            "id": "intent_description",
            "type": "text",
            "name": "Intent Description",
            "data": {
                "placeholder": "Describe the signal..."
            }
        }
    ]

def get_demo_data() -> Dict[str, Any]:
    """
    MIP-003 Compliant: Get demo data for marketing purposes
    Uses new schema-validator format with outreach-specific fields
    
    Returns:
        Example input and output data
    """
    return {
        "input": {
            "prospect_name": "John Smith",
            "prospect_email": "john.smith@techcorp.com",
            "prospect_role": "VP of Engineering",
            "company_name": "TechCorp Inc",
            "company_industry": "Software",
            "company_size": "medium",
            "intent_signal": "funding_event",
            "intent_description": "Company raised Series B funding"
        },
        "output": {
            "result": "Hi John,\n\nI saw that TechCorp Inc recently raised Series B funding - congratulations on this significant milestone! Given your role as VP of Engineering and the company's growth trajectory, I thought you might be interested in discussing how leading engineering teams are scaling their infrastructure during rapid expansion phases.\n\nI'd love to share some insights that might be relevant to your current priorities, particularly around cloud migration strategies that other Series B companies have found effective.\n\nWould you be open to a brief conversation about this?\n\nBest regards"
        }
    }

async def process_outreach_job(job_id: str) -> None:
    """
    Process the actual outreach job by calling the Node.js service
    Handles flat input from new schema-validator format and reconstructs structured format internally
    
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
        logger.info(f"Processing outreach job {job_id}")
        
        # Extract input data
        input_data = job["input_data"]
        
        # Check if input is already in structured format (backward compatibility)
        if "prospectData" in input_data and "intentSignals" in input_data:
            # Already structured format
            prospect_data = input_data.get("prospectData")
            intent_signals = input_data.get("intentSignals", [])
        else:
            # Flat format from new schema-validator - reconstruct structured format
            prospect_data = {
                "role": input_data.get("prospect_role", ""),
                "companyContext": {
                    "name": input_data.get("company_name", ""),
                    "industry": input_data.get("company_industry", "Technology"),
                    "size": input_data.get("company_size", "medium")
                },
                "contactDetails": {
                    "name": input_data.get("prospect_name", ""),
                    "email": input_data.get("prospect_email", "")
                }
            }
            
            # Reconstruct intent signals from flat fields
            # Node.js service requires at least 2 intent signals
            intent_signal_type = input_data.get("intent_signal", "company_growth")
            intent_description = input_data.get("intent_description", "Recent company activity")
            
            # Primary intent signal from user input
            primary_signal = {
                "type": intent_signal_type,
                "description": intent_description,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "relevanceScore": 0.8,
                "source": "User Input"
            }
            
            # Secondary signal inferred from company context (required by Node.js service)
            company_size = input_data.get("company_size", "medium")
            secondary_signal = {
                "type": "company_growth",
                "description": f"Company size: {company_size} - indicates growth stage and potential",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "relevanceScore": 0.6,
                "source": "Company Context"
            }
            
            intent_signals = [primary_signal, secondary_signal]
        
        # Validate required fields
        if not prospect_data or not intent_signals:
            job["status"] = "failed"
            job["result"] = "Invalid input data: missing required fields"
            return
        
        # Prepare request for the outreach service
        outreach_request = {
            "prospectData": prospect_data,
            "intentSignals": intent_signals
        }
        
        # Call the Intent-Driven Cold Outreach Agent service
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OUTREACH_SERVICE_URL}/agent/outreach",
                json=outreach_request,
                timeout=aiohttp.ClientTimeout(total=OUTREACH_TIMEOUT),
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Format result for MIP-003 compliance
                    if result.get("success"):
                        data = result.get("data", {})
                        formatted_result = {
                            "intentConfidence": data.get("intentConfidence"),
                            "reasoningSummary": data.get("reasoningSummary"),
                            "recommendedMessage": data.get("recommendedMessage"),
                            "alternativeMessages": data.get("alternativeMessages", []),
                            "suggestedFollowUpTiming": data.get("suggestedFollowUpTiming"),
                            "processingMetadata": data.get("processingMetadata", {})
                        }
                        
                        job["status"] = "completed"
                        job["result"] = json.dumps(formatted_result)
                        logger.info(f"Job {job_id} completed successfully")
                    else:
                        job["status"] = "failed"
                        job["result"] = f"Outreach processing failed: {result.get('error', {}).get('message', 'Unknown error')}"
                        logger.error(f"Job {job_id} failed: {job['result']}")
                else:
                    error_data = await response.json()
                    job["status"] = "failed"
                    job["result"] = f"Service error {response.status}: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    logger.error(f"Job {job_id} failed with HTTP {response.status}")
                    
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

