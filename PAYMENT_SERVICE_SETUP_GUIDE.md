# Masumi Payment Service - Quick Setup Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone Masumi Dev Stack

```bash
git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git
cd masumi-services-dev-quickstart
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```


Edit `.env` file:
```bash
# Network Configuration
NETWORK=Preprod

# Blockfrost API (Get free key from https://blockfrost.io)
BLOCKFROST_PROJECT_ID=preprodYourProjectIdHere

# Your Cardano Wallet Keys
SELLER_VKEY=addr_vk1...  # Your verification key
SELLER_SKEY=addr_sk1...  # Your secret key (KEEP SECURE!)
```

### Step 3: Start Services

```bash
docker compose up -d
```

Wait 30 seconds for services to start.

### Step 4: Verify Payment Service

```bash
curl http://localhost:3001/health
```

Expected output:
```json
{
  "status": "healthy",
  "service": "Masumi Payment Service",
  "network": "Preprod",
  "version": "1.0.0"
}
```

### Step 5: Configure Python Agent

Update `masumi-outreach-agent/masumi-agent/.env`:

```bash
# Masumi Payment Service
MASUMI_PAYMENT_URL=http://localhost:3001

# Agent Configuration
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1

# Wallet Keys (same as Payment Service)
SELLER_VKEY=addr_vk1...
SELLER_SKEY=addr_sk1...

# Optional: API Key
PAYMENT_API_KEY=
```

### Step 6: Test Integration

```bash
cd masumi-outreach-agent/masumi-agent
python main.py
```

In another terminal:
```bash
curl -X POST http://localhost:8080/start_job \
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

## 🔑 Getting Cardano Wallet Keys

### Option 1: Create New Wallet (Recommended for Testing)

```bash
# Install cardano-cli
# On macOS: brew install cardano-cli
# On Linux: Follow https://developers.cardano.org/docs/get-started/installing-cardano-node

# Generate payment keys
cardano-cli address key-gen \
  --verification-key-file payment.vkey \
  --signing-key-file payment.skey

# View keys
cat payment.vkey  # Copy this to SELLER_VKEY
cat payment.skey  # Copy this to SELLER_SKEY

# Generate address
cardano-cli address build \
  --payment-verification-key-file payment.vkey \
  --testnet-magic 1 \
  --out-file payment.addr

# View address
cat payment.addr
```

### Option 2: Use Existing Wallet

If you have a Daedalus or Yoroi wallet:
1. Export your wallet keys (check wallet documentation)
2. Use the verification key for SELLER_VKEY
3. Use the signing key for SELLER_SKEY

⚠️ **WARNING**: Only use test wallets for development!

## 💰 Fund Your Test Wallet

### Get Test ADA from Faucet

1. Go to: https://docs.cardano.org/cardano-testnet/tools/faucet/
2. Enter your wallet address (from `payment.addr`)
3. Request test ADA (1000 tADA)
4. Wait 1-2 minutes for confirmation

### Verify Balance

```bash
cardano-cli query utxo \
  --address $(cat payment.addr) \
  --testnet-magic 1
```

## 🧪 Testing the Full Flow

### 1. Start All Services

```bash
# Terminal 1: Payment Service
cd masumi-services-dev-quickstart
docker compose up

# Terminal 2: Node.js Outreach Service
cd Intent-Driven-Cold-Outreach-Agent
npm start

# Terminal 3: Python Agent
cd masumi-outreach-agent/masumi-agent
python main.py
```

### 2. Create a Job

```bash
curl -X POST http://localhost:8080/start_job \
  -H "Content-Type: application/json" \
  -d @test-job.json
```

Response will include real `blockchainIdentifier`:
```json
{
  "id": "job-uuid",
  "blockchainIdentifier": "tx_hash_from_cardano",
  "payByTime": 1707849600,
  ...
}
```

### 3. View Transaction on Blockchain

```bash
# Copy the blockchainIdentifier from response
# Visit: https://preprod.cardanoscan.io/transaction/{blockchainIdentifier}
```

### 4. Check Job Status

```bash
curl http://localhost:8080/status?job_id=job-uuid
```

### 5. Verify Payment Released

After job completes:
```bash
cardano-cli query utxo \
  --address $(cat payment.addr) \
  --testnet-magic 1
```

Balance should increase by 500 credits worth of ADA.

## 🐛 Troubleshooting

### Payment Service Not Starting

```bash
# Check logs
docker compose logs payment-service

# Common issues:
# 1. Invalid BLOCKFROST_PROJECT_ID
# 2. Invalid wallet keys
# 3. Port 3001 already in use
```

### Connection Refused

```bash
# Verify service is running
docker compose ps

# Check if port is accessible
curl http://localhost:3001/health

# Check firewall settings
```

### Invalid Blockchain Identifier

```bash
# Check Payment Service logs
docker compose logs payment-service | grep ERROR

# Verify wallet has funds
cardano-cli query utxo --address $(cat payment.addr) --testnet-magic 1
```

### Signature Verification Failed

```bash
# Ensure SELLER_SKEY matches SELLER_VKEY
# Regenerate keys if needed
```

## 📊 Monitoring

### Check Payment Service Health

```bash
watch -n 5 'curl -s http://localhost:3001/health | jq'
```

### Monitor Blockchain Transactions

```bash
# Watch for new transactions
cardano-cli query utxo \
  --address $(cat payment.addr) \
  --testnet-magic 1 \
  --out-file utxos.json

watch -n 10 'cat utxos.json | jq'
```

### Check Agent Logs

```bash
# Python agent logs
tail -f masumi-outreach-agent/masumi-agent/logs/agent.log

# Look for:
# "Calling Masumi Payment Service to create job"
# "Payment Service response: {...}"
# "Submitting result to Payment Service"
```

## 🚀 Moving to Production

### 1. Update Network

```bash
# In masumi-services-dev-quickstart/.env
NETWORK=Mainnet

# In masumi-outreach-agent/masumi-agent/.env
MASUMI_PAYMENT_URL=https://payment-service.masumi.network
```

### 2. Use Production Wallet

- Create new wallet for production
- Fund with real ADA
- Store keys securely (use secrets manager)

### 3. Deploy to Railway

```bash
# Set environment variables in Railway dashboard
MASUMI_PAYMENT_URL=https://payment-service.masumi.network
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
SELLER_VKEY=<production_vkey>
SELLER_SKEY=<production_skey>  # Use Railway secrets!
PAYMENT_API_KEY=<production_key>
```

### 4. Test on Mainnet

- Start with small test transactions
- Monitor wallet balance
- Verify escrow releases correctly

## ✅ Success Checklist

- [ ] Payment Service running on http://localhost:3001
- [ ] Health check returns "healthy"
- [ ] Wallet funded with test ADA
- [ ] Python agent configured with correct keys
- [ ] Test job creates real blockchain transaction
- [ ] Transaction visible on Cardano explorer
- [ ] Job completes and releases escrow
- [ ] Wallet balance increases

## 📚 Next Steps

1. ✅ Complete local testing
2. ✅ Implement Ed25519 signing (replace placeholder)
3. ✅ Add monitoring and alerts
4. ✅ Deploy to Preprod (testnet)
5. ✅ Test with real Sokosumi marketplace
6. ✅ Deploy to Mainnet (production)

## 🆘 Need Help?

- [Masumi Documentation](https://docs.masumi.network)
- [Cardano Developer Portal](https://developers.cardano.org)
- [Masumi Discord](https://discord.gg/masumi)
- [GitHub Issues](https://github.com/masumi-network/masumi-services-dev-quickstart/issues)
