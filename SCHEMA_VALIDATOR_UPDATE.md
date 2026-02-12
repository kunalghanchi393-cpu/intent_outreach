# Schema-Validator Format Update

## Summary
Updated the Masumi agent input schema to the new schema-validator format compatible with https://docs.masumi.network/documentation/technical-documentation/schema-validator-component

## Changes Made

### 1. Updated `get_input_schema()` Function
- **Return Type**: Changed from `Dict[str, Any]` to `list`
- **Schema Structure**: Now returns a list directly (NOT wrapped in `{"input_data": [...]}`)
- **Field Types**: Updated to new types:
  - `text` (was `string`)
  - `email` (new type)
  - `option` (kept same, but uses `values` instead of `options`)
- **Validation Format**: Changed from `{"type": "..."}` to `{"validation": "...", "value": "..."}`

### 2. Outreach-Specific Schema Fields
The schema now includes 8 flat fields for cold outreach:
- `prospect_name` (text) - Prospect's full name with min/max length validation
- `prospect_email` (email) - Prospect's email with format validation
- `prospect_role` (text) - Prospect's job title/role
- `company_name` (text) - Company name
- `company_industry` (text) - Company industry
- `company_size` (option) - Company size (startup, small, medium, large, enterprise)
- `intent_signal` (option) - Primary intent signal type
- `intent_description` (text) - Description of the intent signal

### 3. Updated `get_demo_data()` Function
Updated demo data to match the outreach schema fields:
```json
{
  "input": {
    "prospect_name": "John Smith",
    "prospect_email": "john.smith@techcorp.com",
    "prospect_role": "VP of Engineering",
    "company_name": "TechCorp Inc",
    "company_industry": "Software",
    "company_size": "medium",
    "intent_signal": "funding_event",
    "intent_description": "Company raised Series B funding"
  }
}
```

### 4. Updated `process_outreach_job()` Function
Enhanced job processing to handle flat input and reconstruct structured format internally:
- Accepts flat input from new schema-validator format
- Reconstructs `prospectData` object with nested structure
- Reconstructs `intentSignals` array from flat fields
- Maintains backward compatibility with old structured format
- Calls Node.js outreach service with proper structured format

## Verification

### Schema Output
The `/input_schema` endpoint now returns:
```json
[
  {
    "id": "prospect_name",
    "type": "text",
    "name": "Prospect Name",
    "data": {
      "placeholder": "Enter full name",
      "description": "Full name of the prospect"
    },
    "validations": [
      {"validation": "min", "value": "2"},
      {"validation": "max", "value": "100"}
    ]
  },
  {
    "id": "prospect_email",
    "type": "email",
    "name": "Prospect Email",
    "data": {
      "placeholder": "name@company.com"
    },
    "validations": [
      {"validation": "format", "value": "email"}
    ]
  },
  ...
]
```

### Key Points
- ✅ Schema returns as a list directly (not wrapped in `{"input_data": [...]}`)
- ✅ No legacy `type: "string"` or `required: true` fields
- ✅ Uses new validation format: `{"validation": "type", "value": "..."}`
- ✅ Field types: text, email, option (no nested objects or arrays)
- ✅ Option fields use `values` array instead of `options`
- ✅ MIP-003 compliance maintained
- ✅ `/input_schema` endpoint returns HTTP 200
- ✅ Backward compatibility with structured format maintained
- ✅ Job processing reconstructs structured format internally for Node.js service

## Deployment
Changes committed and pushed to master branch. Railway will automatically redeploy.

## Testing
After deployment, verify:
1. `GET /input_schema` returns HTTP 200
2. Schema matches the new format exactly
3. Job processing works with new input fields
4. Demo endpoint returns updated demo data
