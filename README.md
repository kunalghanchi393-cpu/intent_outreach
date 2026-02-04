# Intent-Driven Cold Outreach Agent

A production-ready AI agent that generates personalized cold outreach messages based on intent signals, featuring a 7-step reasoning workflow and full Masumi network integration.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ and pip
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/kp183/Intent-Driven-Cold-Outreach-Agent.git
cd Intent-Driven-Cold-Outreach-Agent

# Install Node.js dependencies
npm install

# Build the project
npm run build

# Install Python dependencies for Masumi integration
cd masumi-outreach-agent/masumi-agent
pip install -r requirements.txt
cd ../..
```

### Running the Services

```bash
# Terminal 1: Start Node.js outreach service (port 3000)
npm start

# Terminal 2: Start Masumi agent (port 8080)
cd masumi-outreach-agent/masumi-agent
python main.py
```

### Testing

```bash
# Run Node.js tests (116 tests)
npm test

# Run MIP-003 compliance tests (5 tests)
cd masumi-outreach-agent/masumi-agent
python test_mip003.py
```

## 🏗️ Architecture

### Node.js Service (Port 3000)
Core outreach generation service with 7-step reasoning workflow:

1. **Signal Interpretation** - Analyzes intent signals for relevance
2. **Hypothesis Formation** - Forms outreach hypotheses based on signals
3. **Strategy Selection** - Selects optimal messaging strategy
4. **Message Generation** - Creates personalized outreach messages
5. **Authenticity Filtering** - Validates message authenticity
6. **Confidence Scoring** - Assigns confidence levels
7. **Output Assembly** - Assembles final structured response

### Python Masumi Agent (Port 8080)
MIP-003 compliant blockchain integration layer:

- **Job Management** - Handles outreach requests as blockchain jobs
- **Payment Processing** - Integrates with Masumi payment system
- **Status Tracking** - Real-time job status updates
- **Background Processing** - Async job processing pipeline

## 📡 API Endpoints

### Node.js Service
- `GET /health` - Health check
- `POST /agent/outreach` - Generate outreach message

### Masumi Agent (MIP-003 Compliant)
- `POST /start_job` - Start outreach job
- `GET /status?job_id={id}` - Get job status
- `GET /availability` - Check service availability
- `GET /input_schema` - Get input format
- `GET /demo` - Get demo data
- `POST /provide_input` - Provide additional input

## 📊 Input Format

```json
{
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
    }
  ]
}
```

## 📈 Output Format

```json
{
  "success": true,
  "data": {
    "intentConfidence": "High",
    "reasoningSummary": "Strong funding signals indicate expansion phase...",
    "recommendedMessage": "Hi John,\n\nI saw that TechCorp Inc recently raised Series B funding...",
    "alternativeMessages": ["Alternative 1...", "Alternative 2..."],
    "suggestedFollowUpTiming": "one_week",
    "processingMetadata": {
      "executionTime": 45,
      "workflowSteps": [...]
    }
  }
}
```

## 🧪 Testing & Quality

### Node.js Service
- **116 tests** covering all components
- **Property-based testing** with 36 properties
- **Conservative behavior** validation
- **Integration testing** for complete workflows

### Masumi Integration
- **5 MIP-003 compliance tests** (all passing)
- **End-to-end workflow testing**
- **Payment simulation testing**
- **Error handling validation**

### Signal Types Supported
- `job_change` - Role changes, promotions
- `funding_event` - Investment rounds, acquisitions
- `technology_adoption` - Tech stack changes
- `company_growth` - Expansion, hiring sprees
- `industry_trend` - Market shifts, regulations

## 🌐 Deployment

### Environment Configuration

**Node.js Service (.env.example):**
```env
NODE_ENV=production
PORT=3000
```

**Masumi Agent (.env):**
```env
AGENT_IDENTIFIER=intent-driven-outreach-agent-v1
PAYMENT_API_KEY=your-api-key
SELLER_VKEY=your-vkey
NETWORK=Preprod
PORT=8080
OUTREACH_SERVICE_URL=http://localhost:3000
```

### Production Deployment
1. Deploy Node.js service to your preferred platform
2. Deploy Python Masumi agent with environment variables
3. Configure load balancers and health checks
4. Register agent in Masumi marketplace

## 📁 Project Structure

```
Intent-Driven-Cold-Outreach-Agent/
├── src/                          # Node.js source code
│   ├── reasoning-agent/          # Main workflow orchestrator
│   ├── signal-interpreter/       # Intent signal analysis
│   ├── message-generator/        # Message generation
│   └── ...                       # Other components
├── masumi-outreach-agent/        # Masumi integration
│   └── masumi-agent/
│       ├── agent.py              # MIP-003 compliant functions
│       ├── main.py               # FastAPI server
│       └── test_mip003.py        # Compliance tests
├── dist/                         # Compiled output
├── package.json                  # Node.js configuration
├── README.md                     # This file
└── API_DOCUMENTATION.md          # Detailed API docs
```

## 🎯 Key Features

- **Intent-Driven**: Analyzes real intent signals, not just demographics
- **Conservative Approach**: Safety-first with authenticity validation
- **Blockchain Ready**: Full MIP-003 compliance for Masumi network
- **Production Tested**: 121 total tests across both services
- **Scalable Architecture**: Async processing with status tracking
- **Comprehensive Logging**: Full observability and debugging

## 📚 Documentation

- **API Documentation**: Complete API reference with examples
- **Integration Guide**: Step-by-step Masumi integration
- **Testing Guide**: How to run and extend tests
- **Deployment Guide**: Production deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test` and `python test_mip003.py`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🚀 Status

**Production Ready** ✅
- Node.js Service: 116/116 tests passing
- Masumi Integration: 5/5 MIP-003 tests passing
- End-to-end workflow: Fully functional
- Documentation: Complete
- Deployment: Ready for production

---

Built with ❤️ for personalized, intent-driven outreach at scale.