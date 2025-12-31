# API Value Validation Guide

## Purpose
This guide explains how to verify whether Alibaba CloudMonitor API actually returns CPU/Memory utilization values exceeding 100%.

## Quick Test

Run the test script:
```bash
cd /Users/jerielfebrada/Desktop/Projects/oceanbase-reporter
./test_api_values.sh
```

## What to Look For

### 1. Warning Messages
When you run the reporter, look for lines like this:
```
⚠ WARNING: cpu_usage exceeded 100% - Raw values: avg=105.23, min=98.50, max=112.45, p95=110.30
  Sample values from API: [108.5, 110.2, 112.45, 105.3, 109.8]
```

### 2. Capped Values in Output
You'll also see capped indicators in the progress output:
```
CPU: avg=100.0%, min=98.5%, max=100.0%, P95=100.0% (capped from 112.45%)
```

### 3. Check Console Output
During the run, the reporter will show:
- **No warnings**: API returned values within 0-100%
- **Warnings present**: API returned values > 100% (which were capped)

## Why Values Might Exceed 100%

According to Alibaba Cloud documentation and real-world observations, CloudMonitor can return values > 100% due to:

### 1. **Multi-Core CPU Behavior**
- Some metrics aggregate across all cores
- If not properly normalized, can exceed 100%
- Example: 8 cores at 15% each = 120% without normalization

### 2. **CPU Turbo Boost / Bursting**
- Modern CPUs can temporarily exceed rated capacity
- Intel Turbo Boost, AMD Precision Boost
- Short bursts may be reported as >100%

### 3. **Measurement Window Issues**
- CloudMonitor samples at intervals (1s, 5s, 60s, 3600s)
- Spike between samples can cause >100% average
- Timing alignment issues

### 4. **API Data Anomalies**
- Rare API bugs or data processing issues
- Network/system jitter affecting measurements
- Rounding errors in aggregation

## Code Changes Made

### Location 1: Instance-Level Metrics
**File:** `src/oceanbase_client.py` (lines 264-291)

**What it does:**
- Captures raw values from CloudMonitor API
- Calculates avg/min/max/p95 from raw data
- Logs WARNING if any value exceeds 100%
- Caps all values at exactly 100.0%
- Returns both capped and raw values

**Example output:**
```python
{
    'metric_name': 'cpu_usage',
    'avg': 100.0,      # Capped
    'max': 100.0,      # Capped
    'raw_avg': 105.23, # Original from API
    'raw_max': 112.45  # Original from API
}
```

### Location 2: Tenant-Level Metrics
**File:** `src/oceanbase_client.py` (lines 384-410)

**What it does:**
- Same logic for tenant metrics
- Only caps percentage metrics (cpu_usage_percent, memory_usage)
- Leaves absolute metrics (cores, GB, sessions) uncapped
- Logs warnings for percentage metrics > 100%

## Validation Steps

### Step 1: Run with Debug Output
```bash
python3 main.py --frequency daily 2>&1 | tee api_test.log
```

### Step 2: Search for Warnings
```bash
grep "WARNING.*exceeded 100%" api_test.log
```

### Step 3: Count Occurrences
```bash
grep -c "WARNING.*exceeded 100%" api_test.log
```

### Step 4: View Raw Values
```bash
grep "Sample values from API" api_test.log
```

## Expected Results

### Scenario A: API Returns Values > 100%
```
✗ Found 15 instance(s) where API returned values > 100%

Details:
⚠ WARNING: cpu_usage exceeded 100% - Raw values: avg=105.23, max=112.45
⚠ WARNING: memory_percent exceeded 100% - Raw values: avg=102.10, max=108.30
...

CONCLUSION: The Alibaba CloudMonitor API IS returning values > 100%
            The capping at 100% is necessary and working correctly.
```

### Scenario B: API Returns Values ≤ 100%
```
✓ No values exceeded 100%

CONCLUSION: All API values were within 0-100% range.
            The capping code is in place but not triggered.
```

## Impact on Reports

With the fix in place:
- All CSV/Excel reports will show values capped at 100%
- Original raw values are logged but not exported
- Capacity planning will be based on 0-100% scale
- No more confusing values like 112% CPU utilization

## Reference: Alibaba Cloud Documentation

From Alibaba Cloud CloudMonitor docs:
- Metric: `cpu_usage`
- Unit: Percent
- Range: **Typically 0-100, but can exceed 100 in rare cases**
- Aggregation: Average across all CPU cores

## Questions?

If you see consistent values > 100%:
1. Check which instances are affected
2. Review the instance specifications (cores, memory)
3. Verify if it's always the same metric (cpu_usage vs memory_percent)
4. Check the time period (daily vs weekly vs monthly)

The capping is a **safety measure** to ensure reports are consistent and interpretable.
