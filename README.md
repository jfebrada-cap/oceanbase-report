# OceanBase Capacity Assessment Reporter

A Python tool to extract comprehensive OceanBase instance and tenant metrics from Alibaba Cloud for capacity assessment and planning.

## Features

- **Multi-Format Export**
  - Excel workbooks with multiple tabs (Capacity Assessment, Tenants, Summary, Utilization)
  - CSV files (separate files for each report type)
  - Professional formatting and auto-sizing

- **Dated Directory Structure**
  - Automatic dated folders (YYYYMMDD)
  - Organized by frequency (Daily/Weekly/Monthly)
  - Example: `output/20251230/Daily/OceanBase_Daily_Report_20251230_130103.xlsx`

- **Report Frequencies**
  - Daily reports (default)
  - Weekly reports (aggregated)
  - Monthly reports (aggregated)

- **Capacity Center Integration (NEW)**
  - **Instance Capacity Allocation** (28 new fields)
    - Total vs Allocated vs Available for CPU, Memory, Storage, Log Disk
    - Allocation percentages for capacity planning
    - Unit capacity and original capacity tracking
    - Peak disk usage percentages across servers
  - **Tenant Resource Allocation** (8 new fields)
    - Allocated CPU and Memory per tenant
    - Unit CPU/Memory/Log Disk per resource unit
    - Actual disk usage tracking
    - Number of units per tenant
  - **Tenant Connection Information** (4 new fields)
    - Connection address (intranet)
    - Connection port
    - Connection status (ONLINE/CLOSED)
    - Maximum allowed connections

- **Instance Metrics**
  - Resource allocation with total/allocated/available breakdown
  - Utilization metrics (CPU, Memory, Disk with avg/min/max/P95)
  - Disk utilization percentage
  - Resource allocation percentages for capacity planning

- **Tenant Metrics** (Streamlined and Enhanced)
  - **CPU usage** (percentage with avg/max/min/P95)
  - **Memory usage** (percentage with avg/max/min)
  - **Active sessions** (avg/max/min)
  - **Connection details** (address, port, status, max connections)
  - **Resource allocation** (CPU, Memory, Disk, Log Disk)
  - **Clean reports** - Removed 28 unnecessary columns (I/O metrics, memstore, redundant cores metrics)
  - **50% fewer API calls** - Optimized from 6 to 3 CloudMonitor metrics per tenant

- **Summary Statistics**
  - Total resource capacity
  - Average utilization metrics
  - Instance counts and status

## Prerequisites

- Python 3.7 or higher
- Alibaba Cloud account with OceanBase access
- Alibaba Cloud CLI configured with credentials

## Installation

### 1. Clone or Navigate to Project

```bash
cd ~/Desktop/Projects/oceanbase-reporter
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

This will install:
- `alibabacloud-oceanbasepro20190901` - OceanBase API SDK
- `alibabacloud-cms20190101` - CloudMonitor API SDK
- `alibabacloud-tea-openapi` - Alibaba Cloud API core
- `pandas` - Data processing and CSV export
- `openpyxl` - Excel file generation

### 3. Configure Alibaba Cloud Credentials

If you haven't already configured your Alibaba Cloud credentials:

```bash
aliyun configure
```

Enter your:
- Access Key ID
- Access Key Secret
- Default Region (e.g., `ap-southeast-1`)

Your credentials will be stored in `~/.aliyun/config.json`

## Usage

### Generate Reports by Frequency

**Daily report (default):**
```bash
python3 main.py --region ap-southeast-1
```

**Weekly report:**
```bash
python3 main.py --region ap-southeast-1 --frequency weekly
```

**Monthly report:**
```bash
python3 main.py --region ap-southeast-1 --frequency monthly
```

**Single instance:**
```bash
python3 main.py --region ap-southeast-1 --instances <instance_id>
```

### Daily Report with 7-Day P95 Lookback (NEW)

Get the **highest P95 CPU/Memory utilization from the last 7 days** in a daily report:

```bash
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 7
```

This will:
- Generate a daily report
- Fetch metrics from the **last 7 days** instead of 24 hours
- Calculate P95 from all datapoints across those 7 days
- Show the **maximum P95 value** from that period

**Other lookback examples:**
```bash
# 3-day lookback for P95
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 3

# 14-day lookback for P95
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 14
```

### Advanced Options

**Extract specific instances:**
```bash
python3 main.py --region ap-southeast-1 --instances ob2yppfe8jkc3l ob6lxzzelle2xs
```

**List instances only (no metrics):**
```bash
python3 main.py --region ap-southeast-1 --list-only
```

---

This generates:
- Single Excel workbook with multiple tabs
- Dated directory structure: `output/20251230/Daily/` (or Weekly/Monthly)
- Professional formatting with auto-sizing

### Generate Reports in Different Formats

**Excel format (default):**
```bash
python3 main.py --region ap-southeast-1 --format excel
```

**CSV format:**
```bash
python3 main.py --region ap-southeast-1 --format csv
```

**Both Excel and CSV:**
```bash
python3 main.py --region ap-southeast-1 --format both
```

**Custom output directory:**
```bash
python3 main.py --region ap-southeast-1 --output-dir custom_output
```

### Command-Line Options

```
--region           Alibaba Cloud region (default: from credentials)
--output-dir       Base output directory (default: output)
--format          Output format: excel, csv, or both (default: excel)
--frequency       Report frequency: daily, weekly, or monthly (default: daily)
--instances       Specific instance IDs to process (optional)
--list-only       Only list instances without extracting metrics
--config          Path to configuration file (default: config/config.json)
```

## Output Files

### Excel Format (Default)

Single workbook with multiple tabs in dated directory:
```
output/
└── 20251230/
    └── Daily/
        └── OceanBase_Daily_Report_20251230_130103.xlsx
            ├── Tab 1: Capacity Assessment
            ├── Tab 2: Tenants Report
            └── Tab 3: Summary Statistics
```

**Tab 1: Capacity Assessment** (Streamlined)
- Instance ID, Name, Status, Series
- **CPU Capacity**: Total, Allocated, Available
- **Memory Capacity**: Total, Allocated, Available
- **Storage Capacity**: Total, Allocated, Actual Data Usage, Available
- **Log Disk Capacity**: Total, Allocated, Available
- **Utilization Metrics**: CPU, Memory, Disk (avg/min/max/P95 %)
- Disk Type, Create Time

**Tab 2: Tenants Report** (Streamlined)
- Tenant ID, Name, Mode
- **Resource Allocation**:
  - CPU: Allocated CPU
  - Memory: Allocated Memory
  - Disk: Actual Disk Usage
  - Log Disk: Allocated Log Disk
- **Connection Information**:
  - Max Connections
- **CPU Usage** (avg/max/min/P95) - percentage only
- **Memory Usage** (avg/max/min) - percentage only
- **Active Sessions** (avg/max/min)
- Create Time

**Tab 3: Summary Statistics**
- Total instances count
- Total resource capacity (CPU, Memory, Storage)
- Average utilization metrics
- Online instances count

**Note:** Removed all redundant columns for cleaner, more actionable reports focused on essential capacity metrics.

### CSV Format (Optional)

Separate CSV files in `output/` directory:
- `oceanbase_capacity_assessment_YYYYMMDD_HHMMSS.csv`
- `oceanbase_tenants_YYYYMMDD_HHMMSS.csv`

## Execution Time

- **Quick extraction** (2 instances, 37 tenants): ~3-5 minutes
- **Full extraction** (44 instances, 373 tenants): ~15-20 minutes

The tool fetches metrics from CloudMonitor API for the last 24 hours with 1-hour aggregation.

## Example Output

```
======================================================================
OceanBase Capacity Assessment Reporter
======================================================================

Using region: ap-southeast-1

✓ OceanBase client initialized
✓ Excel exporter initialized (output: output/)

Discovering all OceanBase instances...
✓ Found 44 instance(s)

[1/44] Processing instance: ob2yppfe8jkc3l
----------------------------------------------------------------------
  Instance Name: gcash_prod02
  Status: ONLINE
  Spec - CPU: 186.0 cores, Memory: 1200.0 GB, Disk: 99000.0 GB
  Resource Usage:
    Disk: 50158.00 GB used / 99000.0 GB total (50.66%)
  Fetching utilization metrics (last 24 hours)...
    CPU: avg=93.16%, min=69.95%, max=114.21%, P95=109.99%
    Memory: avg=88.74%, min=85.55%, max=91.99%, P95=91.96%
  Fetching tenants...
    Found 27 tenant(s)
    Fetching tenant metrics...
      Processed 10/27 tenants...
      Processed 20/27 tenants...
    ✓ Completed fetching metrics for 27 tenant(s)
  ✓ Completed

...

======================================================================
Generating Reports
======================================================================
Report Frequency: Daily
Output Format: EXCEL

✓ Consolidated Daily report saved to: output/20251230/Daily/OceanBase_Daily_Report_20251230_130103.xlsx
  - Capacity Assessment: 44 instances
  - Tenants Report: 373 tenants
  - Report Type: Daily

======================================================================
✓ Report generation completed successfully
  Total instances processed: 44
  Total tenants found: 373
  Report frequency: Daily
  Output format: excel
  Base output directory: output/
======================================================================
```

## Metrics Details

### Instance Metrics (from CloudMonitor)

All metrics are aggregated based on the report frequency:
- **Daily**: Last 24 hours of data
- **Weekly**: Last 7 days, showing HIGHEST utilization (MAX values)
- **Monthly**: Last 30 days, showing HIGHEST utilization (MAX values)

**CPU Utilization** (converted to percentage 0-100%):
- The CloudMonitor API returns CPU usage in **cores**, which is automatically converted to percentage
- For example: 287.96 cores used / 312 total cores = 92.29%
- Metrics: Average, Minimum, Maximum, P95 percentile
- Column headers: `cpu_utilization_avg_%`, `cpu_utilization_min_%`, `cpu_utilization_max_%`, `cpu_utilization_p95_%`

**Memory Utilization** (percentage 0-100%):
- CloudMonitor returns memory usage as percentage
- Metrics: Average, Minimum, Maximum, P95 percentile
- Column headers: `memory_utilization_avg_%`, `memory_utilization_min_%`, `memory_utilization_max_%`, `memory_utilization_p95_%`

**Disk Utilization** (percentage 0-100%):
- Calculated from: (used_storage / total_storage) × 100
- Represents actual disk space consumption

### Tenant Metrics (Streamlined)

Tenant metrics show utilization and resource allocation details:

**From DescribeTenant API (NEW):**
- **Resource Allocation**: Allocated CPU, Memory, Disk Usage, Log Disk per tenant
- **Connection Information**: Address, Port, Status, Max Connections

**From CloudMonitor API:**
- **CPU Usage Percent**: Tenant CPU usage 0-100% (avg/max/min/P95)
- **Memory Usage**: Tenant memory utilization 0-100% (avg/max/min)
- **Active Sessions**: Number of active connections (avg/max/min)

**Removed Metrics (Unnecessary/Redundant):**
- ~~CPU Usage Cores~~ - Redundant with percentage
- ~~MEMStore Usage~~ - Too granular for capacity reports
- ~~I/O Read/Write Response Times~~ - Better monitored in real-time tools
- ~~I/O Read/Write Bytes per Second~~ - Throughput metrics not needed for capacity planning

**Result:** 50% reduction in API calls (from 6 to 3 CloudMonitor metrics per tenant), cleaner reports with 28 fewer columns.

**Important Note on Tenant Storage Metrics:**
Tenant disk usage is now available through the **DescribeTenant API** (`tenant_actual_disk_usage` field). This shows the actual disk space used by each tenant and is included in the tenant reports.

## Use Cases

### 1. Capacity Planning
**Question:** "How much capacity is available for new tenants?"

**Solution:** Check the new capacity allocation columns:
- `available_cpu` - How many CPU cores are free
- `available_memory` - How much memory is free
- `available_storage` - How much storage is free
- `cpu_allocation_pct`, `memory_allocation_pct` - Percentage of capacity allocated

**Example:**
```
Instance: gcash_prod02
  CPU: 186 cores total, 150 allocated (80.6%), 36 available
  Memory: 1200 GB total, 980 allocated (81.7%), 220 GB available

→ Can provision ~36 new CPU cores or 220 GB more memory
```

### 2. Cost Optimization
**Question:** "Which instances are over-provisioned?"

**Solution:** Find instances with low allocation percentages:
- `cpu_allocation_pct < 30%` - Significant unused CPU capacity
- `memory_allocation_pct < 30%` - Significant unused memory capacity

**Action:** Consider downsizing or consolidating tenants to fewer instances.

### 3. Tenant Resource Audit
**Question:** "How much is each tenant actually using vs allocated?"

**Solution:** Compare allocation vs actual usage:
- `tenant_allocated_cpu` vs `cpu_usage_percent_avg` - Is allocated CPU being used?
- `tenant_allocated_memory` vs `memory_usage_percent_avg` - Is allocated memory being used?
- `tenant_actual_disk_usage` - How much disk space is actually consumed?

**Example:**
```
Tenant: analytics_tenant
  Allocated: 8 CPU cores, 32 GB memory
  Usage: CPU avg=65%, Memory avg=71%
  Actual Disk: 125 GB used

→ Well-balanced allocation, no action needed
```

### 4. Connection Management
**Question:** "How do I connect to each tenant and what are the connection limits?"

**Solution:** Use the new connection information columns:
- `connection_address` - Connection endpoint
- `connection_port` - Port number
- `connection_status` - ONLINE or CLOSED
- `max_connections` - Maximum allowed connections

**Example:**
```
Tenant: analytics_tenant
  Address: analytics.ap-southeast-1.oceanbase.aliyuncs.com
  Port: 3306
  Status: ONLINE
  Max Connections: 12,800
```

### 5. Growth Forecasting
**Question:** "When will we run out of capacity?"

**Solution:** Track allocation percentages over time:
- Weekly/Monthly reports show allocation trends
- Set alerts at 80-90% allocation
- Project when you'll need to scale up

**Allocation Guidelines:**
- < 30%: Consider downsizing
- 30-60%: Well-balanced
- 60-80%: Good utilization
- 80-90%: Plan capacity expansion soon
- > 90%: Scale up immediately

## API Value Validation & Debugging

### Checking for API Values Over 100%

The reporter includes built-in validation to cap utilization metrics at 100%.

**What You'll See:**

If the API returns values > 100%, warnings are logged:
```
⚠ WARNING: cpu_usage exceeded 100% - Raw values: avg=105.23, max=112.45, p95=110.30
```

And metrics are capped in output:
```
CPU: avg=100.0%, min=98.5%, max=100.0%, P95=100.0% (capped from 112.45%)
```

**Why Values Might Exceed 100%:**
- Multi-core CPU aggregation without proper normalization
- CPU turbo boost / bursting above rated capacity
- Measurement timing issues in CloudMonitor

**Solution:** All percentage metrics are automatically capped at 100% in reports.

For detailed information, see [API_VALIDATION_GUIDE.md](API_VALIDATION_GUIDE.md)

### Important Notes on Metrics

1. **All CPU and Memory utilization values are 0-100%** - No values should exceed 100%
2. **Instance CPU metrics are converted from cores to percentages** automatically
3. **Tenant metrics already return percentages** from the API
4. **Weekly/Monthly reports show peak utilization** (highest values during the period)
5. **Tenants with 0% CPU may be genuinely idle** - infrastructure/middleware services often have very low or zero CPU usage

## Troubleshooting

### Authentication Errors

```
✗ Authentication failed: ...
```

**Solution**: Run `aliyun configure` to set up credentials

### No Instances Found

```
✗ No OceanBase instances found
```

**Solution**:
- Verify you have OceanBase instances in the specified region
- Check your credentials have proper permissions
- Try a different region with `--region <region-id>`

### Missing Dependencies

```
ModuleNotFoundError: No module named 'alibabacloud_oceanbasepro20190901'
```

**Solution**:
```bash
pip3 install -r requirements.txt
```

### Slow Execution

If extraction is taking too long, you can:
1. Extract specific instances only: `--instances ob123abc ob456def`
2. Use `--list-only` to verify instances before full extraction

## Project Structure

```
oceanbase-reporter/
├── main.py                              # Main execution script
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
├── .gitignore                           # Git ignore rules
├── config/
│   └── config.json                     # Optional configuration file
├── src/
│   ├── auth.py                         # Alibaba Cloud authentication handler
│   ├── oceanbase_client.py             # OceanBase & CloudMonitor API client
│   ├── csv_exporter.py                 # CSV export utilities
│   └── excel_exporter.py               # Excel export with multi-tab support
├── CAPACITY_CENTER_README.md            # Capacity Center features guide
├── CAPACITY_CENTER_FIELDS.md            # API field documentation
├── CAPACITY_ALLOCATION_IMPLEMENTATION.md # Implementation details
├── IMPLEMENTATION_SUMMARY.md            # Complete feature summary
├── 7DAY_P95_GUIDE.md                   # 7-day P95 lookback guide
├── API_VALIDATION_GUIDE.md             # API validation details
└── output/                             # Generated reports (auto-created)
    └── YYYYMMDD/                       # Dated directories
        ├── Daily/                      # Daily reports
        ├── Weekly/                     # Weekly reports (7-day peak)
        └── Monthly/                    # Monthly reports (30-day peak)
```

## Recent Updates

### Version 2.3.0 - Capacity Center Integration (2025-12-30)

**New Features:**
- **36 new capacity allocation fields** (28 instance + 8 tenant)
- **4 new connection information fields** for tenants
- **Tenant CPU P95 metric** added
- **50% reduction in API calls** (6→3 metrics per tenant)
- **28 unnecessary columns removed** from tenant reports

**APIs Integrated:**
- `DescribeInstance` - Instance capacity allocation
- `DescribeTenant` - Tenant resource allocation and connections

**Benefits:**
- Cleaner, more actionable reports
- Better capacity planning with allocation percentages
- Direct tenant connection information
- Faster report generation
- P95 metrics for capacity planning

**Backward Compatibility:**
- Column positions changed (breaking for position-based parsers)
- Use column headers instead of position indices when parsing CSV files
- All essential data is preserved with better naming conventions

For complete details, see [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

