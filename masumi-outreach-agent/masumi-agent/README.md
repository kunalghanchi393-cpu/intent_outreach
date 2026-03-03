# Intent-Driven Cold Outreach Agent - Masumi SDK

Migrated from custom FastAPI to official Masumi SDK. The SDK handles all MIP-003 protocol while preserving 100% of the outreach business logic.

## Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your Masumi credentials

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Node.js service (in project root)
npm start

# 4. Start agent
python main.py
```

## Configuration

Required in `.env`:
```bash
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
SELLER_VKEY=<from_masumi_ui>
SELLER_SKEY=<your_secret_key>
PAYMENT_API_KEY=<from_masumi>
PAYMENT_SERVICE_URL=https://payment-service.masumi.network/api/v1
OUTREACH_SERVICE_URL=http://localhost:3000
```

## What Changed

**Before**: Custom FastAPI with manual MIP-003 implementation (~730 lines)
**After**: Official Masumi SDK with business logic only (~200 lines)

The SDK now handles:
- All MIP-003 endpoints (`/start_job`, `/status`, `/availability`, `/input_schema`)
- Blockchain integration
- Payment service communication
- Job lifecycle management

## Files

- `agent.py` - Business logic (outreach workflow)
- `main.py` - SDK entry point
- `.env` - Configuration
- `requirements.txt` - Dependencies
- `agent_custom_backup.py` - Original implementation (backup)
- `main_custom_backup.py` - Original server (backup)

## Test

```bash
# Check availability
curl http://localhost:8080/availability

# Get schema
curl http://localhost:8080/input_schema
```

## Rollback

If needed:
```bash
cp agent_custom_backup.py agent.py
cp main_custom_backup.py main.py
python main.py
```
