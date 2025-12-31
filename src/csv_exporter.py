"""
CSV Exporter for OceanBase capacity assessment reports
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class CSVExporter:
    """Export OceanBase data to CSV format"""

    def __init__(self, output_dir: str = 'output'):
        """
        Initialize CSV Exporter

        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def export_instances_report(
        self,
        instances_data: List[Dict],
        filename_prefix: str = 'oceanbase_instances'
    ) -> str:
        """
        Export instances information to CSV

        Args:
            instances_data: List of instance dictionaries
            filename_prefix: Prefix for the CSV filename

        Returns:
            Path to the created CSV file
        """
        if not instances_data:
            print("No instance data to export")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = self.output_dir / filename

        df = pd.DataFrame(instances_data)

        # Reorder columns for better readability
        column_order = [
            'instance_id', 'instance_name', 'status', 'series',

            # CPU Capacity Allocation (Capacity Center fields)
            'total_cpu', 'allocated_cpu', 'available_cpu', 'cpu_allocation_pct',
            'unit_cpu', 'original_total_cpu',

            # Memory Capacity Allocation (Capacity Center fields)
            'total_memory', 'allocated_memory', 'available_memory', 'memory_allocation_pct',
            'unit_memory', 'original_total_memory',

            # Storage (Data Disk) Capacity Allocation (Capacity Center fields)
            'total_storage', 'allocated_storage', 'actual_data_usage', 'available_storage',
            'storage_allocation_pct', 'max_disk_used_pct',
            'unit_disk_size', 'original_total_disk',

            # Log Disk Capacity Allocation (Capacity Center fields)
            'total_log_disk', 'allocated_log_disk', 'available_log_disk', 'log_disk_allocation_pct',
            'max_log_assigned_pct', 'unit_log_disk', 'original_total_log_disk',

            # Instance metadata
            'disk_type',

            # Utilization metrics (from CloudMonitor)
            'cpu_avg', 'cpu_min', 'cpu_max', 'cpu_p95',
            'memory_avg', 'memory_min', 'memory_max', 'memory_p95',
            'disk_avg', 'disk_min', 'disk_max', 'disk_p95',
            'disk_utilization_pct',

            # Instance info
            'create_time', 'expire_time', 'zones', 'version', 'vpc_id'
        ]

        # Only include columns that exist
        available_columns = [col for col in column_order if col in df.columns]
        remaining_columns = [col for col in df.columns if col not in column_order]
        final_columns = available_columns + remaining_columns

        df = df[final_columns]
        df.to_csv(filepath, index=False)

        print(f"✓ Instances report saved to: {filepath}")
        return str(filepath)

    def export_tenants_report(
        self,
        tenants_data: List[Dict],
        filename_prefix: str = 'oceanbase_tenants'
    ) -> str:
        """
        Export tenants information to CSV

        Args:
            tenants_data: List of tenant dictionaries
            filename_prefix: Prefix for the CSV filename

        Returns:
            Path to the created CSV file
        """
        if not tenants_data:
            print("No tenant data to export")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = self.output_dir / filename

        df = pd.DataFrame(tenants_data)

        # Reorder columns for better readability
        column_order = [
            'instance_id', 'instance_name', 'tenant_id', 'tenant_name',
            'tenant_mode',

            # Tenant Resource Allocation (Capacity Center fields - from DescribeTenant API)
            'tenant_allocated_cpu',
            'tenant_allocated_memory',
            'tenant_actual_disk_usage',

            # CPU Usage Metrics (from CloudMonitor API)
            'cpu_usage_percent_avg', 'cpu_usage_percent_max', 'cpu_usage_percent_min', 'cpu_usage_percent_p95',

            # Log Disk Allocation
            'tenant_allocated_log_disk',

            # Tenant Connection Information
            'max_connections',

            # Memory metrics (from CloudMonitor API) - percentage only
            'memory_usage_percent_avg', 'memory_usage_percent_max', 'memory_usage_percent_min',

            # Session/Connection metrics (from CloudMonitor API)
            'active_sessions_avg', 'active_sessions_max', 'active_sessions_min',

            # Tenant info
            'create_time'
        ]

        # Only include columns that exist
        available_columns = [col for col in column_order if col in df.columns]
        remaining_columns = [col for col in df.columns if col not in column_order]
        final_columns = available_columns + remaining_columns

        df = df[final_columns]
        df.to_csv(filepath, index=False)

        print(f"✓ Tenants report saved to: {filepath}")
        return str(filepath)

    def export_comprehensive_report(
        self,
        data: List[Dict],
        filename_prefix: str = 'oceanbase_capacity_assessment'
    ) -> str:
        """
        Export comprehensive capacity assessment report to CSV

        Args:
            data: List of comprehensive data dictionaries
            filename_prefix: Prefix for the CSV filename

        Returns:
            Path to the created CSV file
        """
        if not data:
            print("No data to export")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = self.output_dir / filename

        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)

        print(f"✓ Comprehensive report saved to: {filepath}")
        print(f"  Total records: {len(df)}")
        print(f"  Columns: {', '.join(df.columns.tolist())}")

        return str(filepath)

    def export_summary_statistics(
        self,
        instances_data: List[Dict],
        filename_prefix: str = 'oceanbase_summary'
    ) -> str:
        """
        Export summary statistics to CSV

        Args:
            instances_data: List of instance dictionaries with metrics
            filename_prefix: Prefix for the CSV filename

        Returns:
            Path to the created CSV file
        """
        if not instances_data:
            print("No data to export")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = self.output_dir / filename

        df = pd.DataFrame(instances_data)

        # Calculate summary statistics
        summary_data = {
            'metric': [],
            'total_instances': [],
            'average': [],
            'maximum': [],
            'minimum': []
        }

        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns

        for col in numeric_columns:
            if col in ['cpu', 'memory', 'disk_size']:
                summary_data['metric'].append(col)
                summary_data['total_instances'].append(len(df))
                summary_data['average'].append(df[col].mean())
                summary_data['maximum'].append(df[col].max())
                summary_data['minimum'].append(df[col].min())

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(filepath, index=False)

        print(f"✓ Summary statistics saved to: {filepath}")
        return str(filepath)
