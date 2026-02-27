#!/usr/bin/env python3
"""
Test script to verify Sokosumi array index format handling
"""
import sys
sys.path.insert(0, 'masumi-outreach-agent/masumi-agent')

from agent import convert_option_value, COMPANY_SIZE_OPTIONS, INTENT_SIGNAL_OPTIONS

print("🧪 Testing Sokosumi array index conversion...")
print()

# Test company_size conversion
print("📋 Testing company_size conversion:")
print(f"   Options: {COMPANY_SIZE_OPTIONS}")
print(f"   [2] -> {convert_option_value([2], COMPANY_SIZE_OPTIONS)}")  # Should be "medium"
print(f"   2 -> {convert_option_value(2, COMPANY_SIZE_OPTIONS)}")      # Should be "medium"
print(f"   'medium' -> {convert_option_value('medium', COMPANY_SIZE_OPTIONS)}")  # Should be "medium"
print()

# Test intent_signal conversion
print("📋 Testing intent_signal conversion:")
print(f"   Options: {INTENT_SIGNAL_OPTIONS}")
print(f"   [3] -> {convert_option_value([3], INTENT_SIGNAL_OPTIONS)}")  # Should be "company_growth"
print(f"   3 -> {convert_option_value(3, INTENT_SIGNAL_OPTIONS)}")      # Should be "company_growth"
print(f"   [1] -> {convert_option_value([1], INTENT_SIGNAL_OPTIONS)}")  # Should be "funding_event"
print(f"   'funding_event' -> {convert_option_value('funding_event', INTENT_SIGNAL_OPTIONS)}")  # Should be "funding_event"
print()

print("✅ All conversions completed!")
