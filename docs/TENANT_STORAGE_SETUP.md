# Tenant Storage Metrics Setup Guide

## Current Status

I've added tenant storage metrics to the OceanBase Reporter code, but you need to:
1. Verify the correct metric names in CloudMonitor API
2. Re-run the reporter to generate a new report with the storage columns

## What Was Added

### Code Changes ✅

Three new tenant storage metrics were added:

1. **disk_data_size_tenant** → `disk_data_size_gb` (Data disk size in GB)
2. **disk_usage_percent_tenant** → `disk_usage_percent` (Disk utilization %)
3. **disk_log_size_tenant** → `disk_log_size_gb` (Log disk size in GB)

### Files Modified ✅

- `src/oceanbase_client.py` - Added metrics to tenant_metric_map
- `src/csv_exporter.py` - Added columns to export order
- `src/excel_exporter.py` - Added columns to Tenants Report tab
- `README.md` - Documented the new metrics

## Why You Don't See the Columns Yet

**Your existing report was generated BEFORE the code changes:**
- Existing file: `output/20251230/Daily/OceanBase_Daily_Report_20251230_173554.xlsx`
- Created at: 5:35 PM (Dec 30)
- Code changes made: After 5:35 PM

**The columns will only appear after you run the reporter again.**

## Step 1: Verify Metric Names

The metric names I used (`disk_data_size_tenant`, `disk_usage_percent_tenant`, `disk_log_size_tenant`) are based on common OceanBase CloudMonitor naming patterns. However, they might be different in the actual API.

**Run the diagnostic script to find the correct names:**

```bash
cd /Users/jerielfebrada/Desktop/Projects/oceanbase-reporter
python3 check_available_metrics.py
```

This script will:
- Test multiple possible metric name variations
- Show which metrics are actually available in CloudMonitor
- Display sample values from each metric
- Tell you exactly what to add to the code

## Step 2: Update Metric Names (if needed)

If the diagnostic script finds different metric names, update them in `src/oceanbase_client.py`:

```python
# Around line 318-321
# Storage/Disk metrics - tenant disk usage
'disk_data_size_tenant': 'disk_data_size_gb',         # ← Update these
'disk_usage_percent_tenant': 'disk_usage_percent',    # ← if needed
'disk_log_size_tenant': 'disk_log_size_gb',          # ← based on script output
```

## Step 3: Run the Reporter

Once you've verified/updated the metric names, run the reporter:

```bash
python3 main.py --frequency daily --region ap-southeast-1
```

## Step 4: Check the New Report

Open the new Excel file in `output/YYYYMMDD/Daily/` and go to the **Tenants Report** tab.

**You should see these new columns:**
- `disk_data_size_gb_avg`
- `disk_data_size_gb_max`
- `disk_data_size_gb_min`
- `disk_usage_percent_avg`
- `disk_usage_percent_max`
- `disk_usage_percent_min`
- `disk_log_size_gb_avg`
- `disk_log_size_gb_max`
- `disk_log_size_gb_min`

## What If Metrics Are Not Available?

If the diagnostic script shows **no storage metrics found**, it could mean:

1. **CloudMonitor doesn't collect tenant-level storage metrics**
   - Some metrics are only available at instance level
   - Check the Alibaba Cloud console to confirm

2. **Different metric namespace**
   - Might be in a different namespace (not `acs_oceanbase`)
   - Check CloudMonitor documentation

3. **Permissions issue**
   - Your access key might not have permission to view certain metrics

### Alternative: Use Instance-Level Storage Only

If tenant-level storage metrics aren't available, you can still track storage at the instance level (which is already working in the Capacity Assessment tab).

## Troubleshooting

### Issue: Columns appear but are empty

**Possible causes:**
- Metrics exist but have no data for your time period
- Metrics require specific tenant configuration
- API timeout during metric fetch

**Solution:**
Check the console output when running the reporter. You should see:
```
Fetching tenant metrics...
  Processed 10/27 tenants...
```

If storage metrics are being fetched, you'll see values in the output.

### Issue: Script shows "metric not found"

**This is normal!** The script tests many possible names. Only the ones that return data are valid.

### Issue: API timeout

If you have many tenants (373 in your case), fetching additional metrics might cause timeouts.

**Solution:** The code already uses 1-hour aggregation periods to reduce API calls. If timeouts occur, you can:
1. Reduce the number of metrics fetched
2. Increase timeout values
3. Process instances in batches

## Expected Output

### If Storage Metrics ARE Available:

```
Fetching tenant metrics...
  ✓ disk_data_size_tenant: 125.5 GB
  ✓ disk_usage_percent_tenant: 67.3%
  ✓ disk_log_size_tenant: 45.2 GB
```

### If Storage Metrics ARE NOT Available:

```
Fetching tenant metrics...
  ⚠ disk_data_size_tenant: No data
  ⚠ disk_usage_percent_tenant: No data
  ⚠ disk_log_size_tenant: No data
```

The columns will still appear in the report but will be empty.

## Next Steps

1. **Run the diagnostic script:** `python3 check_available_metrics.py`
2. **Update metric names if needed:** Edit `src/oceanbase_client.py`
3. **Run the reporter:** `python3 main.py --frequency daily`
4. **Check the Tenants Report tab** in the new Excel file

## Questions?

If storage metrics aren't available through the API, let me know and I can:
- Help find alternative ways to get the data
- Modify the code to calculate storage from other available metrics
- Add placeholder columns that you can fill manually
