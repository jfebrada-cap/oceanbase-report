"""
Historical Data Aggregator for OceanBase Reports
Aggregates daily CSV reports into weekly and monthly summaries
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import glob


class HistoricalAggregator:
    """Aggregate historical daily reports into weekly/monthly summaries"""

    def __init__(self, output_dir: str = 'output'):
        """
        Initialize Historical Aggregator

        Args:
            output_dir: Directory containing daily CSV reports
        """
        self.output_dir = Path(output_dir)

    def find_daily_reports(self, days_back: int = 7) -> Dict[str, List[str]]:
        """
        Find daily CSV reports from the past N days

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary with 'capacity' and 'tenants' lists of file paths
        """
        reports = {
            'capacity': [],
            'tenants': []
        }

        # Search for capacity assessment files
        capacity_pattern = str(self.output_dir / 'oceanbase_capacity_assessment_*.csv')
        capacity_files = glob.glob(capacity_pattern)

        # Search for tenants files
        tenants_pattern = str(self.output_dir / 'oceanbase_tenants_*.csv')
        tenants_files = glob.glob(tenants_pattern)

        # Filter by date (last N days)
        cutoff_date = datetime.now() - timedelta(days=days_back)

        for filepath in capacity_files:
            # Extract date from filename: oceanbase_capacity_assessment_YYYYMMDD_HHMMSS.csv
            filename = Path(filepath).name
            try:
                date_str = filename.split('_')[-2]  # YYYYMMDD
                file_date = datetime.strptime(date_str, '%Y%m%d')
                if file_date >= cutoff_date:
                    reports['capacity'].append(filepath)
            except (ValueError, IndexError):
                continue

        for filepath in tenants_files:
            filename = Path(filepath).name
            try:
                date_str = filename.split('_')[-2]  # YYYYMMDD
                file_date = datetime.strptime(date_str, '%Y%m%d')
                if file_date >= cutoff_date:
                    reports['tenants'].append(filepath)
            except (ValueError, IndexError):
                continue

        # Sort by filename (chronological)
        reports['capacity'].sort()
        reports['tenants'].sort()

        return reports

    def aggregate_capacity_data(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Aggregate capacity assessment data from multiple daily reports
        Extracts the HIGHEST utilization metrics across all days

        Args:
            file_paths: List of CSV file paths to aggregate

        Returns:
            Aggregated DataFrame with highest utilization metrics
        """
        if not file_paths:
            return pd.DataFrame()

        all_data = []
        for filepath in file_paths:
            try:
                df = pd.read_csv(filepath)
                # Add extraction date
                filename = Path(filepath).name
                date_str = filename.split('_')[-2]
                df['extraction_date'] = date_str
                all_data.append(df)
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")
                continue

        if not all_data:
            return pd.DataFrame()

        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)

        # Group by instance_id and get HIGHEST utilization
        numeric_cols = combined_df.select_dtypes(include=['float64', 'int64']).columns

        agg_dict = {}

        # For utilization metrics, get MAX (highest)
        utilization_cols = ['cpu_avg', 'cpu_max', 'cpu_p95',
                           'memory_avg', 'memory_max', 'memory_p95',
                           'disk_utilization_pct']

        for col in numeric_cols:
            if col not in ['instance_id']:
                if any(util in col for util in utilization_cols):
                    # Get HIGHEST utilization
                    agg_dict[col] = 'max'
                else:
                    # For capacity metrics, take the latest value
                    agg_dict[col] = 'last'

        # Add categorical columns - take the latest
        categorical_cols = ['instance_name', 'status', 'series', 'zones', 'version',
                           'create_time', 'expire_time', 'disk_type']
        for col in categorical_cols:
            if col in combined_df.columns:
                agg_dict[col] = 'last'

        grouped = combined_df.groupby('instance_id').agg(agg_dict)

        # Reset index to make instance_id a column again
        result = grouped.reset_index()

        # Add metadata
        result['period_start'] = min([Path(f).name.split('_')[-2] for f in file_paths])
        result['period_end'] = max([Path(f).name.split('_')[-2] for f in file_paths])
        result['num_days_analyzed'] = len(file_paths)

        return result

    def aggregate_tenants_data(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Aggregate tenants data from multiple daily reports

        Args:
            file_paths: List of CSV file paths to aggregate

        Returns:
            Aggregated DataFrame with min/max/avg metrics
        """
        if not file_paths:
            return pd.DataFrame()

        all_data = []
        for filepath in file_paths:
            try:
                df = pd.read_csv(filepath)
                # Add extraction date
                filename = Path(filepath).name
                date_str = filename.split('_')[-2]
                df['extraction_date'] = date_str
                all_data.append(df)
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")
                continue

        if not all_data:
            return pd.DataFrame()

        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)

        # Group by instance_id and tenant_id
        numeric_cols = combined_df.select_dtypes(include=['float64', 'int64']).columns

        agg_dict = {}
        for col in numeric_cols:
            if col not in ['instance_id', 'tenant_id']:
                agg_dict[col] = ['min', 'max', 'mean']

        # Add categorical columns
        categorical_cols = ['instance_name', 'tenant_name', 'status', 'tenant_mode', 'charset']
        for col in categorical_cols:
            if col in combined_df.columns:
                agg_dict[col] = 'first'

        grouped = combined_df.groupby(['instance_id', 'tenant_id']).agg(agg_dict)

        # Flatten multi-level columns
        grouped.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col
                          for col in grouped.columns]

        # Reset index
        result = grouped.reset_index()

        # Add metadata
        result['aggregation_start'] = min([f.split('_')[-2] for f in file_paths])
        result['aggregation_end'] = max([f.split('_')[-2] for f in file_paths])
        result['num_reports_aggregated'] = len(file_paths)

        return result

    def generate_weekly_report(self) -> tuple:
        """
        Generate weekly report from the last 7 days of daily reports

        Returns:
            Tuple of (capacity_df, tenants_df)
        """
        print("Generating weekly report from historical data...")
        reports = self.find_daily_reports(days_back=7)

        if not reports['capacity'] and not reports['tenants']:
            print("  No daily reports found for the past 7 days")
            return None, None

        print(f"  Found {len(reports['capacity'])} capacity reports")
        print(f"  Found {len(reports['tenants'])} tenant reports")

        capacity_df = self.aggregate_capacity_data(reports['capacity'])
        tenants_df = self.aggregate_tenants_data(reports['tenants'])

        return capacity_df, tenants_df

    def generate_monthly_report(self) -> tuple:
        """
        Generate monthly report from the last 30 days of daily reports

        Returns:
            Tuple of (capacity_df, tenants_df)
        """
        print("Generating monthly report from historical data...")
        reports = self.find_daily_reports(days_back=30)

        if not reports['capacity'] and not reports['tenants']:
            print("  No daily reports found for the past 30 days")
            return None, None

        print(f"  Found {len(reports['capacity'])} capacity reports")
        print(f"  Found {len(reports['tenants'])} tenant reports")

        capacity_df = self.aggregate_capacity_data(reports['capacity'])
        tenants_df = self.aggregate_tenants_data(reports['tenants'])

        return capacity_df, tenants_df
