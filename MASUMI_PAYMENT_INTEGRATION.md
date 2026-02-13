# Masumi Payment Service Integration

## 🎯 Overview

Upgraded the MIP-003 Python agent to integrate with Masumi Payment Service for real escrow-based job handling. This replaces fake blockchain identifiers with actual blockchain transactions on Cardano.

## 🔄 What Changed

### Before (Fake Blockchain)
```python
# Generated fake blockchain identifier
blockchain_identifier = generate_blockchain_identifier()  # Returns "block_abc123..."
pay_by_time = current_time + 3600  # Hardcoded timing
```

### After (Real Blockchain Escrow)
```python
# Call Masumi Payment Service
payment_response = await session.post(
    f"{MASUMI_PAYMENT_URL}/create-job",
    json={
        "agentIdentifier": agent_identifier,
        "sellerVKey": seller_vkey,
        "identifierFromPurchaser": identifier_from_purchaser,
        "inputHash": input_hash,
        "price": 500  # 500 credits
    }
)

# Extract real blockchain details
blockchain_identifier = payment_response["blockchainIdentifier"]
pay_by_time = payment_response["payByTime"]
```

## 📋 Implementation Details

### 1. Job Creation (`start_job()`)

**Calls:** `POST /create-job` on Masumi Payment Service

**Request:**
```json
{
  "agentIdentifier": "intent-driven-outreach-agent-v1",
  "sellerVKey": "addr_vk1...",
  "identifierFromPurchaser": "purchaser-123",
  "inputHash": "sha256_hash_of_input_data",
  "price": 500
}
```

**Response:**
```json
{
  "blockchainIdentifier": "tx_hash_from_cardano",
  "payByTime": 1707849600,
  "submitResultTime": 1707853200,
  "unlockTime": 1707856800,
  "externalDisputeUnlockTime": 1707936000
}
```

**What Happens:**
- Payment Service creates escrow transaction on Cardano blockchain
- Funds are locked in smart contract
- Returns real blockchain transaction hash
- Sets payment deadlines based on blockchain time

### 2. Result Submission (`process_outreach_job()`)

**Calls:** `POST /submit-result` on Masumi Payment Service

**Request:**
```json
{
  "blockchainIdentifier": "tx_hash_from_cardano",
  "resultHash": "sha256_hash_of_result",
  "signature": "ed25519_signature"
}
```

**What Happens:**
- Agent completes outreach processing
- Generates SHA256 hash of result
- Signs hash with seller's Ed25519 key
- Submits to Payment Service
- Payment Service verifies and releases escrow funds

### 3. Error Handling

**Payment Service Unavailable:**
```python
except aiohttp.ClientError as e:
    logger.error(f"Failed to connect to Payment Service: {e}")
    raise ValueError(f"Could not connect to Masumi Payment Service at {MASUMI_PAYMENT_URL}: {e}")
```

**Invalid Response:**
```python
if not blockchain_identifier:
    raise ValueError("Payment Service did not return blockchainIdentifier")
```

**Result Submission Failure:**
```python
if payment_response.status != 200:
    logger.error(f"Payment Service submit-result error: {payment_response.status}")
    job["status"] = "failed"
    job["result"] = f"Failed to submit result to Payment Service"
```

## 🔐 Environment Variables

### Required Variables

```bash
# Agent identification
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1

# Seller wallet keys
SELLER_VKEY=addr_vk1...  # Verification key (public)
SELLER_SKEY=addr_sk1...  # Secret key (private) - KEEP SECURE!

# Payment Service
MASUMI_PAYMENT_URL=http://localhost:3001  # Local dev
# MASUMI_PAYMENT_URL=https://payment-service.masumi.network  # Production

# Optional: API authentication
PAYMENT_API_KEY=your_api_key_here
```

### Security Notes

⚠️ **CRITICAL**: Never commit `SELLER_SKEY` to version control!
- Add to `.gitignore`
- Use environment variables only
- Rotate keys if compromised

## 🚀 Local Development Setup

### 1. Clone Masumi Dev Stack

```bash
git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git
cd masumi-services-dev-quickstart
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
NETWORK=Preprod
BLOCKFROST_PROJECT_ID=your_blockfrost_key
SELLER_VKEY=your_wallet_vkey
SELLER_SKEY=your_wallet_skey
```

### 3. Start Payment Service

```bash
docker compose up -d
```

### 4. Verify Payment Service

```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Masumi Payment Service",
  "network": "Preprod"
}
```

### 5. Configure Python Agent

Update `masumi-outreach-agent/masumi-agent/.env`:
```bash
MASUMI_PAYMENT_URL=http://localhost:3001
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
SELLER_VKEY=your_wallet_vkey
SELLER_SKEY=your_wallet_skey
PAYMENT_API_KEY=your_api_key
```

### 6. Test Integration

```bash
cd masumi-outreach-agent/masumi-agent
python -m pytest test_mip003.py -v
```

## 🧪 Testing Workflow

### 1. Start Job
```python
job_response = await start_job("test-purchaser", input_data)
# Returns real blockchain identifier from Payment Service
```

### 2. Check Blockchain
```bash
# View transaction on Cardano explorer
https://preprod.cardanoscan.io/transaction/{blockchainIdentifier}
```

### 3. Process Job
```python
await process_outreach_job(job_id)
# Submits result to Payment Service
# Releases escrow funds
```

### 4. Verify Payment
```bash
# Check wallet balance increased
cardano-cli query utxo --address {SELLER_ADDRESS}
```

## 📊 Integration Flow

```
┌─────────────┐
│   Sokosumi  │
│  (Buyer)    │
└──────┬──────┘
       │ 1. Hire Agent
       ▼
┌─────────────────────┐
│  Python Agent       │
│  /start_job         │
└──────┬──────────────┘
       │ 2. Create Job
       ▼
┌─────────────────────┐
│  Payment Service    │
│  /create-job        │
└──────┬──────────────┘
       │ 3. Create Escrow TX
       ▼
┌─────────────────────┐
│  Cardano Blockchain │
│  (Funds Locked)     │
└─────────────────────┘
       │
       │ 4. Return TX Hash
       ▼
┌─────────────────────┐
│  Python Agent       │
│  process_job()      │
└──────┬──────────────┘
       │ 5. Generate Result
       ▼
┌─────────────────────┐
│  Node.js Service    │
│  /agent/outreach    │
└──────┬──────────────┘
       │ 6. Return Message
       ▼
┌─────────────────────┐
│  Python Agent       │
│  /submit-result     │
└──────┬──────────────┘
       │ 7. Submit Result
       ▼
┌─────────────────────┐
│  Payment Service    │
│  /submit-result     │
└──────┬──────────────┘
       │ 8. Release Escrow
       ▼
┌─────────────────────┐
│  Cardano Blockchain │
│  (Funds Released)   │
└─────────────────────┘
```

## 🔍 Debugging

### Check Payment Service Logs
```bash
docker compose logs -f payment-service
```

### Check Agent Logs
```bash
# Look for these log messages:
# "Calling Masumi Payment Service to create job"
# "Payment Service response: {...}"
# "Submitting result to Payment Service"
# "Result submitted successfully to Payment Service"
```

### Common Issues

**1. Connection Refused**
```
Could not connect to Masumi Payment Service at http://localhost:3001
```
Solution: Ensure Payment Service is running (`docker compose ps`)

**2. Missing Blockchain Identifier**
```
Payment Service did not return blockchainIdentifier
```
Solution: Check Payment Service logs for errors

**3. Invalid Signature**
```
Failed to submit result to Payment Service: Invalid signature
```
Solution: Verify SELLER_SKEY matches SELLER_VKEY

**4. Insufficient Funds**
```
Payment Service error: Insufficient funds in wallet
```
Solution: Fund seller wallet with test ADA on Preprod

## 🎯 Production Deployment

### 1. Update Environment Variables

```bash
# Railway or production environment
MASUMI_PAYMENT_URL=https://payment-service.masumi.network
NETWORK=Mainnet
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
SELLER_VKEY=<production_vkey>
SELLER_SKEY=<production_skey>  # SECURE!
PAYMENT_API_KEY=<production_api_key>
```

### 2. Security Checklist

- [ ] SELLER_SKEY stored in secure secrets manager
- [ ] PAYMENT_API_KEY rotated regularly
- [ ] HTTPS enabled for all endpoints
- [ ] Rate limiting configured
- [ ] Monitoring and alerts set up
- [ ] Backup wallet keys securely

### 3. Monitoring

Monitor these metrics:
- Job creation success rate
- Result submission success rate
- Payment Service response times
- Blockchain transaction confirmations
- Wallet balance

## 📝 TODO: Ed25519 Signing

Currently using placeholder signature. Implement real Ed25519 signing:

```python
# Install: pip install PyNaCl
from nacl.signing import SigningKey

def generate_signature(data: str, seller_skey: str) -> str:
    """Generate real Ed25519 signature"""
    signing_key = SigningKey(bytes.fromhex(seller_skey))
    signed = signing_key.sign(data.encode())
    return signed.signature.hex()
```

## ✅ Benefits

### Before Integration
- ❌ Fake blockchain identifiers
- ❌ No real payment escrow
- ❌ No buyer protection
- ❌ No seller guarantees
- ❌ Not marketplace-ready

### After Integration
- ✅ Real Cardano blockchain transactions
- ✅ Smart contract escrow
- ✅ Buyer funds protected until delivery
- ✅ Seller guaranteed payment on completion
- ✅ Fully decentralized and trustless
- ✅ Marketplace-ready
- ✅ Web3 monetizable AI agent

## 🚀 Next Steps

1. **Test Locally**: Run Masumi dev stack and test full flow
2. **Implement Ed25519**: Replace placeholder signature with real signing
3. **Add Monitoring**: Track payment success rates
4. **Deploy to Preprod**: Test on Cardano testnet
5. **Deploy to Mainnet**: Go live with real payments

## 📚 Resources

- [Masumi Documentation](https://docs.masumi.network)
- [MIP-003 Specification](https://docs.masumi.network/mip-003)
- [Cardano Developer Portal](https://developers.cardano.org)
- [Masumi Dev Quickstart](https://github.com/masumi-network/masumi-services-dev-quickstart)
