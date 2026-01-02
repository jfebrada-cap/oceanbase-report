# OceanBase Capacity Assessment Reporter

A high-performance Python tool to extract comprehensive OceanBase instance and tenant metrics from Alibaba Cloud for capacity assessment and planning.

## ⚡ Performance Improvement

| Report Type | Old Time (Sequential) | New Time (Parallel) | Time Saved |
|-------------|----------------------|---------------------|------------|
| **Daily (44 instances)** | 2-3 hours | **50-60 min** | **1-2 hours** |
| **Weekly (44 instances)** | 2-3 hours | **50-60 min** | **1-2 hours** |
| **Monthly (44 instances)** | 2-3 hours | **50-60 min** | **1-2 hours** |

**Simply add `--parallel-workers 5` to your command to achieve 3x faster extraction!**

## Features

- **⚡ High-Performance Parallel Extraction**
  - 3.4x faster tenant metric fetching using multi-threading
  - Configurable concurrency (default: 5 workers)
  - Automatic progress tracking
  - Single instance: ~1-1.5 min (vs ~4-5 min sequential)
  - Full deployment (44 instances): ~50-60 min (vs ~2.5-3.5 hours sequential)

- **📊 Comprehensive Metrics Collection**
  - **Instance-level**: CPU, memory, disk utilization with avg/min/max/P95
  - **Tenant-level**: 23 verified metrics including CPU, memory, SQL, I/O, network
  - **Capacity allocation**: Total/allocated/available breakdown for all resources
  - **Time series data**: Daily, weekly, or monthly aggregation

- **📈 Professional Excel Reports**
  - Multi-tab workbooks with formatted tables
  - Capacity Assessment tab (instance overview)
  - Tenants Report tab (detailed tenant metrics)
  - Summary Statistics tab (aggregate insights)
  - Auto-sized columns and professional formatting

- **🗓️ Flexible Reporting Periods**
  - Daily reports (24-hour metrics)
  - Weekly reports (7-day highest values)
  - Monthly reports (30-day highest values)
  - Custom lookback periods (e.g., 7-day P95 in daily reports)

---

## ⚡ Quick Command Reference

**Most Common Commands (with recommended parallel processing):**

```bash
# Daily report (all 44 instances, ~50-60 min)
python3 main.py --region ap-southeast-1 --frequency daily --parallel-workers 5

# Weekly report (all 44 instances, ~50-60 min)
python3 main.py --region ap-southeast-1 --frequency weekly --parallel-workers 5

# Monthly report (all 44 instances, ~50-60 min)
python3 main.py --region ap-southeast-1 --frequency monthly --parallel-workers 5
```

**Performance Note:** Using `--parallel-workers 5` reduces extraction time from **2-3 hours to 50-60 minutes** for 44 instances!

---

## Quick Start

### Prerequisites

- Python 3.7 or higher
- Alibaba Cloud account with OceanBase access
- Alibaba Cloud CLI configured with credentials

### Installation

1. **Install Dependencies**
```bash
pip3 install -r requirements.txt
```

2. **Configure Alibaba Cloud Credentials**

Make sure you have configured your Alibaba Cloud CLI:
```bash
aliyun configure
```

Or set environment variables:
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-secret-key"
export ALIBABA_CLOUD_REGION="ap-southeast-1"
```

### Basic Usage

> **💡 Tip:** All commands below use `--parallel-workers 5` by default for optimal performance (3.4x faster than sequential mode)

**Daily report (recommended - runs with parallel mode by default):**
```bash
# Extract all instances with parallel processing (5 workers)
python3 main.py --region ap-southeast-1 --frequency daily --parallel-workers 5

# Or simply (5 workers is now default):
python3 main.py --region ap-southeast-1
```

**Weekly report (with parallel processing):**
```bash
python3 main.py --region ap-southeast-1 --frequency weekly --parallel-workers 5
```

**Monthly report (with parallel processing):**
```bash
python3 main.py --region ap-southeast-1 --frequency monthly --parallel-workers 5
```

**Extract specific instances:**
```bash
python3 main.py --region ap-southeast-1 --instances ob2yqkpgcoxwu8 ob6lxzzelle2xs --parallel-workers 5
```

---

## Performance Optimization

### Parallel Extraction (Recommended)

By default, the tool uses **5 parallel workers** for optimal performance. You can adjust based on your needs:

```bash
# Fast (default - recommended for most cases)
python3 main.py --region ap-southeast-1 --parallel-workers 5

# Conservative (lower API load, use if experiencing throttling)
python3 main.py --region ap-southeast-1 --parallel-workers 3

# Aggressive (maximum speed, may hit API rate limits)
python3 main.py --region ap-southeast-1 --parallel-workers 10

# Sequential (original behavior, use only if parallel mode causes issues)
python3 main.py --region ap-southeast-1 --parallel-workers 1
```

### Performance Benchmarks

| Deployment Size | Workers | Time | Speedup |
|----------------|---------|------|---------|
| **1 instance (27 tenants)** | 1 (sequential) | ~4-5 min | 1.0x |
| **1 instance (27 tenants)** | 5 (parallel) | **~1-1.5 min** | **3.4x** |
| **44 instances (1000+ tenants)** | 1 (sequential) | ~2.5-3.5 hours | 1.0x |
| **44 instances (1000+ tenants)** | 5 (parallel) | **~50-60 min** | **3.0x** |

### Optimization Tips for Large Deployments

For 44 instances taking 2 hours, you can reduce this significantly:

**1. Use Parallel Mode (Primary Optimization)**
```bash
python3 main.py --region ap-southeast-1 --parallel-workers 5
# Expected time: 50-60 minutes (vs 2-3 hours sequential)
```

**2. Process in Batches (If hitting API rate limits)**
```bash
# Batch 1: First 10 instances
python3 main.py --region ap-southeast-1 --instances inst1 inst2 inst3 ... inst10 --parallel-workers 5

# Batch 2: Next 10 instances
python3 main.py --region ap-southeast-1 --instances inst11 inst12 ... inst20 --parallel-workers 5

# Combine results afterward
```

**3. Use Higher Concurrency (If network is stable)**
```bash
# Up to 10 workers can reduce time to ~30-40 minutes
python3 main.py --region ap-southeast-1 --parallel-workers 10
```

**4. Extract Specific Instances Only**
```bash
# If you only need critical instances
python3 main.py --region ap-southeast-1 --instances prod_instance1 prod_instance2
```

---

## Command-Line Options

### Basic Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | Alibaba Cloud region | From credentials |
| `--instances` | Specific instance IDs to process | All instances |
| `--frequency` | Report frequency: `daily`, `weekly`, `monthly` | `daily` |
| `--parallel-workers` | Number of parallel threads (1-20) | `5` |
| `--output-dir` | Output directory for reports | `output` |
| `--list-only` | List instances without extracting metrics | `false` |

### Advanced Options

| Option | Description | Example |
|--------|-------------|---------|
| `--lookback-days` | Custom lookback period (overrides frequency) | `--lookback-days 7` |
| `--config` | Custom config file path | `--config custom_config.json` |

---

## Report Types

> **⚡ Recommended:** Always use `--parallel-workers 5` for optimal performance

### Daily Report (Default)
- Time period: Last 24 hours
- Metrics: Average, Min, Max, P95 for last 24 hours
- Best for: Daily capacity monitoring
- **Extraction time**: ~50-60 min for 44 instances (vs 2-3 hours sequential)

```bash
# Recommended command (with parallel processing)
python3 main.py --region ap-southeast-1 --frequency daily --parallel-workers 5

# Or simply (parallel is now default):
python3 main.py --region ap-southeast-1
```

### Weekly Report
- Time period: Last 7 days
- Metrics: **HIGHEST** values from the past 7 days
- Best for: Weekly capacity reviews
- **Extraction time**: ~50-60 min for 44 instances (vs 2-3 hours sequential)

```bash
# Recommended command (with parallel processing)
python3 main.py --region ap-southeast-1 --frequency weekly --parallel-workers 5
```

### Monthly Report
- Time period: Last 30 days
- Metrics: **HIGHEST** values from the past 30 days
- Best for: Monthly capacity planning
- **Extraction time**: ~50-60 min for 44 instances (vs 2-3 hours sequential)

```bash
# Recommended command (with parallel processing)
python3 main.py --region ap-southeast-1 --frequency monthly --parallel-workers 5
```

### Custom Lookback Period
Get 7-day P95 in a daily report format:
```bash
# Recommended command (with parallel processing)
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 7 --parallel-workers 5
```

---

## Output Structure

Reports are organized by date and frequency:

```
output/
├── 20260101/
│   ├── Daily/
│   │   └── OceanBase_Daily_Report_20260101_143022.xlsx
│   ├── Weekly/
│   │   └── OceanBase_Weekly_Report_20260101_150033.xlsx
│   └── Monthly/
│       └── OceanBase_Monthly_Report_20260101_160044.xlsx
└── 20260102/
    └── Daily/
        └── OceanBase_Daily_Report_20260102_090011.xlsx
```

### Excel Report Tabs

Each report contains three tabs:

#### 1. Capacity Assessment Tab
Instance-level capacity and utilization (32 columns):

**Key Metrics:**
- Instance identification (ID, name, status)
- **CPU allocation**: total, allocated, available
- **Memory allocation**: total, allocated, available
- **Storage allocation**: total, allocated, actual usage, available
- **Log disk allocation**: total, allocated, available
- **Utilization metrics**: CPU %, Memory % (avg/min/max/P95)
- Disk utilization percentage
- Metadata: disk type, create time, zones

#### 2. Tenants Report Tab
Tenant-level resources and performance (62 columns):

**Key Metrics:**
- Tenant identification (ID, name, instance)
- **Resource allocation**: CPU cores, Memory GB, Disk GB, Log Disk GB
- **CPU utilization**: % usage (avg/max/min/P95)
- **Memory utilization**: % usage (avg/max/min/P95)
- **Session metrics**: active sessions, total sessions
- **SQL performance**: QPS, response time, breakdown by operation type (SELECT/INSERT/UPDATE/DELETE)
- **Transaction metrics**: TPS, commit log count, sync latency
- **I/O metrics**: read/write operations, latency
- **Network metrics**: bytes received/sent
- Connection info: address, port, status, max connections

#### 3. Summary Statistics Tab
Aggregate statistics across all instances:
- Total resource capacity
- Average utilization percentages
- Instance count and status distribution

---

## Metrics Collected

### Instance-Level Metrics (10 metrics × 4 statistics = 40 data points)

| Metric | Description | Statistics |
|--------|-------------|------------|
| **CPU Usage %** | CPU utilization percentage | avg, min, max, P95 |
| **CPU Percent** | Alternative CPU metric | avg, min, max, P95 |
| **Memory %** | Memory utilization percentage | avg, min, max, P95 |
| **Active Sessions** | Number of active sessions | avg, min, max, P95 |

### Tenant-Level Metrics (23 metrics × 4 statistics = 92 data points)

**Resource Utilization:**
- CPU usage % (avg/max/min/P95)
- Memory usage % (avg/max/min/P95)

**Session Metrics:**
- Active sessions
- All sessions

**SQL Performance:**
- SQL QPS (queries per second)
- SQL response time (ms)
- SELECT QPS
- INSERT QPS
- UPDATE QPS
- DELETE QPS
- REPLACE QPS

**Transaction Metrics:**
- Transaction TPS (transactions per second)
- Transaction partition TPS
- Commit log count
- Commit log sync latency (ms)
- Commit log size (MB)

**I/O Metrics:**
- I/O read operations/sec
- I/O write operations/sec
- I/O read latency (μs)
- I/O write latency (μs)
- Request queue time (μs)

**Network Metrics:**
- Network bytes received/sec
- Network bytes sent/sec

**Resource Allocation (from DescribeTenant API):**
- Allocated CPU (cores)
- Allocated Memory (GB)
- Allocated Log Disk (GB)
- Actual Disk Usage (GB)
- Number of units
- Unit CPU/Memory/Log Disk per resource unit

**Connection Information:**
- Connection address
- Connection port
- Connection status
- Maximum connections

---

## Troubleshooting

### Issue: Extraction taking too long

**Solution 1: Enable parallel mode (if not already enabled)**
```bash
python3 main.py --region ap-southeast-1 --parallel-workers 5
```

**Solution 2: Increase workers (if network is stable)**
```bash
python3 main.py --region ap-southeast-1 --parallel-workers 10
```

**Solution 3: Process in batches**
Split your 44 instances into batches of 10-15 instances each.

### Issue: API throttling errors

**Solution: Reduce parallel workers**
```bash
python3 main.py --region ap-southeast-1 --parallel-workers 3
```

Or use sequential mode:
```bash
python3 main.py --region ap-southeast-1 --parallel-workers 1
```

### Issue: Connection timeouts

**Solution: Use sequential mode**
```bash
python3 main.py --region ap-southeast-1 --parallel-workers 1
```

### Issue: Missing metrics in reports

**Cause:** Some tenants may not have all metrics available (e.g., inactive tenants, newly created tenants)

**Solution:** This is normal. The tool fetches all available metrics and skips unavailable ones gracefully.

### Issue: Authentication failed

**Solution:** Reconfigure Alibaba Cloud credentials
```bash
aliyun configure
```

---

## Best Practices

### For Daily Monitoring
```bash
# Run every morning for yesterday's data
python3 main.py --region ap-southeast-1 --frequency daily --parallel-workers 5
```

### For Weekly Reviews
```bash
# Run every Monday for last week's HIGHEST values
python3 main.py --region ap-southeast-1 --frequency weekly --parallel-workers 5
```

### For Monthly Capacity Planning
```bash
# Run on 1st of month for last 30 days HIGHEST values
python3 main.py --region ap-southeast-1 --frequency monthly --parallel-workers 5
```

### For Large Deployments (40+ instances)
```bash
# Use parallel mode with moderate concurrency
python3 main.py --region ap-southeast-1 --parallel-workers 5

# Expected time: ~50-60 minutes for 44 instances
```

### For Ad-hoc Analysis
```bash
# Extract specific instances with 7-day lookback
python3 main.py --region ap-southeast-1 \
  --instances ob2yqkpgcoxwu8 ob6lxzzelle2xs \
  --frequency daily \
  --lookback-days 7 \
  --parallel-workers 5
```

---

## Performance Comparison

### Solving the 2-Hour Extraction Issue

**Problem:** Daily/Weekly/Monthly reports for 44 instances taking 2 hours to complete

**Root Cause:** Using sequential mode (processing one tenant at a time)

**Solution:** Use parallel mode (processing multiple tenants simultaneously)

#### Extraction Time Comparison

| Method | Workers | Command | Time (44 instances) | Speedup |
|--------|---------|---------|---------------------|---------|
| **Sequential (old)** | 1 | `--parallel-workers 1` | ~2-3 hours | 1.0x |
| **✅ Recommended** | 5 | `--parallel-workers 5` | **~50-60 min** | **3.0x** |
| **Aggressive** | 10 | `--parallel-workers 10` | **~30-40 min** | **4.5x** |

#### Quick Fix

**For Daily Reports:**
```bash
# OLD (2-3 hours):
python3 main.py --region ap-southeast-1 --frequency daily

# NEW (50-60 min):
python3 main.py --region ap-southeast-1 --frequency daily --parallel-workers 5
```

**For Weekly Reports:**
```bash
# OLD (2-3 hours):
python3 main.py --region ap-southeast-1 --frequency weekly

# NEW (50-60 min):
python3 main.py --region ap-southeast-1 --frequency weekly --parallel-workers 5
```

**For Monthly Reports:**
```bash
# OLD (2-3 hours):
python3 main.py --region ap-southeast-1 --frequency monthly

# NEW (50-60 min):
python3 main.py --region ap-southeast-1 --frequency monthly --parallel-workers 5
```

#### Even Faster (Advanced)

If your network is stable and you want maximum speed:
```bash
# Can reduce to ~30-40 minutes (but may hit API rate limits)
python3 main.py --region ap-southeast-1 --frequency daily --parallel-workers 10
```

#### Batch Processing Alternative

If you experience API throttling with high concurrency, process in batches:
```bash
# Batch 1: First 11 instances (~12-15 min)
python3 main.py --region ap-southeast-1 --instances inst1 inst2 ... inst11 --parallel-workers 5

# Batch 2: Next 11 instances (~12-15 min)
python3 main.py --region ap-southeast-1 --instances inst12 inst13 ... inst22 --parallel-workers 5

# Batch 3: Next 11 instances (~12-15 min)
python3 main.py --region ap-southeast-1 --instances inst23 inst24 ... inst33 --parallel-workers 5

# Batch 4: Last 11 instances (~12-15 min)
python3 main.py --region ap-southeast-1 --instances inst34 inst35 ... inst44 --parallel-workers 5

# Total time: ~48-60 minutes (spread across 4 batches)
```

---

## Project Structure

```
oceanbase-reporter/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── config/
│   └── config.json        # Configuration file (optional)
├── src/
│   ├── auth.py            # Authentication handling
│   ├── oceanbase_client.py # OceanBase API client (with parallel fetching)
│   ├── csv_exporter.py    # CSV export functionality
│   └── excel_exporter.py  # Excel export functionality
├── output/                # Generated reports (auto-created)
│   └── YYYYMMDD/
│       ├── Daily/
│       ├── Weekly/
│       └── Monthly/
└── README.md              # This file
```

---

## API Metrics Coverage

### ✅ Available Metrics (33 total)

**Instance Level (10):**
- CPU usage, CPU percent
- Memory percent
- Active sessions
- (Others available but excluded from reports for clarity)

**Tenant Level (23):**
- CPU usage %, Memory usage %
- Active sessions, All sessions
- SQL QPS, SQL RT, SQL breakdown (5 types)
- Transaction TPS (2 types), commit log metrics (3 types)
- I/O metrics (4 types), Request queue time
- Network metrics (2 types)

### ❌ Unavailable Metrics

The following are NOT available via Alibaba Cloud OceanBase API:

- Node-level or server-level metrics
- Replica information or distribution
- Zone-level utilization breakdown
- Instance-level memstore details
- Some storage-level metrics

**Note:** These limitations are from the Alibaba Cloud API itself, not this tool.

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review command-line options for correct usage
3. Verify Alibaba Cloud credentials are configured
4. Check network connectivity to Alibaba Cloud APIs

---

## License

Proprietary - Internal use only

---

## Changelog

### v2.0.0 (2026-01-02)
- ✅ Added parallel tenant metric fetching (3.4x performance improvement)
- ✅ Verified and enabled 13 additional tenant metrics (33 total)
- ✅ Fixed tenant memory utilization metrics collection
- ✅ Optimized Capacity Assessment tab (removed 28 unnecessary columns)
- ✅ Added configurable concurrency via `--parallel-workers`
- ✅ Comprehensive documentation and cleanup

### v1.0.0
- Initial release with sequential extraction
- Basic instance and tenant metrics collection
- Excel report generation
