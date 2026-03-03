#!/usr/bin/env python3
"""
Intent-Driven Cold Outreach Agent - Masumi SDK Integration
Migrated from custom FastAPI implementation to official Masumi SDK

This file contains the agent's business logic for processing outreach requests.
All MIP-003 protocol handling is now managed by the Masumi SDK.
"""
import os
import json
import aiohttp
import logging
from typing import Dict, Any, List
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

# Schema option mappings for converting indices to values
COMPANY_SIZE_OPTIONS = ["startup", "small", "medium", "large", "enterprise"]
INTENT_SIGNAL_OPTIONS = [
    "job_change",
    "funding_event",
    "technology_adoption",
    "company_growth",
    "industry_trend"
]

def convert_option_value(value: Any, options: List[str]) -> str:
    """
    Convert option value from Sokosumi format to actual string value.
    Sokosumi may send either:
    - A string value directly
    - An array with a single index [n]
    - An integer index n
    
    Args:
        value: The value to convert (can be str, int, or list)
        options: List of valid option values
    
    Returns:
        The actual string value from the options list
    """
    # If it's already a string and valid, return it
    if isinstance(value, str) and value in options:
        return value
    
    # If it's a list with one element (Sokosumi format)
    if isinstance(value, list) and len(value) > 0:
        index = value[0]
        if isinstance(index, int) and 0 <= index < len(options):
            return options[index]
    
    # If it's an integer index
    if isinstance(value, int) and 0 <= value < len(options):
        return options[value]
    
    # Default to first option if conversion fails
    logger.warning(f"Could not convert option value {value}, using default: {options[0]}")
    return options[0]

async def process_job(identifier_from_purchaser: str, input_data: dict) -> str:
    """
    Process an outreach job using the Intent-Driven Cold Outreach Agent workflow.
    This is the main entry point called by the Masumi SDK.
    
    The SDK handles:
    - input_hash generation
    - blockchain identifier creation
    - seller_vkey verification
    - payment polling and escrow
    - job lifecycle management
    - result submission to blockchain
    
    This function only needs to:
    - Extract and validate input
    - Call the outreach workflow
    - Return the result as a string or dict
    
    Args:
        identifier_from_purchaser: Purchaser-defined identifier
        input_data: Input data matching the schema
    
    Returns:
        Result string or dict (SDK will handle serialization)
    """
    try:
        logger.info(f"Processing outreach job for purchaser {identifier_from_purchaser}")
        
        # Check if input is already in structured format (backward compatibility)
        if "prospectData" in input_data and "intentSignals" in input_data:
            # Already structured format
            prospect_data = input_data.get("prospectData")
            intent_signals = input_data.get("intentSignals", [])
        else:
            # Flat format from schema-validator - reconstruct structured format
            # Handle Sokosumi sending array indices instead of string values
            company_size_raw = input_data.get("company_size", "medium")
            company_size = convert_option_value(company_size_raw, COMPANY_SIZE_OPTIONS)
            
            intent_signal_raw = input_data.get("intent_signal", "company_growth")
            intent_signal_type = convert_option_value(intent_signal_raw, INTENT_SIGNAL_OPTIONS)
            
            prospect_data = {
                "role": input_data.get("prospect_role", ""),
                "companyContext": {
                    "name": input_data.get("company_name", ""),
                    "industry": input_data.get("company_industry", "Technology"),
                    "size": company_size
                },
                "contactDetails": {
                    "name": input_data.get("prospect_name", ""),
                    "email": input_data.get("prospect_email", "")
                }
            }
            
            # Reconstruct intent signals from flat fields
            # Node.js service requires at least 2 intent signals
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
            raise ValueError("Invalid input data: missing required fields")
        
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
                    
                    # Format result for return
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
                        
                        # Return as JSON string (SDK will handle submission)
                        return json.dumps(formatted_result)
                    else:
                        error_msg = result.get('error', {}).get('message', 'Unknown error')
                        raise ValueError(f"Outreach processing failed: {error_msg}")
                else:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    raise ValueError(f"Service error {response.status}: {error_msg}")
                    
    except Exception as e:
        logger.error(f"Job processing failed: {e}")
        raise
