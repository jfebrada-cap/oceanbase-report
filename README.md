# OceanBase Capacity Assessment Reporter

A high-performance Python tool to extract comprehensive OceanBase instance and tenant metrics from Alibaba Cloud for capacity assessment and planning.

## 🚀 Quick Start

**Primary extraction command (recommended for production use):**

```bash
python3 main.py --region ap-southeast-1 --frequency weekly --instance-workers 15 --parallel-workers 50
```

**What this does:**
- `--region ap-southeast-1` - Extract from Asia Pacific (Singapore) region
- `--frequency weekly` - Generate weekly report with 7-day highest utilization values
- `--instance-workers 15` - Process 15 instances in parallel simultaneously
- `--parallel-workers 50` - Fetch 50 tenant metrics concurrently per instance

**Expected performance:**
- **5-10x faster** than sequential processing
- Large deployments (15+ instances, 30+ tenants): ~10-15 minutes
- Medium deployments (5-15 instances): ~5-7 minutes
- Small deployments (1-5 instances): ~2-3 minutes

## Features

- **⚡ High-Performance Parallel Extraction**
  - Parallel instance processing (configurable: 5-15 workers)
  - Parallel tenant metric fetching (configurable: 20-50 workers)
  - 5-10x faster than sequential processing
  - Real-time progress tracking

- **📊 Comprehensive Metrics Collection**
  - **Instance-level**: CPU, memory, disk utilization with avg/min/max/P95
  - **Tenant-level**: CPU, memory, SQL, I/O, network, connection metrics
  - **Capacity allocation**: Total/allocated/available breakdown for all resources
  - **Time series data**: Daily, weekly, or monthly aggregation

- **📈 Professional Excel Reports**
  - Multi-tab workbooks with formatted tables
  - Capacity Assessment tab (instance overview)
  - Tenants Report tab (detailed tenant metrics)
  - Auto-sized columns and professional formatting

- **🗓️ Flexible Reporting Periods**
  - Daily reports (24-hour metrics)
  - Weekly reports (7-day highest values)
  - Monthly reports (30-day highest values)
  - Custom lookback periods

---

## Installation

**Prerequisites:**
- Python 3.7 or higher
- Alibaba Cloud account with OceanBase access
- Alibaba Cloud CLI configured with credentials

**Steps:**

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Configure Alibaba Cloud credentials:
```bash
aliyun configure
```

Or set environment variables:
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-secret-key"
export ALIBABA_CLOUD_REGION="ap-southeast-1"
```

3. Run extraction:
```bash
python3 main.py --region ap-southeast-1 --frequency weekly --instance-workers 15 --parallel-workers 50
```

---

## Usage Examples

### Basic Commands

**Weekly report (recommended for production):**
```bash
python3 main.py --region ap-southeast-1 --frequency weekly --instance-workers 15 --parallel-workers 50
```

**Daily report:**
```bash
python3 main.py --region ap-southeast-1 --frequency daily --instance-workers 10 --parallel-workers 20
```

**Monthly report:**
```bash
python3 main.py --region ap-southeast-1 --frequency monthly --instance-workers 15 --parallel-workers 50
```

**Extract specific instances:**
```bash
python3 main.py --region ap-southeast-1 --instances ob2yqkpgcoxwu8 ob6lxzzelle2xs --instance-workers 5 --parallel-workers 20
```

### Performance Tuning

**For large deployments (15+ instances, 30+ tenants):**
```bash
python3 main.py --region ap-southeast-1 --frequency weekly --instance-workers 15 --parallel-workers 50
```

**For medium deployments (5-15 instances):**
```bash
python3 main.py --region ap-southeast-1 --frequency weekly --instance-workers 10 --parallel-workers 30
```

**For small deployments (1-5 instances):**
```bash
python3 main.py --region ap-southeast-1 --frequency weekly --instance-workers 5 --parallel-workers 20
```

**If experiencing API rate limiting:**
```bash
python3 main.py --region ap-southeast-1 --frequency weekly --instance-workers 5 --parallel-workers 15
```

---

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | Alibaba Cloud region (e.g., ap-southeast-1) | From credentials |
| `--frequency` | Report frequency: `daily`, `weekly`, `monthly` | `daily` |
| `--instance-workers` | Parallel instance processing workers (5-15) | `10` |
| `--parallel-workers` | Parallel tenant metric workers (20-50) | `20` |
| `--instances` | Specific instance IDs to process | All instances |
| `--output-dir` | Output directory for reports | `output` |
| `--lookback-days` | Custom lookback period (overrides frequency) | Based on frequency |
| `--list-only` | List instances without extracting metrics | `false` |
| `--config` | Custom config file path | `config/config.json` |

---

## Report Types

### Daily Report
- **Time period:** Last 24 hours
- **Metrics:** Average, Min, Max, P95 for last 24 hours
- **Best for:** Daily capacity monitoring

### Weekly Report (Recommended)
- **Time period:** Last 7 days
- **Metrics:** HIGHEST values from the past 7 days
- **Best for:** Weekly capacity reviews and capacity planning

### Monthly Report
- **Time period:** Last 30 days
- **Metrics:** HIGHEST values from the past 30 days
- **Best for:** Monthly capacity planning and trend analysis

---

## Output Structure

Reports are organized by date and frequency:

```
output/
├── 20260102/
│   ├── Daily/
│   │   └── OceanBase_Daily_Report_20260102_143022.xlsx
│   ├── Weekly/
│   │   └── OceanBase_Weekly_Report_20260102_150033.xlsx
│   └── Monthly/
│       └── OceanBase_Monthly_Report_20260102_160044.xlsx
```

### Excel Report Tabs

Each Excel report contains two tabs:

#### 1. Capacity Assessment
Instance-level capacity and utilization metrics:
- Instance identification (ID, name, status, series)
- CPU allocation (total, allocated, available) and utilization (avg/min/max/P95)
- Memory allocation (total, allocated, available) and utilization (avg/min/max/P95)
- Storage allocation (total, allocated, actual usage, available) and utilization
- Log disk allocation and utilization
- Network, connection, I/O metrics

#### 2. Tenants Report
Tenant-level resources and performance metrics:
- Tenant identification (ID, name, instance, mode)
- Resource allocation (CPU, Memory, Disk, Log Disk)
- CPU and Memory utilization (min/avg/max/P95)
- Session and connection metrics
- SQL performance (QPS, response time, operation breakdown)
- Transaction metrics (TPS, commit log)
- I/O and network metrics

---

## Troubleshooting

### Extraction taking too long
- Increase `--instance-workers` and `--parallel-workers` values
- Example: `--instance-workers 15 --parallel-workers 50`

### API throttling errors
- Reduce worker counts: `--instance-workers 5 --parallel-workers 15`
- Process instances in smaller batches using `--instances` option

### Authentication failed
- Reconfigure credentials: `aliyun configure`
- Or set environment variables with valid access keys

### Missing metrics in reports
- Normal behavior - some tenants may not have all metrics available
- Tool gracefully skips unavailable metrics

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

## License

Proprietary - Internal use only

