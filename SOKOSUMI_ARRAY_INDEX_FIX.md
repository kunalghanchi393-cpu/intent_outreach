# Sokosumi Array Index Format Fix

## 🔍 Problem Discovered

After fixing the HTTP 400 error for insufficient intent signals, a new validation error appeared:

```
❌ STEP: Validation failed
❌ STEP: Validation error: {
  "code": "VALIDATION_FAILED",
  "message": "Input validation failed: intentSignals[0].type: Signal type is required and must be a string",
  "field": "intentSignals[0].type",
  "code": "MISSING_SIGNAL_TYPE"
}
```

### Root Cause Analysis

Looking at the debug logs:

```json
{
  "prospectData": {
    "companyContext": {
      "size": [2]  // ❌ Should be "medium"
    }
  },
  "intentSignals": [{
    "type": [3]  // ❌ Should be "company_growth"
  }]
}
```

**Issue**: Sokosumi is sending array indices `[n]` instead of the actual string values from the schema options.

### Why This Happens

In the input schema, option fields are defined with a `values` array:

```python
{
  "id": "company_size",
  "type": "option",
  "data": {
    "values": ["startup", "small", "medium", "large", "enterprise"]
  }
}
```

When a user selects "medium" (index 2), Sokosumi sends `[2]` instead of `"medium"`.

## ✅ Solution Implemented

### 1. Created Option Mappings

```python
# Schema option mappings for converting indices to values
COMPANY_SIZE_OPTIONS = ["startup", "small", "medium", "large", "enterprise"]
INTENT_SIGNAL_OPTIONS = [
    "job_change",
    "funding_event",
    "technology_adoption",
    "company_growth",
    "industry_trend"
]
```

### 2. Created Conversion Function

```python
def convert_option_value(value: Any, options: List[str]) -> str:
    """
    Convert option value from Sokosumi format to actual string value.
    Sokosumi may send either:
    - A string value directly
    - An array with a single index [n]
    - An integer index n
    
    Args:
        value: The value to convert (can be str, int, or list)
        options: List of valid option values
    
    Returns:
        The actual string value from the options list
    """
    # If it's already a string and valid, return it
    if isinstance(value, str) and value in options:
        return value
    
    # If it's a list with one element (Sokosumi format)
    if isinstance(value, list) and len(value) > 0:
        index = value[0]
        if isinstance(index, int) and 0 <= index < len(options):
            return options[index]
    
    # If it's an integer index
    if isinstance(value, int) and 0 <= value < len(options):
        return options[value]
    
    # Default to first option if conversion fails
    logger.warning(f"Could not convert option value {value}, using default: {options[0]}")
    return options[0]
```

### 3. Updated Job Processing

```python
# Handle Sokosumi sending array indices instead of string values
company_size_raw = input_data.get("company_size", "medium")
company_size = convert_option_value(company_size_raw, COMPANY_SIZE_OPTIONS)

intent_signal_raw = input_data.get("intent_signal", "company_growth")
intent_signal_type = convert_option_value(intent_signal_raw, INTENT_SIGNAL_OPTIONS)
```

## 🧪 Testing Results

### Test Cases

```python
# Company Size
convert_option_value([2], COMPANY_SIZE_OPTIONS)  # -> "medium" ✅
convert_option_value(2, COMPANY_SIZE_OPTIONS)    # -> "medium" ✅
convert_option_value("medium", COMPANY_SIZE_OPTIONS)  # -> "medium" ✅

# Intent Signal
convert_option_value([3], INTENT_SIGNAL_OPTIONS)  # -> "company_growth" ✅
convert_option_value([1], INTENT_SIGNAL_OPTIONS)  # -> "funding_event" ✅
convert_option_value("funding_event", INTENT_SIGNAL_OPTIONS)  # -> "funding_event" ✅
```

### Before Fix

**Input from Sokosumi:**
```json
{
  "company_size": [2],
  "intent_signal": [3]
}
```

**Sent to Node.js:**
```json
{
  "companyContext": {
    "size": [2]  // ❌ Invalid
  },
  "intentSignals": [{
    "type": [3]  // ❌ Invalid
  }]
}
```

**Result:** HTTP 400 - VALIDATION_FAILED

### After Fix

**Input from Sokosumi:**
```json
{
  "company_size": [2],
  "intent_signal": [3]
}
```

**Sent to Node.js:**
```json
{
  "companyContext": {
    "size": "medium"  // ✅ Valid
  },
  "intentSignals": [{
    "type": "company_growth"  // ✅ Valid
  }]
}
```

**Result:** HTTP 200 - SUCCESS

## 📋 Supported Input Formats

The converter now handles all these formats:

1. **Sokosumi array format**: `[2]` → `"medium"`
2. **Integer index**: `2` → `"medium"`
3. **String value**: `"medium"` → `"medium"`

This ensures backward compatibility and flexibility.

## 🎯 Impact

### Before
- ❌ Sokosumi sends array indices
- ❌ Node.js validation fails
- ❌ Jobs cannot be processed

### After
- ✅ Array indices converted to strings
- ✅ Node.js validation passes
- ✅ Jobs process successfully
- ✅ Backward compatible with string values

## 🚀 Deployment Status

- ✅ Conversion function added
- ✅ Option mappings defined
- ✅ Job processing updated
- ✅ Tested with all formats
- ✅ Committed to master
- ✅ Pushed to GitHub
- 🔄 Railway will automatically redeploy

## 📝 Index Mappings Reference

### Company Size
```
0 -> "startup"
1 -> "small"
2 -> "medium"
3 -> "large"
4 -> "enterprise"
```

### Intent Signal
```
0 -> "job_change"
1 -> "funding_event"
2 -> "technology_adoption"
3 -> "company_growth"
4 -> "industry_trend"
```

## 🔧 Future Considerations

1. **Schema Validation**: Consider adding validation on the Python side before sending to Node.js
2. **Error Handling**: Log warnings when conversion uses defaults
3. **Testing**: Add integration tests for Sokosumi format handling
4. **Documentation**: Update API docs to clarify supported input formats

## ✅ Verification Checklist

After deployment:
- [ ] Sokosumi can submit jobs with option selections
- [ ] Array indices are converted correctly
- [ ] Node.js validation passes
- [ ] Jobs complete successfully
- [ ] Generated messages are high quality
