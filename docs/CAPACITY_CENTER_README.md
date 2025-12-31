# Capacity Center Features - Quick Reference

## What's New

The OceanBase Reporter now includes **comprehensive capacity allocation metrics** from Alibaba Cloud's Capacity Center, showing you exactly how much of your resources are allocated vs available.

## New Columns in Reports

### Instance Report (Capacity Assessment Tab)

#### CPU Capacity
- **total_cpu** - Total CPU capacity (cores)
- **allocated_cpu** - ⭐ CPU allocated to tenants (cores)
- **available_cpu** - ⭐ CPU still available for new tenants (cores)
- **cpu_allocation_pct** - ⭐ Percentage of CPU allocated (%)

#### Memory Capacity
- **total_memory** - Total memory capacity (GB)
- **allocated_memory** - ⭐ Memory allocated to tenants (GB)
- **available_memory** - ⭐ Memory still available for new tenants (GB)
- **memory_allocation_pct** - ⭐ Percentage of memory allocated (%)

#### Storage Capacity
- **total_storage** - Total storage capacity (GB)
- **allocated_storage** - ⭐ Storage allocated (GB)
- **actual_data_usage** - ⭐ Actual data disk usage (GB)
- **available_storage** - ⭐ Storage still available (GB)
- **storage_allocation_pct** - ⭐ Percentage of storage allocated (%)
- **max_disk_used_pct** - ⭐ Peak disk usage across servers (%)

#### Log Disk Capacity
- **total_log_disk** - Total log disk capacity (GB)
- **allocated_log_disk** - ⭐ Log disk allocated (GB)
- **available_log_disk** - ⭐ Log disk still available (GB)
- **log_disk_allocation_pct** - ⭐ Percentage of log disk allocated (%)
- **max_log_assigned_pct** - ⭐ Peak log disk assignment across servers (%)

### Tenant Report (Tenants Tab)

#### Tenant Allocated Resources
- **tenant_allocated_cpu** - ⭐ CPU allocated to this tenant (cores)
- **tenant_allocated_memory** - ⭐ Memory allocated to this tenant (GB)
- **tenant_actual_disk_usage** - ⭐ Actual disk space used by this tenant (GB)
- **tenant_allocated_log_disk** - ⭐ Log disk allocated to this tenant (GB)
- **tenant_unit_num** - Number of resource units for this tenant

## Quick Start

### Run a Report

```bash
cd /Users/jerielfebrada/Desktop/Projects/oceanbase-reporter
python3 main.py --region ap-southeast-1 --frequency daily
```

### Check the Output

Open the Excel file in the `output/` directory. You'll see:

**Capacity Assessment Tab:**
- All instance capacity allocation metrics
- Shows allocated vs available for CPU, Memory, Storage, Log Disk

**Tenants Tab:**
- Tenant resource allocations
- Actual disk usage per tenant

## Common Questions

### Q: How much capacity is available for new tenants?

**A:** Check the `available_*` columns:
- `available_cpu` - CPU cores still available
- `available_memory` - GB of memory still available
- `available_storage` - GB of storage still available

**Example:**
| Instance | Total CPU | Allocated CPU | Available CPU | CPU Alloc % |
|----------|-----------|---------------|---------------|-------------|
| prod_db | 16 | 12 | 4 | 75% |

**Answer:** This instance has **4 CPU cores** available for new tenants (75% allocated, 25% free).

### Q: Are my instances over-provisioned?

**A:** Check the `*_allocation_pct` columns:
- **< 30%**: Under-utilized (potential cost savings)
- **30-60%**: Well-balanced
- **60-80%**: Good utilization
- **> 80%**: High utilization (consider scaling)

**Example:**
| Instance | CPU Alloc % | Memory Alloc % | Storage Alloc % |
|----------|-------------|----------------|-----------------|
| test_db | 25% | 25% | 2% |

**Answer:** This instance is **heavily over-provisioned**. Only 25% of CPU/Memory and 2% of storage are allocated. Consider rightsizing or adding more tenants.

### Q: What's the difference between allocated and actual usage?

**A:**
- **Allocated** = Reserved capacity for tenants (what you've assigned)
- **Actual Usage** = What tenants are currently using

**Example:**
| Instance | Allocated Storage | Actual Data Usage |
|----------|-------------------|-------------------|
| prod_db | 100 GB | 25 GB |

**Answer:** You've allocated 100 GB to tenants, but they're only actually using 25 GB (75 GB is reserved but unused).

### Q: How much is each tenant using?

**A:** Check the Tenants Tab:
- `tenant_allocated_cpu` - What CPU is allocated to this tenant
- `tenant_allocated_memory` - What memory is allocated to this tenant
- `tenant_actual_disk_usage` - What disk space this tenant is actually using

**Example:**
| Tenant | Allocated CPU | Allocated Memory | Actual Disk Usage |
|--------|---------------|------------------|-------------------|
| app1 | 4 cores | 16 GB | 2.5 GB |
| app2 | 8 cores | 32 GB | 45.0 GB |

**Answer:** Tenant `app1` has 4 cores and 16 GB allocated, using 2.5 GB disk. Tenant `app2` has 8 cores and 32 GB allocated, using 45 GB disk.

### Q: When will I run out of capacity?

**A:** Use the allocation percentages and growth rate:

1. Check current `cpu_allocation_pct`
2. Run reports weekly/monthly to track growth
3. Calculate when you'll hit 80-90% allocation

**Example:**
- Month 1: CPU Alloc = 40%
- Month 2: CPU Alloc = 55%
- Month 3: CPU Alloc = 70%

**Growth rate:** +15% per month
**Answer:** You'll hit 85% allocation in about 1 month. Plan capacity expansion now.

### Q: Can I get 7-day capacity metrics?

**A:** Yes! Use the `--lookback-days` parameter:

```bash
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 7
```

This will show you the **highest** utilization (including P95) over the last 7 days, which is useful for capacity planning.

## Use Cases

### 1. Capacity Planning
**Scenario:** Planning to add new tenants

**Steps:**
1. Run daily report
2. Check `available_cpu` and `available_memory` columns
3. Compare with new tenant requirements

**Example:**
- New tenant needs: 4 cores, 16 GB
- Instance has: `available_cpu = 6`, `available_memory = 24 GB`
- **Decision:** Sufficient capacity available

### 2. Cost Optimization
**Scenario:** Reduce cloud costs

**Steps:**
1. Run monthly report
2. Find instances with `cpu_allocation_pct < 30%`
3. Consider consolidating tenants or downsizing

**Example:**
| Instance | Total CPU | Allocated CPU | CPU Alloc % | Monthly Cost |
|----------|-----------|---------------|-------------|--------------|
| test_db | 32 | 8 | 25% | $1,200 |

**Action:** Migrate tenants to a smaller instance (16 cores) to save ~$600/month

### 3. Growth Forecasting
**Scenario:** When to expand capacity

**Steps:**
1. Run weekly reports for 4 weeks
2. Track `cpu_allocation_pct` trend
3. Project when you'll hit 80%

**Example:**
| Week | CPU Alloc % | Growth |
|------|-------------|--------|
| 1 | 60% | - |
| 2 | 65% | +5% |
| 3 | 70% | +5% |
| 4 | 75% | +5% |

**Projection:** +5% per week, will hit 80% in 1 week. **Action:** Expand capacity now.

### 4. Tenant Resource Audit
**Scenario:** Identify resource hogs

**Steps:**
1. Run daily report
2. Check Tenants tab
3. Sort by `tenant_actual_disk_usage` descending

**Example:**
| Tenant | Allocated CPU | Actual Disk Usage |
|--------|---------------|-------------------|
| analytics | 8 | 250 GB |
| app1 | 4 | 2 GB |
| app2 | 4 | 5 GB |

**Finding:** `analytics` tenant is using 98% of disk space. Consider expanding or archiving data.

## Report Examples

### Instance with Good Allocation
```
Instance: prod_app_db
Total CPU: 16 cores
Allocated CPU: 12 cores (75%)
Available CPU: 4 cores

Total Memory: 64 GB
Allocated Memory: 48 GB (75%)
Available Memory: 16 GB

Status: ✓ Well-balanced, room for 1-2 more tenants
```

### Instance with Low Allocation (Over-Provisioned)
```
Instance: dev_test_db
Total CPU: 32 cores
Allocated CPU: 4 cores (12.5%)
Available CPU: 28 cores

Total Storage: 2000 GB
Allocated Storage: 50 GB (2.5%)
Available Storage: 1950 GB

Status: ⚠ Heavily over-provisioned, consider rightsizing
```

### Instance with High Allocation (Near Capacity)
```
Instance: analytics_db
Total CPU: 64 cores
Allocated CPU: 60 cores (93.75%)
Available CPU: 4 cores

Total Memory: 256 GB
Allocated Memory: 240 GB (93.75%)
Available Memory: 16 GB

Status: ⚠ Near capacity, plan expansion soon
```

## Data Sources

### Instance Capacity: DescribeInstance API
- Source: OceanBase Pro SDK
- Updates: Real-time (reflects current allocation)
- Includes: Allocated vs Total for CPU, Memory, Storage, Log Disk

### Tenant Allocation: DescribeTenant API
- Source: OceanBase Pro SDK
- Updates: Real-time (reflects current allocation)
- Includes: Tenant allocated resources and actual disk usage

### Utilization Metrics: CloudMonitor API
- Source: Cloud Monitor Service
- Updates: Hourly datapoints
- Includes: CPU/Memory/Disk utilization (avg, min, max, P95)

## Tips

1. **Run reports regularly** - Weekly for production, monthly for dev/test
2. **Track trends** - Compare allocation % over time to predict growth
3. **Set thresholds** - Alert when allocation > 80% to avoid capacity issues
4. **Review tenants** - Identify tenants with high allocation but low usage
5. **Plan ahead** - Use 7-day P95 metrics for capacity planning

## Troubleshooting

### Issue: Some capacity columns show 0

**Cause:** Instance doesn't have resource allocation info (older API version)

**Solution:** These instances use legacy allocation model. Contact Alibaba Cloud support.

### Issue: Allocated > Total

**Cause:** Temporary capacity expansion or auto-scaling active

**Solution:** This is normal during auto-scaling. Check `original_total_cpu` for base capacity.

### Issue: Tenant allocated doesn't sum to instance allocated

**Cause:** System overhead, reserved capacity, or rounding

**Solution:** This is normal. Instance allocated includes system overhead (typically 5-10%).
