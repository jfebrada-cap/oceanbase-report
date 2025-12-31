# 7-Day P95 CPU Usage in Daily Reports - Guide

## Quick Start

To get the **maximum P95 CPU usage from the last 7 days** in your daily report:

```bash
cd /Users/jerielfebrada/Desktop/Projects/oceanbase-reporter
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 7
```

## What This Does

### Standard Daily Report (24 hours)
```bash
python3 main.py --region ap-southeast-1 --frequency daily
```
- Fetches metrics from: **Last 24 hours**
- P95 calculation: Based on ~24 datapoints (1 per hour)
- Result: P95 for yesterday's traffic

### Daily Report with 7-Day Lookback
```bash
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 7
```
- Fetches metrics from: **Last 7 days (168 hours)**
- P95 calculation: Based on ~168 datapoints (1 per hour × 7 days)
- Result: **HIGHEST P95 from the past week**

## How P95 is Calculated

### Example Scenario

**Instance: gcash_prod02**

**Last 7 days of hourly CPU utilization:**
```
Day 1: [45%, 52%, 48%, 55%, 62%, 58%, 51%, ...]  ← 24 datapoints
Day 2: [47%, 54%, 50%, 57%, 65%, 60%, 53%, ...]  ← 24 datapoints
Day 3: [88%, 92%, 87%, 91%, 95%, 89%, 85%, ...]  ← Peak day (maintenance)
Day 4: [46%, 53%, 49%, 56%, 63%, 59%, 52%, ...]
Day 5: [48%, 55%, 51%, 58%, 66%, 61%, 54%, ...]
Day 6: [50%, 57%, 53%, 60%, 68%, 63%, 56%, ...]
Day 7: [49%, 56%, 52%, 59%, 67%, 62%, 55%, ...]
```

**Total: 168 hourly datapoints**

### P95 Calculation:
1. Sort all 168 values from lowest to highest
2. Take the value at position 160 (95% × 168 = 159.6 ≈ 160)
3. This represents the CPU usage that was exceeded only 5% of the time

**Result:** `cpu_p95 = 89%` (from Day 3's peak period)

This tells you: *"For 95% of the time in the last 7 days, CPU was below 89%"*

## Column Values in Report

When you run with `--lookback-days 7`, the report will show:

| Column | Description | Example Value |
|--------|-------------|---------------|
| `cpu_utilization_avg_%` | Average across 7 days | 58.3% |
| `cpu_utilization_min_%` | Lowest value in 7 days | 45.0% |
| `cpu_utilization_max_%` | Highest value in 7 days (capped at 100%) | 95.0% |
| `cpu_utilization_p95_%` | 95th percentile (peak capacity) | 89.0% |

## Use Cases

### 1. Capacity Planning
**Question:** *"What's the maximum CPU I need to handle 95% of my traffic?"*

**Command:**
```bash
python3 main.py --region ap-southeast-1 --lookback-days 30
```

**Answer:** Check `cpu_p95` column - this is your sizing target.

### 2. Peak Detection
**Question:** *"Did we have any CPU spikes in the last week?"*

**Command:**
```bash
python3 main.py --region ap-southeast-1 --lookback-days 7
```

**Answer:** Compare `cpu_p95` vs `cpu_avg`:
- If `cpu_p95` >> `cpu_avg`: You had spikes
- If `cpu_p95` ≈ `cpu_avg`: Consistent load

### 3. Trend Analysis
**Question:** *"How do 7-day peaks compare to 30-day peaks?"*

**Commands:**
```bash
# 7-day P95
python3 main.py --region ap-southeast-1 --lookback-days 7

# 30-day P95
python3 main.py --region ap-southeast-1 --lookback-days 30
```

**Analysis:** Compare the P95 values between reports.

## Important Notes

### 1. All Metrics Use Same Lookback Period

When you specify `--lookback-days 7`, it affects **ALL metrics**:
- ✅ CPU utilization (avg, min, max, P95)
- ✅ Memory utilization (avg, min, max, P95)
- ✅ Disk utilization (avg, min, max, P95)
- ✅ Tenant metrics (CPU, memory, sessions, I/O)

### 2. P95 vs Max

- **Max** = Absolute highest value (can be a spike/anomaly)
- **P95** = High but sustainable (excludes top 5% outliers)

**Example:**
```
Values: [50%, 52%, 54%, 55%, 57%, 58%, 95%]  ← One spike to 95%

Max  = 95%   ← Includes the spike
P95  = 58%   ← Excludes the spike (more representative)
```

For capacity planning, **P95 is more useful** than Max because it filters out rare anomalies.

### 3. Capped at 100%

All percentage metrics are capped at 100% max, even if CloudMonitor API returns higher values.

## Comparison: Different Lookback Periods

| Lookback | Datapoints | Best For | Command |
|----------|------------|----------|---------|
| 1 day (default) | ~24 | Daily operations | `--frequency daily` |
| 3 days | ~72 | Short-term trends | `--lookback-days 3` |
| 7 days | ~168 | Weekly capacity review | `--lookback-days 7` |
| 14 days | ~336 | Bi-weekly trends | `--lookback-days 14` |
| 30 days | ~720 | Monthly capacity planning | `--frequency monthly` |

## Example Output

### Daily Report (24h lookback)
```
Report Frequency: DAILY
Time Period: Last 24 hours

Instance: gcash_prod02
  CPU: avg=58.5%, min=45.2%, max=72.3%, P95=68.9%
```

### Daily Report with 7-Day Lookback
```
Report Frequency: DAILY
Time Period: Last 7 days (HIGHEST utilization including P95)
Custom Lookback: 7 days

Instance: gcash_prod02
  CPU: avg=61.2%, min=45.2%, max=95.0%, P95=89.0%
```

Notice:
- `avg` is higher (average of 7 days vs 1 day)
- `max` is much higher (caught the peak on Day 3)
- `P95` is higher (sustainable peak capacity over 7 days)

## Testing

**Quick test to verify it's working:**

```bash
# Run with 1 day (default)
python3 main.py --region ap-southeast-1 --frequency daily

# Run with 7 days
python3 main.py --region ap-southeast-1 --frequency daily --lookback-days 7

# Compare the P95 values - the 7-day version should be higher
```

## Troubleshooting

### Issue: Same P95 for 1-day and 7-day

**Possible causes:**
- Your load is very consistent (no peaks in last 7 days)
- CloudMonitor aggregation is limiting datapoints

**Solution:** This is normal if your traffic is steady.

### Issue: 7-day P95 seems too high

**Possible causes:**
- There was a legitimate spike/peak in the last 7 days
- Check `max` value - if it's close to P95, you had sustained high load

**Solution:** Investigate the spike period in CloudMonitor console.

## Recommendations

For most use cases:

- **Daily monitoring:** Use default 24-hour lookback
- **Weekly reviews:** Use `--lookback-days 7`
- **Capacity planning:** Use `--frequency monthly` or `--lookback-days 30`

The 7-day P95 is particularly useful for:
- Sizing new instances (provision for P95, not max)
- Detecting weekly patterns (if weekends differ from weekdays)
- Planning for growth (compare week-over-week P95 trends)
