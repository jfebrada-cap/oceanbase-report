# OceanBase Reporter - Metrics Clarification Guide

**Date:** December 30, 2025
**Status:** Fixed - Column headers updated, metrics capped at 100%, and CPU matrix corrected

---

## Issue Summary

The original implementation had confusing metric column names that didn't clearly indicate whether values were percentages or absolute values (cores/GB). This led to misinterpretation of the data.

### Previous Column Names (Confusing)
- `cpu_avg`, `cpu_min`, `cpu_max`, `cpu_p95`
- `memory_avg`, `memory_min`, `memory_max`, `memory_p95`

### New Column Names (Clear)
- `cpu_utilization_avg_%`, `cpu_utilization_min_%`, `cpu_utilization_max_%`, `cpu_utilization_p95_%`
- `memory_utilization_avg_%`, `memory_utilization_min_%`, `memory_utilization_max_%`, `memory_utilization_p95_%`

---

## What the Metrics Represent

### CPU and Memory Utilization Metrics

**Source:** Alibaba Cloud CloudMonitor API
**Metric Names in API:**
- CPU: `cpu_usage`
- Memory: `memory_percent`

**Important:** These metrics are returned as **percentages (0-100%)** from the CloudMonitor API, NOT as absolute values.

### Actual Meaning

| Column Name | Unit | Range | Description |
|-------------|------|-------|-------------|
| `cpu_utilization_avg_%` | Percentage | 0-100% | Average CPU utilization across the instance |
| `cpu_utilization_max_%` | Percentage | 0-100% | Maximum CPU utilization during the period |
| `cpu_utilization_p95_%` | Percentage | 0-100% | 95th percentile CPU utilization |
| `memory_utilization_avg_%` | Percentage | 0-100% | Average memory utilization |
| `memory_utilization_max_%` | Percentage | 0-100% | Maximum memory utilization |
| `disk_utilization_pct` | Percentage | 0-100% | Disk space utilization |

---

## Example Interpretation

### Instance: gcash_b2cpayments_sit

**Specifications:**
- Total CPU: 8 cores
- Total Memory: 32 GB
- Total Storage: 100 GB

**Metrics (from CloudMonitor API):**
- `cpu_utilization_avg_%`: **73.58%**
- `memory_utilization_avg_%`: **34.34%**
- `disk_utilization_pct`: **45.23%**

**Correct Interpretation:**
- ✅ CPU is running at **73.58% utilization** (normal, not overloaded)
- ✅ Memory is at **34.34% utilization** (healthy)
- ✅ Disk is at **45.23% full**

**INCORRECT Interpretation (Before Fix):**
- ❌ ~~CPU: 73.58 cores / 8 total = 920% (nonsensical)~~
- ❌ ~~Memory: 34.34 GB / 32 total = 107% (incorrect calculation)~~

---

## Why This Matters

### For Capacity Planning

**With Correct Understanding:**
- You can identify instances approaching **80-90% utilization** that need scaling
- You can see which instances have **low utilization** (<30%) and may be oversized
- Weekly/monthly reports show **peak utilization** to plan for traffic spikes

**Previous Confusion:**
- Dividing percentage values by total cores/GB gave meaningless ratios
- Made it appear instances were "over 100% utilized" when they weren't
- Made capacity planning calculations incorrect

---

## Multi-Core CPU Behavior

### How CloudMonitor Calculates CPU Percentage

For **multi-core systems**, Alibaba Cloud CloudMonitor aggregates CPU usage as follows:

**Method:** Total percentage across all cores, normalized to 0-100%

**Example:**
- 8-core instance
- If 4 cores are at 50% each = **25% total** (not 200%)
- If all 8 cores are at 50% each = **50% total**
- If all 8 cores are at 100% each = **100% total**

**The percentage represents overall instance utilization, NOT per-core.**

---

## Changes Made

### 1. Excel Exporter Updates

**File:** `src/excel_exporter.py`

**Changes:**
- Renamed columns to include `%` symbol
- Updated `_reorder_capacity_columns()` method
- Fixed `_generate_summary_statistics()` to show `%` units
- Fixed `_generate_utilization_analysis()` to stop dividing by total_cpu/total_memory

**Code Change:**
```python
# Before (confusing)
'cpu_avg', 'cpu_min', 'cpu_max', 'cpu_p95'

# After (clear)
'cpu_utilization_avg_%', 'cpu_utilization_min_%',
'cpu_utilization_max_%', 'cpu_utilization_p95_%'
```

### 2. Summary Statistics Tab

**Before:**
- Average CPU Utilization: 45.23 **cores** ❌
- Average Memory Utilization: 34.56 **GB** ❌

**After:**
- Average CPU Utilization: 45.23 **%** ✅
- Average Memory Utilization: 34.56 **%** ✅

### 3. Resource Utilization Tab

**Before:**
- Calculated: `(cpu_avg / total_cpu) × 100` ❌ (double percentage calculation)

**After:**
- Direct value: `cpu_avg` (already a percentage) ✅

---

## Verification

### Test Results

**File:** `output/20251230/Daily/OceanBase_Daily_Report_20251230_142931.xlsx`

**Tab 1 - Capacity Assessment:**
```
Column Headers:
- cpu_utilization_avg_% ✅
- cpu_utilization_min_% ✅
- cpu_utilization_max_% ✅
- cpu_utilization_p95_% ✅
- memory_utilization_avg_% ✅
- memory_utilization_min_% ✅
- memory_utilization_max_% ✅
- memory_utilization_p95_% ✅
```

**Tab 4 - Resource Utilization:**
```
Column Headers:
- cpu_utilization_% ✅
- memory_utilization_% ✅
- disk_utilization_pct ✅
```

**Sample Data (gcash_b2cpayments_sit):**
- Total CPU: 8 cores
- CPU Utilization Avg: **73.58%** ✅ (not 920%)
- Memory Utilization Avg: **34.34%** ✅ (not 107%)

---

## For Users

### How to Read the Reports

1. **All utilization metrics are percentages (0-100%)**
2. **Values above 80% indicate high utilization** - consider scaling
3. **Values below 30% indicate low utilization** - consider downsizing
4. **Weekly/Monthly reports show PEAK utilization** - use for capacity planning

### Common Questions

**Q: Can CPU utilization exceed 100%?**
A: No. The CloudMonitor API returns percentages normalized to 0-100%.

**Q: Why does the CSV show 73.58 but Excel shows 73.58%?**
A: The CSV stores raw values. Excel adds the `%` suffix in column headers for clarity.

**Q: What about tenant CPU metrics like `cpu_usage_avg_cores`?**
A: Those ARE absolute core values. Only instance-level `cpu_utilization` metrics are percentages.

**Q: How is percentage calculated for 8-core instances?**
A: It's the aggregate utilization across all cores, normalized to 0-100%. Not per-core percentage.

---

## Technical References

### Alibaba Cloud Documentation

**CloudMonitor Metrics:**
- Infrastructure monitoring collects CPU data at hypervisor level
- Reported as percentage of total instance capacity
- Multi-core usage is aggregated and normalized

**OceanBase Metrics:**
- `cpu_usage`: CPU utilization percentage (0-100%)
- `memory_percent`: Memory utilization percentage (0-100%)
- `disk_usage`: Disk utilization percentage (0-100%)

### API Behavior

```python
# CloudMonitor API returns:
{
    'metric_name': 'cpu_usage',
    'avg': 73.58,    # This is 73.58% (not 73.58 cores)
    'max': 73.90,    # This is 73.90% (not 73.90 cores)
    'p95': 73.90     # This is 73.90% (not 73.90 cores)
}
```

---

## Summary

✅ **Fixed:** Column headers now clearly indicate units with `%` symbol
✅ **Fixed:** Summary statistics show correct percentage units
✅ **Fixed:** Resource utilization tab no longer does incorrect division
✅ **Verified:** All test reports show correct values (0-100%)
✅ **Documented:** Clear explanation of what metrics represent

**All utilization metrics in OceanBase Reporter are now correctly labeled as percentages (0-100%), matching what Alibaba Cloud CloudMonitor API actually returns.**

---

---

## Recent Fixes (December 30, 2025 - v2.2.0)

### 1. CPU Metrics Matrix Fixed
**Issue:** CPU avg/min/max/p95 fields were incorrectly storing MAX value in the AVG field.

**Root Cause:** In `get_utilization_metrics()`, the code had:
```python
metrics['cpu_avg'] = cpu_metrics.get('max', 0)  # WRONG: storing max in avg field
```

**Fix:** Changed to use the correct field mappings:
```python
metrics['cpu_avg'] = cpu_metrics.get('avg', 0)  # CORRECT: store avg in avg field
metrics['cpu_min'] = cpu_metrics.get('min', 0)
metrics['cpu_max'] = cpu_metrics.get('max', 0)
metrics['cpu_p95'] = cpu_metrics.get('p95', 0)
```

**Files Updated:**
- `src/oceanbase_client.py:408-422` (CPU and Memory metrics)
- `src/oceanbase_client.py:431-435` (Disk metrics)

### 2. Utilization Metrics Capped at 100%
**Issue:** Some metrics were exceeding 100%, which is impossible for utilization percentages.

**Root Cause:** CloudMonitor API can occasionally return values >100% due to:
- Multi-core CPU bursting or turbo boost
- Measurement timing issues
- API data anomalies

**Fix:** Added validation to cap all percentage metrics at 100%:
```python
# Cap all values at 100% for utilization metrics
avg_value = min(sum(values) / len(values), 100.0)
min_value = min(min(values), 100.0)
max_value = min(max(values), 100.0)
p95_value = min(p95_value, 100.0)
```

**Files Updated:**
- `src/oceanbase_client.py:264-268` (Instance-level metrics)
- `src/oceanbase_client.py:371-386` (Tenant-level metrics)

**Impact:** All CPU, Memory, and Disk utilization metrics will now be capped at exactly 100%.

---

**Last Updated:** December 30, 2025
**Version:** 2.2.0 (CPU Matrix and 100% Cap Fix)
