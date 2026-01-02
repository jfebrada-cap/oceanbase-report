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

            # Utilization metrics (from CloudMonitor) - Legacy format
            'cpu_avg', 'cpu_min', 'cpu_max', 'cpu_p95',
            'memory_avg', 'memory_min', 'memory_max', 'memory_p95',
            'disk_avg', 'disk_min', 'disk_max', 'disk_p95',
            'disk_utilization_pct',

            # ALL Instance CloudMonitor Metrics (avg/min/max/p95)
            # Active sessions
            'active_sessions_avg', 'active_sessions_min', 'active_sessions_max', 'active_sessions_p95',

            # Data size
            'data_size_gb_avg', 'data_size_gb_min', 'data_size_gb_max', 'data_size_gb_p95',

            # Disk metrics
            'disk_usage_percent_avg', 'disk_usage_percent_min', 'disk_usage_percent_max', 'disk_usage_percent_p95',
            'disk_used_gb_avg', 'disk_used_gb_min', 'disk_used_gb_max', 'disk_used_gb_p95',
            'disk_total_gb_avg', 'disk_total_gb_min', 'disk_total_gb_max', 'disk_total_gb_p95',

            # Network metrics
            'network_in_bytes_per_sec_avg', 'network_in_bytes_per_sec_min', 'network_in_bytes_per_sec_max', 'network_in_bytes_per_sec_p95',
            'network_out_bytes_per_sec_avg', 'network_out_bytes_per_sec_min', 'network_out_bytes_per_sec_max', 'network_out_bytes_per_sec_p95',

            # Connection metrics
            'connection_count_avg', 'connection_count_min', 'connection_count_max', 'connection_count_p95',
            'max_connections_limit_avg', 'max_connections_limit_min', 'max_connections_limit_max', 'max_connections_limit_p95',

            # Cache metrics
            'cache_hit_rate_percent_avg', 'cache_hit_rate_percent_min', 'cache_hit_rate_percent_max', 'cache_hit_rate_percent_p95',

            # I/O metrics
            'io_read_ops_per_sec_avg', 'io_read_ops_per_sec_min', 'io_read_ops_per_sec_max', 'io_read_ops_per_sec_p95',
            'io_write_ops_per_sec_avg', 'io_write_ops_per_sec_min', 'io_write_ops_per_sec_max', 'io_write_ops_per_sec_p95',
            'io_util_percent_avg', 'io_util_percent_min', 'io_util_percent_max', 'io_util_percent_p95',

            # SQL metrics
            'sql_count_per_sec_avg', 'sql_count_per_sec_min', 'sql_count_per_sec_max', 'sql_count_per_sec_p95',
            'sql_rt_ms_avg', 'sql_rt_ms_min', 'sql_rt_ms_max', 'sql_rt_ms_p95',
            'sql_select_per_sec_avg', 'sql_select_per_sec_min', 'sql_select_per_sec_max', 'sql_select_per_sec_p95',
            'sql_insert_per_sec_avg', 'sql_insert_per_sec_min', 'sql_insert_per_sec_max', 'sql_insert_per_sec_p95',
            'sql_update_per_sec_avg', 'sql_update_per_sec_min', 'sql_update_per_sec_max', 'sql_update_per_sec_p95',
            'sql_delete_per_sec_avg', 'sql_delete_per_sec_min', 'sql_delete_per_sec_max', 'sql_delete_per_sec_p95',

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
        Export tenants information to CSV with renamed columns

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

        # Rename columns to user-friendly display names
        rename_map = {
            'tenant_allocated_cpu': 'Allocated_CPU',
            'tenant_allocated_memory': 'Allocated_Mem',
            'tenant_allocated_disk': 'Allocated_Disk',
            'tenant_actual_disk_usage': 'disk_usage',
            'cpu_usage_percent_min': 'min_CPU_Util',
            'cpu_usage_percent_avg': 'avg_CPU_Util',
            'cpu_usage_percent_max': 'max_CPU_Util',
            'cpu_usage_percent_p95': 'p95_CPU_Util',
            'tenant_allocated_log_disk': 'Allocated_log_disk',
            'tenant_log_disk_usage': 'log_disk_usage',
            'memory_usage_percent_min': 'min_Mem_Util',
            'memory_usage_percent_avg': 'avg_Mem_Util',
            'memory_usage_percent_max': 'max_Mem_Util',
            'memory_usage_percent_p95': 'p95_Mem_Util',
        }

        # Apply column renaming
        df = df.rename(columns=rename_map)

        # Reorder columns for better readability (using renamed column names)
        column_order = [
            'instance_id', 'instance_name', 'tenant_id', 'tenant_name',
            'tenant_mode',

            # Tenant Resource Allocation
            'Allocated_CPU',
            'Allocated_Mem',
            'Allocated_Disk',
            'disk_usage',

            # CPU Usage Metrics
            'min_CPU_Util', 'avg_CPU_Util', 'max_CPU_Util', 'p95_CPU_Util',
            'cpu_usage_avg_cores_avg', 'cpu_usage_avg_cores_max', 'cpu_usage_avg_cores_min', 'cpu_usage_avg_cores_p95',

            # Log Disk Allocation and Usage
            'Allocated_log_disk',
            'log_disk_usage',

            # Memory Usage Metrics
            'min_Mem_Util', 'avg_Mem_Util', 'max_Mem_Util', 'p95_Mem_Util',
            'memstore_percent_avg', 'memstore_percent_max', 'memstore_percent_min', 'memstore_percent_p95',
            'memstore_used_mb_avg', 'memstore_used_mb_max', 'memstore_used_mb_min', 'memstore_used_mb_p95',
            'memstore_total_mb_avg', 'memstore_total_mb_max', 'memstore_total_mb_min', 'memstore_total_mb_p95',

            # Tenant Connection Information
            'max_connections',
            'sessions_avg',

            # Session/Connection metrics (from CloudMonitor API)
            'sessions_max', 'sessions_min', 'sessions_p95',
            'connection_avg', 'connection_max', 'connection_min', 'connection_p95',

            # QPS Metrics
            'qps_avg', 'qps_max', 'qps_min', 'qps_p95',
            'sql_select_qps_avg', 'sql_select_qps_max', 'sql_select_qps_min', 'sql_select_qps_p95',
            'sql_insert_qps_avg', 'sql_insert_qps_max', 'sql_insert_qps_min', 'sql_insert_qps_p95',
            'sql_update_qps_avg', 'sql_update_qps_max', 'sql_update_qps_min', 'sql_update_qps_p95',
            'sql_delete_qps_avg', 'sql_delete_qps_max', 'sql_delete_qps_min', 'sql_delete_qps_p95',
            'sql_replace_qps_avg', 'sql_replace_qps_max', 'sql_replace_qps_min', 'sql_replace_qps_p95',

            # TPS Metrics
            'tps_avg', 'tps_max', 'tps_min', 'tps_p95',
            'transaction_avg_rt_us_avg', 'transaction_avg_rt_us_max', 'transaction_avg_rt_us_min', 'transaction_avg_rt_us_p95',

            # I/O Operations Metrics
            'io_ops_per_sec_avg', 'io_ops_per_sec_max', 'io_ops_per_sec_min', 'io_ops_per_sec_p95',
            'io_avg_rt_us_avg', 'io_avg_rt_us_max', 'io_avg_rt_us_min', 'io_avg_rt_us_p95',
            'io_throughput_bytes_avg', 'io_throughput_bytes_max', 'io_throughput_bytes_min', 'io_throughput_bytes_p95',
            'io_read_ops_per_sec_avg', 'io_read_ops_per_sec_max', 'io_read_ops_per_sec_min', 'io_read_ops_per_sec_p95',
            'io_write_ops_per_sec_avg', 'io_write_ops_per_sec_max', 'io_write_ops_per_sec_min', 'io_write_ops_per_sec_p95',
            'io_read_bytes_per_sec_avg', 'io_read_bytes_per_sec_max', 'io_read_bytes_per_sec_min', 'io_read_bytes_per_sec_p95',
            'io_write_bytes_per_sec_avg', 'io_write_bytes_per_sec_max', 'io_write_bytes_per_sec_min', 'io_write_bytes_per_sec_p95',

            # Cache Metrics
            'cache_hit_rate_percent_avg', 'cache_hit_rate_percent_max', 'cache_hit_rate_percent_min', 'cache_hit_rate_percent_p95',
            'cache_size_mb_avg', 'cache_size_mb_max', 'cache_size_mb_min', 'cache_size_mb_p95',

            # Database Wait Events
            'wait_event_count_avg', 'wait_event_count_max', 'wait_event_count_min', 'wait_event_count_p95',
            'sql_event_count_avg', 'sql_event_count_max', 'sql_event_count_min', 'sql_event_count_p95',

            # Storage Metrics (tenant-level disk usage)
            'log_disk_total_gb_avg', 'log_disk_total_gb_max', 'log_disk_total_gb_min', 'log_disk_total_gb_p95',
            'server_required_size_gb_avg', 'server_required_size_gb_max', 'server_required_size_gb_min', 'server_required_size_gb_p95',
            'data_size_gb_avg', 'data_size_gb_max', 'data_size_gb_min', 'data_size_gb_p95',
            'binlog_disk_used_gb_avg', 'binlog_disk_used_gb_max', 'binlog_disk_used_gb_min', 'binlog_disk_used_gb_p95',

            # Uptime
            'uptime_seconds_avg', 'uptime_seconds_max', 'uptime_seconds_min', 'uptime_seconds_p95',

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
