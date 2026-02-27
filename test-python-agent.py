#!/usr/bin/env python3
"""
Test script for Python agent's outreach job processing
"""
import sys
import asyncio
sys.path.insert(0, 'masumi-outreach-agent/masumi-agent')

from agent import process_outreach_job, job_storage, generate_job_id
from datetime import datetime

async def test_outreach():
    print("🧪 Testing Python agent outreach processing...")
    
    # Create a test job
    job_id = generate_job_id()
    job_storage[job_id] = {
        "id": job_id,
        "identifier_from_purchaser": "test-purchaser",
        "input_data": {
            "prospect_name": "John Doe",
            "prospect_email": "john@company.com",
            "prospect_role": "VP Engineering",
            "company_name": "TestCorp",
            "company_industry": "Software",
            "company_size": "medium",
            "intent_signal": "funding_event",
            "intent_description": "Raised Series B"
        },
        "input_hash": "test_hash",
        "status": "awaiting_payment",
        "created_at": int(datetime.utcnow().timestamp()),
        "blockchain_identifier": "test_blockchain",
        "result": None
    }
    
    print(f"📦 Created test job: {job_id}")
    print(f"📋 Input data: {job_storage[job_id]['input_data']}")
    print("")
    
    # Process the job
    print("🔄 Processing job...")
    await process_outreach_job(job_id)
    
    # Check result
    job = job_storage[job_id]
    print(f"✅ Job status: {job['status']}")
    print(f"📥 Job result: {job.get('result', 'No result')[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_outreach())
