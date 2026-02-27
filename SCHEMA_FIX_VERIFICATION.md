# FastAPI Schema Fix Verification

## 🔧 Issue Fixed

There was a duplicate `FastAPI()` app definition in `main.py` that was causing schema confusion.

## ✅ What Was Fixed

### Removed Duplicate App Definition

**Before:**
```python
# FastAPI app
app = FastAPI(...)

# FastAPI app  # ← DUPLICATE!
app = FastAPI(...)
```

**After:**
```python
# FastAPI app
app = FastAPI(...)
```

## 📋 Current Schema Configuration

### Request Model (StartJobRequest)
```python
class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: Dict[str, Any]
```

### Response Model (StartJobResponse)
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

### Endpoint Definition
```python
@app.post("/start_job", response_model=StartJobResponse)
async def start_job_endpoint(request: StartJobRequest):
    """MIP-003 Required: Initiates a job on the remote crew"""
    ...
```

## ✅ Expected Swagger UI Schema

After Railway redeploys, `/docs` should show:

### Request Body Schema
```json
{
  "identifier_from_purchaser": "string",
  "input_data": {}
}
```

### Response Schema (200)
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

## 🧪 Verification Steps

### 1. Check Swagger UI

Visit: `https://your-railway-url.railway.app/docs`

1. Expand `/start_job` endpoint
2. Check "Request body" section:
   - Should show `identifier_from_purchaser` and `input_data`
   - Should NOT show response fields like `blockchain_identifier`
3. Check "Responses" → "200" section:
   - Should show all snake_case response fields

### 2. Test with Curl

```bash
curl -X POST https://your-railway-url.railway.app/start_job \
  -H "Content-Type: application/json" \
  -d '{
    "identifier_from_purchaser": "test-buyer",
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

Expected response:
```json
{
  "id": "uuid",
  "blockchain_identifier": "block_...",
  "pay_by_time": 1707849600,
  "submit_result_time": 1707853200,
  "unlock_time": 1707856800,
  "external_dispute_unlock_time": 1707936000,
  "agent_identifier": "intent-driven-outreach-agent-v1",
  "seller_vkey": "...",
  "identifier_from_purchaser": "test-buyer",
  "input_hash": "sha256_hash"
}
```

### 3. Test with Sokosumi

Sokosumi should now be able to:
- ✅ Send correct request format
- ✅ Receive correct response format
- ✅ Parse snake_case fields
- ✅ Complete job successfully

## 🎯 What This Fixes

### Before
- ❌ Duplicate FastAPI app causing schema confusion
- ❌ Swagger might show wrong request schema
- ❌ 422 validation errors possible

### After
- ✅ Single FastAPI app definition
- ✅ Correct request schema (identifier_from_purchaser + input_data)
- ✅ Correct response schema (snake_case fields)
- ✅ Full MIP-003 compliance

## 📝 Summary

The schema configuration is now correct:

1. **Request**: Uses `StartJobRequest` with `identifier_from_purchaser` and `input_data`
2. **Response**: Uses `StartJobResponse` with snake_case fields
3. **Endpoint**: Properly decorated with `response_model=StartJobResponse`
4. **No duplicates**: Single FastAPI app definition

## 🚀 Deployment

Changes committed and pushed. Railway will automatically redeploy.

After deployment, verify:
- [ ] `/docs` shows correct request schema
- [ ] `/docs` shows correct response schema
- [ ] Test request succeeds with proper format
- [ ] Response has snake_case fields
- [ ] Sokosumi can hire agent successfully
