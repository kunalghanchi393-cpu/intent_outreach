/**
 * Test script for the outreach service
 * Run with: node test-outreach.js
 */

const http = require('http');

const testPayload = {
  prospectData: {
    role: "VP Engineering",
    companyContext: {
      name: "TestCorp",
      industry: "Software",
      size: "medium"
    },
    contactDetails: {
      name: "John Doe",
      email: "john@company.com"
    }
  },
  intentSignals: [{
    type: "funding_event",
    description: "Raised Series B",
    timestamp: "2026-02-13T15:00:00Z",
    relevanceScore: 0.8,
    source: "User Input"
  }]
};

const postData = JSON.stringify(testPayload);

const options = {
  hostname: 'localhost',
  port: 3000,
  path: '/agent/outreach',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

console.log('🧪 Testing outreach service...');
console.log('📤 Sending request to http://localhost:3000/agent/outreach');
console.log('📦 Payload:', JSON.stringify(testPayload, null, 2));
console.log('');

const req = http.request(options, (res) => {
  console.log(`📡 Response Status: ${res.statusCode}`);
  console.log(`📋 Response Headers:`, res.headers);
  console.log('');

  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    console.log('📥 Response Body:');
    try {
      const parsed = JSON.parse(data);
      console.log(JSON.stringify(parsed, null, 2));
    } catch (e) {
      console.log(data);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request Error:', error);
});

req.write(postData);
req.end();
