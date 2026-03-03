#!/usr/bin/env python3
"""
Intent-Driven Cold Outreach Agent - Masumi SDK Entry Point
Migrated from custom FastAPI implementation to official Masumi SDK

This is the entry point for the MIP-003 compliant Masumi outreach agent.
Run this file to start the agent server with the official Masumi SDK.

The SDK automatically provides:
- /start_job endpoint
- /status endpoint  
- /availability endpoint
- /input_schema endpoint
- /provide_input endpoint (optional)
- /demo endpoint (optional)
- Blockchain integration
- Payment service integration
- Job lifecycle management
"""
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from masumi import run
from agent import process_job

# Define input schema for the outreach agent
# This matches the schema-validator format from the custom implementation
INPUT_SCHEMA = {
    "input_data": [
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
}

# Main entry point
if __name__ == "__main__":
    print("🚀 Starting Intent-Driven Cold Outreach Agent (Masumi SDK)")
    print("📋 This agent processes outreach requests using a 7-step reasoning workflow")
    print("🔗 Connects to the Node.js outreach service for message generation")
    print("📡 MIP-003 Agentic Service API Standard compliant via Masumi SDK")
    print()
    
    # Run the agent with the Masumi SDK
    # The SDK automatically:
    # - Loads config from environment variables (AGENT_IDENTIFIER, SELLER_VKEY, etc.)
    # - Creates all MIP-003 required endpoints
    # - Handles blockchain integration
    # - Manages payment service communication
    # - Processes job lifecycle
    # - Submits results to blockchain
    run(
        start_job_handler=process_job,
        input_schema_handler=INPUT_SCHEMA
        # config, agent_identifier, network loaded from env vars automatically
    )
