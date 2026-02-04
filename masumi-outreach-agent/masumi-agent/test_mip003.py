#!/usr/bin/env python3
"""
Test script for MIP-003 Compliant Intent-Driven Cold Outreach Agent
Tests all required MIP-003 Agentic Service API Standard endpoints
"""
import asyncio
import json
import sys
import aiohttp
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8080"
TIMEOUT = 30

# Test data
TEST_INPUT_DATA = {
    "prospectData": {
        "role": "VP of Engineering",
        "companyContext": {
            "name": "TechCorp Inc",
            "industry": "Software",
            "size": "medium"
        },
        "contactDetails": {
            "name": "John Smith",
            "email": "john.smith@techcorp.com"
        }
    },
    "intentSignals": [
        {
            "type": "funding_event",
            "description": "Company raised Series B funding",
            "timestamp": "2024-01-15T00:00:00.000Z",
            "relevanceScore": 0.9,
            "source": "TechCrunch"
        },
        {
            "type": "technology_adoption",
            "description": "Migrating to cloud infrastructure",
            "timestamp": "2024-01-10T00:00:00.000Z",
            "relevanceScore": 0.8,
            "source": "LinkedIn"
        }
    ]
}

async def make_request(method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, str] = None) -> Dict[str, Any]:
    """Make HTTP request to the API"""
    url = f"{BASE_URL}{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        if method.upper() == "GET":
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as response:
                return {
                    "status": response.status,
                    "data": await response.json() if response.content_type == "application/json" else await response.text()
                }
        elif method.upper() == "POST":
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as response:
                return {
                    "status": response.status,
                    "data": await response.json() if response.content_type == "application/json" else await response.text()
                }

async def test_availability():
    """Test MIP-003 Required: /availability endpoint"""
    print("🔍 Testing /availability endpoint...")
    
    try:
        result = await make_request("GET", "/availability")
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Availability check successful")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Type: {data.get('type', 'unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            return data.get('status') == 'available'
        else:
            print(f"❌ Availability check failed with status {result['status']}")
            return False
            
    except Exception as e:
        print(f"❌ Availability check failed with error: {e}")
        return False

async def test_input_schema():
    """Test MIP-003 Required: /input_schema endpoint"""
    print("\n📋 Testing /input_schema endpoint...")
    
    try:
        result = await make_request("GET", "/input_schema")
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Input schema retrieved successfully")
            print(f"   Fields: {len(data.get('input_data', []))}")
            
            # Validate schema structure
            input_data = data.get('input_data', [])
            required_fields = ['prospectData', 'intentSignals']
            found_fields = [field.get('id') for field in input_data]
            
            if all(field in found_fields for field in required_fields):
                print(f"   Required fields present: {required_fields}")
                return True
            else:
                print(f"   Missing required fields. Found: {found_fields}")
                return False
        else:
            print(f"❌ Input schema retrieval failed with status {result['status']}")
            return False
            
    except Exception as e:
        print(f"❌ Input schema retrieval failed with error: {e}")
        return False

async def test_demo_data():
    """Test MIP-003 Optional: /demo endpoint"""
    print("\n🎭 Testing /demo endpoint...")
    
    try:
        result = await make_request("GET", "/demo")
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Demo data retrieved successfully")
            
            if "input" in data and "output" in data:
                print(f"   Has input example: ✅")
                print(f"   Has output example: ✅")
                return True
            else:
                print(f"   Missing input or output examples")
                return False
        else:
            print(f"❌ Demo data retrieval failed with status {result['status']}")
            return False
            
    except Exception as e:
        print(f"❌ Demo data retrieval failed with error: {e}")
        return False

async def test_start_job():
    """Test MIP-003 Required: /start_job endpoint"""
    print("\n🚀 Testing /start_job endpoint...")
    
    try:
        request_data = {
            "identifier_from_purchaser": "test-purchaser-mip003",
            "input_data": TEST_INPUT_DATA
        }
        
        result = await make_request("POST", "/start_job", data=request_data)
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Job started successfully")
            print(f"   Job ID: {data.get('id', 'unknown')}")
            print(f"   Blockchain ID: {data.get('blockchainIdentifier', 'unknown')}")
            print(f"   Agent ID: {data.get('agentIdentifier', 'unknown')}")
            print(f"   Input Hash: {data.get('inputHash', 'unknown')}")
            
            # Validate required fields
            required_fields = ['id', 'blockchainIdentifier', 'payByTime', 'submitResultTime', 
                             'unlockTime', 'externalDisputeUnlockTime', 'agentIdentifier', 
                             'sellerVKey', 'identifierFromPurchaser', 'inputHash']
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print(f"   All required fields present ✅")
                return data.get('id')
            else:
                print(f"   Missing required fields: {missing_fields}")
                return None
        else:
            print(f"❌ Job start failed with status {result['status']}")
            print(f"   Error: {result.get('data', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Job start failed with error: {e}")
        return None

async def test_job_status(job_id: str):
    """Test MIP-003 Required: /status endpoint"""
    print(f"\n📊 Testing /status endpoint for job {job_id}...")
    
    try:
        result = await make_request("GET", "/status", params={"job_id": job_id})
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Job status retrieved successfully")
            print(f"   Status ID: {data.get('id', 'unknown')}")
            print(f"   Status: {data.get('status', 'unknown')}")
            
            if data.get('result'):
                print(f"   Has result: ✅")
            
            return data.get('status')
        elif result["status"] == 404:
            print(f"❌ Job not found")
            return None
        else:
            print(f"❌ Status retrieval failed with status {result['status']}")
            return None
            
    except Exception as e:
        print(f"❌ Status retrieval failed with error: {e}")
        return None

async def test_health_check():
    """Test additional health check endpoint"""
    print("\n🏥 Testing /health endpoint...")
    
    try:
        result = await make_request("GET", "/health")
        
        if result["status"] == 200:
            data = result["data"]
            print(f"✅ Health check successful")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Service: {data.get('service', 'unknown')}")
            print(f"   MIP-003 Compliant: {data.get('mip003_compliant', False)}")
            return True
        else:
            print(f"❌ Health check failed with status {result['status']}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        return False

async def test_job_workflow():
    """Test complete job workflow"""
    print("\n🔄 Testing complete job workflow...")
    
    # Start job
    job_id = await test_start_job()
    if not job_id:
        return False
    
    # Check initial status
    initial_status = await test_job_status(job_id)
    if not initial_status:
        return False
    
    print(f"   Initial status: {initial_status}")
    
    # Wait for automatic payment simulation and processing
    print("   Waiting for automatic payment simulation and processing...")
    
    # Check status multiple times to see progression
    for i in range(10):  # Increased from 5 to 10 attempts
        await asyncio.sleep(3)
        status = await test_job_status(job_id)
        print(f"   Status check {i+1}: {status}")
        
        if status == "completed":
            print("✅ Job completed successfully!")
            return True
        elif status == "failed":
            print("❌ Job failed")
            return False
        elif status == "running":
            print("   Job is now running, waiting for completion...")
    
    print("⚠️  Job still processing after timeout")
    return False

async def main():
    """Run all MIP-003 compliance tests"""
    print("🚀 MIP-003 Agentic Service API Standard Compliance Test")
    print("=" * 70)
    print()
    
    tests = [
        ("Availability Check", test_availability),
        ("Input Schema", test_input_schema),
        ("Demo Data", test_demo_data),
        ("Health Check", test_health_check),
        ("Job Workflow", test_job_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 MIP-003 Compliance Test Results:")
    print()
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All MIP-003 compliance tests PASSED!")
        print("✅ Agent is fully compliant with MIP-003 Agentic Service API Standard")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests FAILED")
        print("❌ Agent needs fixes to be MIP-003 compliant")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test suite failed with error: {e}")
        sys.exit(1)