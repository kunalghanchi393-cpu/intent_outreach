# MIP-003 Environment Variable Validation Fix

## 🔥 Critical Issues Fixed

### Problems Detected
1. **sellerVKey returning empty string** - Must return a valid value from environment
2. **agentIdentifier contains trailing newline (\n)** - Must strip whitespace
3. **No validation** - Empty values were being returned without error

### Impact
- Sokosumi could not start jobs due to invalid MIP-003 response
- Empty `sellerVKey` violated MIP-003 specification
- Trailing whitespace in `agentIdentifier` caused parsing issues

## ✅ Solution Implemented

### 1. Removed Global Constants
**Before:**
```python
# Configuration
AGENT_IDENTIFIER = os.getenv("AGENT_IDENTIFIER", "intent-driven-outreach-agent-v1")
SELLER_VKEY = os.getenv("SELLER_VKEY", "")
```

**After:**
```python
# Configuration
OUTREACH_SERVICE_URL = os.getenv("OUTREACH_SERVICE_URL", "http://localhost:3000")
OUTREACH_TIMEOUT = int(os.getenv("OUTREACH_TIMEOUT", "30"))
# AGENT_IDENTIFIER and SELLER_VKEY now loaded per-request with validation
```

### 2. Added Per-Request Validation in `start_job()`
```python
async def start_job(identifier_from_purchaser: str, input_data: dict) -> Dict[str, Any]:
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
        
        # ... rest of function
        
        # Return MIP-003 compliant response with cleaned values
        return {
            "id": job_id,
            "blockchainIdentifier": blockchain_identifier,
            "payByTime": pay_by_time,
            "submitResultTime": submit_result_time,
            "unlockTime": unlock_time,
            "externalDisputeUnlockTime": external_dispute_unlock_time,
            "agentIdentifier": agent_identifier,  # Cleaned value
            "sellerVKey": seller_vkey,            # Cleaned value
            "identifierFromPurchaser": identifier_from_purchaser,
            "inputHash": input_hash
        }
```

### 3. Updated `.env.example` Documentation
```bash
# ============================================
# MASUMI CONFIGURATION (REQUIRED)
# ============================================
# REQUIRED: Agent identifier for MIP-003 compliance
# Must be set to a non-empty value (no trailing whitespace)
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1

# REQUIRED: Seller verification key for MIP-003 compliance
# Must be set to a non-empty value (no trailing whitespace)
# Get this from Masumi admin interface
SELLER_VKEY=

# REQUIRED for production: Payment API key
PAYMENT_API_KEY=
```

## 🎯 What This Fixes

### Before
```json
{
  "agentIdentifier": "intent-driven-outreach-agent-v1\n",  // ❌ Trailing newline
  "sellerVKey": ""  // ❌ Empty string
}
```

### After
```json
{
  "agentIdentifier": "intent-driven-outreach-agent-v1",  // ✅ Clean value
  "sellerVKey": "actual_vkey_value"  // ✅ Valid value or error
}
```

## ✅ Validation Behavior

### Valid Configuration
If environment variables are properly set:
```bash
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
SELLER_VKEY=vkey1abc123xyz
```

Response:
```json
{
  "agentIdentifier": "intent-driven-outreach-agent-v1",
  "sellerVKey": "vkey1abc123xyz"
}
```

### Invalid Configuration
If environment variables are missing or empty:
```bash
AGENT_IDENTIFIER=
SELLER_VKEY=
```

Response:
```json
{
  "detail": "AGENT_IDENTIFIER environment variable is not set or empty"
}
```
HTTP Status: 500

## 🔒 Security & Compliance

### MIP-003 Requirements Met
- ✅ `agentIdentifier` is non-empty string
- ✅ `sellerVKey` is non-empty string
- ✅ No trailing whitespace
- ✅ No leading whitespace
- ✅ Validation on every request
- ✅ Clear error messages

### Best Practices
- ✅ Per-request validation (not just startup)
- ✅ Explicit error messages
- ✅ `.strip()` removes all whitespace
- ✅ Environment variables documented
- ✅ No default empty values allowed

## 🚀 Deployment Checklist

Before deploying to production:

1. **Set Environment Variables in Railway:**
   ```bash
   AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
   SELLER_VKEY=<your_actual_vkey>
   ```

2. **Verify No Trailing Whitespace:**
   - Check Railway dashboard
   - Ensure no newlines or spaces at end of values

3. **Test `/start_job` Endpoint:**
   ```bash
   curl -X POST https://your-railway-url/start_job \
     -H "Content-Type: application/json" \
     -d '{
       "identifier_from_purchaser": "test",
       "input_data": {"prospect_name": "Test"}
     }'
   ```

4. **Verify Response:**
   - Check `agentIdentifier` has no `\n`
   - Check `sellerVKey` is not empty
   - Both should be clean strings

## 📋 Deployment Status

- ✅ Environment variable validation added
- ✅ `.strip()` applied to both variables
- ✅ Clear error messages for missing values
- ✅ `.env.example` updated with documentation
- ✅ Committed to master
- ✅ Pushed to GitHub
- 🔄 Railway will automatically redeploy

## ⚠️ Important Notes

1. **Railway Environment Variables:**
   - Must set `AGENT_IDENTIFIER` in Railway dashboard
   - Must set `SELLER_VKEY` in Railway dashboard
   - No trailing newlines or spaces

2. **Error Handling:**
   - Missing variables will cause 500 error
   - Error message clearly indicates which variable is missing
   - This is intentional - better to fail fast than return invalid data

3. **Testing:**
   - Test locally with `.env` file first
   - Verify Railway environment variables are set correctly
   - Check `/start_job` response before testing in Sokosumi

## 🎯 Expected Outcome

After deployment with proper environment variables:
- ✅ `/start_job` returns clean `agentIdentifier` (no whitespace)
- ✅ `/start_job` returns valid `sellerVKey` (not empty)
- ✅ Sokosumi can successfully start jobs
- ✅ Full MIP-003 compliance achieved
