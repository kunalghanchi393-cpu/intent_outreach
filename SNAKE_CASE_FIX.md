# MIP-003 Snake Case Response Fix

## 🔧 Issue Fixed

The `/start_job` endpoint was returning camelCase field names, but the MIP-003 platform expects snake_case.

## ❌ Before (camelCase)

```json
{
  "id": "job-uuid",
  "blockchainIdentifier": "tx_hash",
  "payByTime": 1707849600,
  "submitResultTime": 1707853200,
  "unlockTime": 1707856800,
  "externalDisputeUnlockTime": 1707936000,
  "agentIdentifier": "intent-driven-outreach-agent-v1",
  "sellerVKey": "addr_vk1...",
  "identifierFromPurchaser": "purchaser-123",
  "inputHash": "sha256_hash"
}
```

## ✅ After (snake_case)

```json
{
  "id": "job-uuid",
  "blockchain_identifier": "tx_hash",
  "pay_by_time": 1707849600,
  "submit_result_time": 1707853200,
  "unlock_time": 1707856800,
  "external_dispute_unlock_time": 1707936000,
  "agent_identifier": "intent-driven-outreach-agent-v1",
  "seller_vkey": "addr_vk1...",
  "identifier_from_purchaser": "purchaser-123",
  "input_hash": "sha256_hash"
}
```

## 📋 Changes Made

### 1. Updated Pydantic Model (`main.py`)

**Before:**
```python
class StartJobResponse(BaseModel):
    id: str
    blockchainIdentifier: str
    payByTime: int
    submitResultTime: int
    unlockTime: int
    externalDisputeUnlockTime: int
    agentIdentifier: str
    sellerVKey: str
    identifierFromPurchaser: str
    inputHash: str
```

**After:**
```python
class StartJobResponse(BaseModel):
    """MIP-003 compliant response for /start_job endpoint with snake_case fields"""
    id: str
    blockchain_identifier: str
    pay_by_time: int
    submit_result_time: int
    unlock_time: int
    external_dispute_unlock_time: int
    agent_identifier: str
    seller_vkey: str
    identifier_from_purchaser: str
    input_hash: str
```

### 2. Updated Agent Response (`agent.py`)

**Before:**
```python
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
```

**After:**
```python
return {
    "id": job_id,
    "blockchain_identifier": blockchain_identifier,
    "pay_by_time": pay_by_time,
    "submit_result_time": submit_result_time,
    "unlock_time": unlock_time,
    "external_dispute_unlock_time": external_dispute_unlock_time,
    "agent_identifier": agent_identifier,
    "seller_vkey": seller_vkey,
    "identifier_from_purchaser": identifier_from_purchaser,
    "input_hash": input_hash
}
```

## ✅ Field Mapping

| Old (camelCase) | New (snake_case) |
|----------------|------------------|
| `blockchainIdentifier` | `blockchain_identifier` |
| `payByTime` | `pay_by_time` |
| `submitResultTime` | `submit_result_time` |
| `unlockTime` | `unlock_time` |
| `externalDisputeUnlockTime` | `external_dispute_unlock_time` |
| `agentIdentifier` | `agent_identifier` |
| `sellerVKey` | `seller_vkey` |
| `identifierFromPurchaser` | `identifier_from_purchaser` |
| `inputHash` | `input_hash` |

## 🧪 Verification

### Check OpenAPI Schema

Visit: `https://your-railway-url.railway.app/docs`

Expand `/start_job` endpoint → "Responses" → "200"

Should show:
```json
{
  "id": "string",
  "blockchain_identifier": "string",
  "pay_by_time": 0,
  "submit_result_time": 0,
  "unlock_time": 0,
  "external_dispute_unlock_time": 0,
  "agent_identifier": "string",
  "seller_vkey": "string",
  "identifier_from_purchaser": "string",
  "input_hash": "string"
}
```

### Test Endpoint

```bash
curl -X POST https://your-railway-url.railway.app/start_job \
  -H "Content-Type: application/json" \
  -d '{
    "identifier_from_purchaser": "test",
    "input_data": {
      "prospect_name": "John Doe",
      "prospect_email": "john@example.com",
      "prospect_role": "VP Engineering",
      "company_name": "TestCorp",
      "company_industry": "Software",
      "company_size": "medium",
      "intent_signal": "funding_event",
      "intent_description": "Raised Series B"
    }
  }'
```

Response should have snake_case fields:
```json
{
  "id": "...",
  "blockchain_identifier": "...",
  "pay_by_time": 1707849600,
  ...
}
```

## 🎯 Impact

### Before Fix
- ❌ Platform couldn't parse camelCase fields
- ❌ Job creation might fail
- ❌ Sokosumi integration issues

### After Fix
- ✅ Platform correctly parses snake_case fields
- ✅ Job creation works as expected
- ✅ Full MIP-003 compliance
- ✅ Sokosumi integration compatible

## 📝 Notes

- All field names now use snake_case as per MIP-003 specification
- OpenAPI schema automatically updated by FastAPI
- No breaking changes to internal logic
- Only response format changed

## 🚀 Deployment

Changes committed and pushed to master. Railway will automatically redeploy.

After deployment:
- ✅ `/start_job` returns snake_case fields
- ✅ OpenAPI docs show correct schema
- ✅ Platform can parse responses correctly
- ✅ Full MIP-003 compliance achieved
