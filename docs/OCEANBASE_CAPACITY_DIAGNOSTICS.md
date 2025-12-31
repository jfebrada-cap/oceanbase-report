# OceanBase Capacity Diagnostics API Integration

## Overview

The OceanBase SDK provides a dedicated **`DescribeTenantMetrics`** API specifically for capacity diagnostics. This is separate from CloudMonitor and is designed to provide tenant usage details over configurable time periods (like "Past 7 Days").

## API Details

### Method: `describe_tenant_metrics`

**Location:** OceanBase Pro SDK (`alibabacloud_oceanbasepro20190901`)

**Purpose:** Get capacity diagnostics data for tenants, including historical usage metrics

### Request Parameters

```python
DescribeTenantMetricsRequest(
    instance_id: str,        # Required: OceanBase instance ID
    tenant_id: str,          # Required: Tenant ID
    start_time: str,         # Required: ISO 8601 format (e.g., "2025-12-23T00:00:00Z")
    end_time: str,           # Required: ISO 8601 format (e.g., "2025-12-30T23:59:59Z")
    metrics: str,            # Optional: Specific metrics (empty = all metrics)
    page_number: int,        # Optional: Page number for pagination
    page_size: int           # Optional: Results per page (default: 100)
)
```

### Common Use Cases

**1. Past 7 Days Capacity Diagnostics:**
```python
from datetime import datetime, timedelta

end_time = datetime.now()
start_time = end_time - timedelta(days=7)

request = DescribeTenantMetricsRequest(
    instance_id="ob6sl3pzhfa3mo",
    tenant_id="t6sl5u0v7kgkg",
    start_time=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    end_time=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    metrics='',  # All metrics
    page_size=100
)

response = oceanbase_client.describe_tenant_metrics(request)
```

**2. Custom Time Range:**
```python
# Last 3 days
start_time = datetime.now() - timedelta(days=3)
end_time = datetime.now()

# Last 30 days
start_time = datetime.now() - timedelta(days=30)
end_time = datetime.now()

# Specific date range
start_time = datetime(2025, 12, 1)
end_time = datetime(2025, 12, 31)
```

## Implementation in Reporter

### New Function: `get_tenant_capacity_diagnostics()`

**File:** `src/oceanbase_client.py`

```python
def get_tenant_capacity_diagnostics(
    self,
    instance_id: str,
    tenant_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Dict:
    """
    Get tenant capacity diagnostics using OceanBase DescribeTenantMetrics API

    Args:
        instance_id: OceanBase instance ID
        tenant_id: Tenant ID
        start_time: Start time in ISO format (optional, defaults to 7 days ago)
        end_time: End time in ISO format (optional, defaults to now)

    Returns:
        Dictionary with tenant capacity metrics from OceanBase API
    """
```

### Integration with Existing Reports

The capacity diagnostics data is automatically fetched when processing tenants:

```python
# In get_tenant_metrics()
capacity_diag = self.get_tenant_capacity_diagnostics(
    instance_id, tenant_id, start_time, end_time
)

if capacity_diag.get('capacity_diagnostics_available'):
    metrics['capacity_diagnostics'] = capacity_diag
```

## Testing the API

### Run the Test Script

```bash
cd /Users/jerielfebrada/Desktop/Projects/oceanbase-reporter
python3 test_capacity_diagnostics_api.py
```

This will:
1. Find an instance with tenants
2. Call `DescribeTenantMetrics` API for 7-day data
3. Display the response structure
4. Show what data is available

### Expected Output

**If API works:**
```
✓ SUCCESS! Capacity diagnostics data retrieved

Response structure:
{
  "capacity_diagnostics_available": true,
  "data": {
    // Tenant metrics data here
  }
}
```

**If API not available:**
```
ℹ No data returned (but no error)

This could mean:
  1. Tenant has no capacity diagnostics data for this period
  2. The metrics parameter needs to be specified
  3. The time range is outside available data
```

## Comparison: Capacity Diagnostics vs CloudMonitor

| Feature | DescribeTenantMetrics (Capacity Diagnostics) | CloudMonitor API |
|---------|---------------------------------------------|------------------|
| **Source** | OceanBase Pro SDK | Cloud Monitor Service |
| **Purpose** | Capacity planning & diagnostics | Real-time monitoring |
| **Data Type** | Aggregated capacity metrics | Time-series datapoints |
| **Time Range** | Flexible (days/weeks/months) | Fixed periods (1h, 24h, 7d) |
| **Tenant Storage** | May include storage data | NOT available |
| **API Method** | `describe_tenant_metrics()` | `describe_metric_list()` |
| **Namespace** | N/A (native OceanBase API) | `acs_oceanbase` |

## Potential Metrics Available

Based on the API design, capacity diagnostics may include:

- **CPU Metrics:**
  - Peak CPU usage
  - Average CPU over period
  - CPU P95/P99 percentiles

- **Memory Metrics:**
  - Peak memory usage
  - Average memory over period
  - Memory growth trends

- **Storage Metrics (if available):**
  - Data disk usage
  - Log disk usage
  - Storage growth rate

- **Session/Connection Metrics:**
  - Peak connections
  - Average active sessions

- **Performance Metrics:**
  - Transaction rates
  - Query latency percentiles

## Next Steps After Testing

### 1. If API Returns Data:

Parse the response structure and extract useful metrics:

```python
if capacity_diag.get('capacity_diagnostics_available'):
    data = capacity_diag['data']

    # Extract metrics based on actual response structure
    # Example (structure TBD based on test results):
    cpu_p95 = data.get('cpu_p95')
    memory_peak = data.get('memory_peak')
    storage_used = data.get('storage_used_gb')
```

### 2. Add to Report Columns:

Update CSV/Excel exporters to include capacity diagnostics data:

```python
# In CSV exporter column order
column_order = [
    'tenant_id', 'tenant_name',
    # ... existing columns ...
    'capacity_cpu_p95_7d',      # From capacity diagnostics
    'capacity_memory_peak_7d',   # From capacity diagnostics
    'capacity_storage_used_7d',  # From capacity diagnostics (if available!)
]
```

### 3. Document Findings:

Create mapping between API response fields and report columns.

## Troubleshooting

### Error: "InvalidParameter"

**Cause:** Time format incorrect

**Solution:** Ensure ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

### Error: "Forbidden" or "Unauthorized"

**Cause:** Account doesn't have permission

**Solution:** Verify your access key has `oceanbasepro:DescribeTenantMetrics` permission

### No Data Returned

**Possible reasons:**
1. Tenant is newly created (no historical data)
2. Time range is too far in the past
3. Capacity diagnostics not enabled for this tenant
4. Region doesn't support this API

## References

- [OceanBase Capacity Diagnostics](https://www.alibabacloud.com/help/en/apsaradb-for-oceanbase/latest/performance-monitoring)
- [DescribeInstance API](https://www.alibabacloud.com/help/en/apsaradb-for-oceanbase/latest/api-oceanbasepro-2019-09-01-describeinstance)
- [Multidimensional Metrics Monitoring](https://www.alibabacloud.com/help/en/apsaradb-for-oceanbase/latest/cluster-multi-dimensional-metric-monitoring-details)

---

**Last Updated:** December 30, 2025
**Status:** Testing in progress
**API:** `alibabacloud_oceanbasepro20190901.describe_tenant_metrics`
