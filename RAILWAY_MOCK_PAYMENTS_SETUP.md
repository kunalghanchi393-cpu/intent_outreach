# Railway Mock Payments Setup

## 🎯 Quick Fix for Railway Deployment

Since you don't have Docker installed locally, you can use **Mock Payments Mode** to test the agent on Railway without the Payment Service.

## ⚙️ Railway Configuration

### Add This Environment Variable

Go to your Railway project dashboard and add:

```
MOCK_PAYMENTS=true
```

This will:
- ✅ Skip Payment Service connection
- ✅ Use simulated blockchain identifiers
- ✅ Allow Sokosumi to hire and test the agent
- ✅ Complete jobs successfully without real escrow

### Current Railway Environment Variables

Make sure you have these set:

```bash
# Node.js Service URL (already working)
OUTREACH_SERVICE_URL=https://intent-driven-cold-outreach-agent-production.up.railway.app

# Agent Configuration
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
SELLER_VKEY=your_vkey_here

# Mock Payments (NEW - add this!)
MOCK_PAYMENTS=true

# Network
NETWORK=Preprod
```

## 🚀 After Adding MOCK_PAYMENTS=true

Railway will automatically redeploy. Then:

1. **Test /start_job endpoint:**
   - Should return HTTP 200 (not 400)
   - Will have simulated `blockchainIdentifier`
   - No Payment Service connection needed

2. **Sokosumi can hire the agent:**
   - Jobs will be created successfully
   - Processing will complete
   - Results will be returned

3. **Check logs:**
   ```
   MOCK_PAYMENTS enabled - using simulated blockchain
   Mock blockchain ID: block_abc123...
   Job completed successfully (mock mode)
   ```

## ⚠️ Important Notes

### What Mock Mode Does
- ✅ Simulates blockchain identifiers
- ✅ Skips Payment Service API calls
- ✅ Allows full agent testing
- ✅ Completes jobs successfully

### What Mock Mode Doesn't Do
- ❌ No real blockchain transactions
- ❌ No actual escrow
- ❌ No real payments
- ❌ Not suitable for production with real money

## 🔄 Switching to Real Payments Later

When you're ready to use real blockchain payments:

### 1. Set Up Payment Service Locally

```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop/

# Clone and run Payment Service
git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git
cd masumi-services-dev-quickstart
cp .env.example .env
# Edit .env with your keys
docker compose up -d
```

### 2. Update Railway Environment Variables

```bash
# Change this:
MOCK_PAYMENTS=false

# Add Payment Service URL (when you deploy it)
MASUMI_PAYMENT_URL=https://your-payment-service.railway.app

# Add required keys
SELLER_SKEY=your_secret_key
PAYMENT_API_KEY=your_api_key
```

### 3. Deploy Payment Service to Railway

You can deploy the Payment Service to Railway too:
- Create new Railway project
- Connect masumi-services-dev-quickstart repo
- Set environment variables
- Deploy

## 📊 Current Status

### ✅ Working Now
- Node.js outreach service (deployed on Railway)
- Python Masumi agent (deployed on Railway)
- Agent can connect to Node.js service
- Mock payments mode enabled

### 🔄 Next Steps
1. Add `MOCK_PAYMENTS=true` to Railway
2. Test agent with Sokosumi
3. Verify jobs complete successfully
4. Later: Set up real Payment Service

## 🧪 Testing

### Test Availability
```bash
curl https://your-railway-url.railway.app/availability
```

Expected:
```json
{
  "status": "available",
  "type": "masumi-agent",
  "message": "Intent-Driven Cold Outreach Agent is ready to accept jobs"
}
```

### Test Job Creation
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

Expected:
```json
{
  "id": "job-uuid",
  "blockchainIdentifier": "block_simulated_123",
  "payByTime": 1707849600,
  ...
}
```

## 🎯 Summary

**Current Setup:**
- ✅ Agent deployed on Railway
- ✅ Connects to Node.js service successfully
- ⚠️ Payment Service not available (no Docker)

**Solution:**
- ✅ Add `MOCK_PAYMENTS=true` to Railway
- ✅ Agent works without Payment Service
- ✅ Can test full flow with Sokosumi

**Future:**
- 🔄 Install Docker Desktop
- 🔄 Run Payment Service locally
- 🔄 Switch to real blockchain payments
- 🔄 Deploy Payment Service to Railway

## 📝 Quick Checklist

- [ ] Add `MOCK_PAYMENTS=true` to Railway environment variables
- [ ] Wait for Railway to redeploy (2-3 minutes)
- [ ] Test `/availability` endpoint
- [ ] Test `/start_job` endpoint
- [ ] Verify no Payment Service errors in logs
- [ ] Test with Sokosumi marketplace
- [ ] Confirm jobs complete successfully

Once this is working, you can decide when to set up real blockchain payments!
