# Capacity Allocation Implementation - Complete

## Overview

Successfully implemented **Capacity Center** features to the OceanBase Reporter, including:
- **Allocated vs Total resources** (CPU, Memory, Storage, Log Disk)
- **Available capacity** calculations
- **Allocation percentages**
- **Tenant resource allocation details**

## What Was Implemented

### 1. Instance-Level Capacity Allocation

Added comprehensive capacity metrics from `DescribeInstance` API:

#### CPU Allocation
- `total_cpu` - Total CPU capacity (cores)
- `allocated_cpu` - CPU allocated to tenants (cores)
- `available_cpu` - CPU still available for allocation (cores)
- `cpu_allocation_pct` - Percentage of CPU allocated (%)
- `unit_cpu` - CPU per unit
- `original_total_cpu` - Original CPU capacity

#### Memory Allocation
- `total_memory` - Total memory capacity (GB)
- `allocated_memory` - Memory allocated to tenants (GB)
- `available_memory` - Memory still available for allocation (GB)
- `memory_allocation_pct` - Percentage of memory allocated (%)
- `unit_memory` - Memory per unit (GB)
- `original_total_memory` - Original memory capacity (GB)

#### Storage (Data Disk) Allocation
- `total_storage` - Total storage capacity (GB)
- `allocated_storage` - Storage allocated (GB)
- `actual_data_usage` - Actual data disk usage (GB)
- `available_storage` - Storage still available for allocation (GB)
- `storage_allocation_pct` - Percentage of storage allocated (%)
- `max_disk_used_pct` - Peak disk usage across servers (%)
- `unit_disk_size` - Disk per unit (GB)
- `original_total_disk` - Original disk capacity (GB)

#### Log Disk Allocation
- `total_log_disk` - Total log disk capacity (GB)
- `allocated_log_disk` - Log disk allocated (GB)
- `available_log_disk` - Log disk still available for allocation (GB)
- `log_disk_allocation_pct` - Percentage of log disk allocated (%)
- `max_log_assigned_pct` - Peak log disk assignment across servers (%)
- `unit_log_disk` - Log disk per unit (GB)
- `original_total_log_disk` - Original log disk capacity (GB)

### 2. Tenant-Level Resource Allocation

Added detailed tenant allocation metrics from `DescribeTenant` API:

#### Tenant Allocated Resources
- `tenant_allocated_cpu` - CPU allocated to this tenant (cores)
- `tenant_unit_cpu` - CPU per unit for this tenant (cores)
- `tenant_allocated_memory` - Memory allocated to this tenant (GB)
- `tenant_unit_memory` - Memory per unit for this tenant (GB)
- `tenant_actual_disk_usage` - Actual disk usage by this tenant (GB)
- `tenant_allocated_log_disk` - Log disk allocated to this tenant (GB)
- `tenant_unit_log_disk` - Log disk per unit for this tenant (GB)
- `tenant_unit_num` - Number of units for this tenant

## Code Changes

### 1. oceanbase_client.py

#### Enhanced `get_instance_details()` (lines 91-238)
- Extracts CPU, Memory, Storage, and Log Disk allocation from `DescribeInstance` API
- Calculates allocation percentages
- Calculates available resources
- Rounds percentages to 2 decimal places

#### New `get_tenant_details()` (lines 278-354)
- Calls `DescribeTenant` API to get detailed tenant resource allocation
- Extracts allocated CPU, memory, disk usage, and log disk
- Handles fallback if TenantResource object not available

### 2. main.py (lines 214-221)

Added call to `get_tenant_details()` before `get_tenant_metrics()`:

```python
# Get detailed tenant resource allocation (from DescribeTenant API)
tenant_details = reporter.get_tenant_details(
    instance_id,
    tenant['tenant_id']
)
if tenant_details:
    # Merge detailed allocation info (will include tenant_allocated_cpu, etc.)
    tenant.update(tenant_details)
```

### 3. csv_exporter.py

#### Instance Report Columns (lines 49-81)
Updated column order to include all capacity allocation fields at the front

#### Tenant Report Columns (lines 120-163)
Updated column order to include tenant allocation fields at the front

### 4. excel_exporter.py

#### Instance Report Columns (lines 204-240)
Updated column order to match CSV exporter

#### Tenant Report Columns (lines 249-290)
Updated column order to match CSV exporter

## Example Output

### Instance Report

| Instance | Total CPU | Allocated CPU | Available CPU | CPU Alloc % | Total Memory | Allocated Memory | Available Memory | Memory Alloc % |
|----------|-----------|---------------|---------------|-------------|--------------|------------------|------------------|----------------|
| gcash_sit | 8.0 | 4.0 | 4.0 | 50.00 | 32.0 | 16.0 | 16.0 | 50.00 |

| Total Storage | Allocated Storage | Actual Data Usage | Available Storage | Storage Alloc % | Max Disk Used % |
|---------------|-------------------|-------------------|-------------------|-----------------|-----------------|
| 1000.0 | 1.0 | 1.0 | 999.0 | 0.10 | 0.09 |

| Total Log Disk | Allocated Log Disk | Available Log Disk | Log Disk Alloc % | Max Log Assigned % |
|----------------|--------------------|--------------------|------------------|--------------------|
| 100.0 | 47.0 | 53.0 | 47.00 | 50.72 |

### Tenant Report

| Tenant | Allocated CPU | Allocated Memory | Actual Disk Usage | Allocated Log Disk | Unit Num |
|--------|---------------|------------------|-------------------|--------------------|----------|
| facepay_tenant | 4.0 | 16.0 | 0.1 | 29.0 | 1 |

## Use Cases

### 1. Capacity Planning
**Question:** "How much capacity is still available for new tenants?"

**Answer:** Check `available_cpu`, `available_memory`, `available_storage`, `available_log_disk` columns

**Example:**
- Available CPU: 4.0 cores (50% of total)
- Available Memory: 16.0 GB (50% of total)
- Available Storage: 999.0 GB (99.9% of total)

### 2. Rightsizing Instances
**Question:** "Are we over-provisioned?"

**Answer:** Check `*_allocation_pct` columns

**Example:**
- CPU Allocation: 50% - Good utilization
- Memory Allocation: 50% - Good utilization
- Storage Allocation: 0.1% - Very under-utilized (potential cost savings)

### 3. Growth Planning
**Question:** "When will we run out of capacity?"

**Answer:** Compare allocated vs total over time to project when you'll hit 80-90% allocation

### 4. Cost Optimization
**Question:** "Which instances have low allocation but high cost?"

**Answer:** Find instances with:
- Low `cpu_allocation_pct` (<30%)
- Low `memory_allocation_pct` (<30%)
- Large `total_cpu` and `total_memory` (expensive)

### 5. Tenant Resource Audit
**Question:** "How much is each tenant actually using?"

**Answer:** Compare:
- `tenant_allocated_cpu` vs `cpu_usage_percent_avg` (allocated vs actual usage)
- `tenant_allocated_memory` vs `memory_usage_percent_avg`
- `tenant_actual_disk_usage` (actual disk space used)

## API Sources

### Instance Capacity: DescribeInstance API
- **Namespace:** OceanBase Pro SDK
- **Method:** `describe_instance(instance_id)`
- **Response Path:** `response.body.instance.resource`

### Tenant Allocation: DescribeTenant API
- **Namespace:** OceanBase Pro SDK
- **Method:** `describe_tenant(instance_id, tenant_id)`
- **Response Path:** `response.body.tenant.tenant_resource`

### Utilization Metrics: CloudMonitor API
- **Namespace:** Cloud Monitor Service
- **Method:** `describe_metric_list()`
- **Namespace ID:** `acs_oceanbase`

## Testing

### Run a test report:

```bash
cd /Users/jerielfebrada/Desktop/Projects/oceanbase-reporter
python3 main.py --region ap-southeast-1 --frequency daily
```

### Expected output columns:

**Instance Report (Capacity Assessment tab):**
- All capacity allocation fields (allocated, available, allocation %)
- All utilization metrics (avg, min, max, P95)

**Tenant Report (Tenants tab):**
- Tenant allocated resources (CPU, memory, log disk)
- Tenant actual disk usage
- Tenant utilization metrics from CloudMonitor

### Verification:

1. Check Excel file has capacity columns in Capacity Assessment tab
2. Check Excel file has tenant allocation columns in Tenants tab
3. Verify numbers make sense:
   - `allocated + available = total`
   - `allocation_pct = (allocated / total) * 100`
   - Tenant allocated resources should sum to instance allocated resources

