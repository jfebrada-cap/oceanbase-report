"""
OceanBase Client for extracting instance and tenant information
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from alibabacloud_oceanbasepro20190901.client import Client as OceanBaseClient
from alibabacloud_oceanbasepro20190901 import models as oceanbase_models
from alibabacloud_tea_openapi import models as api_models
from alibabacloud_cms20190101.client import Client as CmsClient
from alibabacloud_cms20190101 import models as cms_models


class OceanBaseReporter:
    """Client for extracting OceanBase metrics and information"""

    def __init__(self, access_key_id: str, access_key_secret: str, region: str):
        """
        Initialize OceanBase Reporter

        Args:
            access_key_id: Alibaba Cloud access key ID
            access_key_secret: Alibaba Cloud access key secret
            region: Alibaba Cloud region (e.g., 'cn-hangzhou')
        """
        self.region = region
        self.oceanbase_client = self._create_oceanbase_client(
            access_key_id, access_key_secret, region
        )
        self.cms_client = self._create_cms_client(
            access_key_id, access_key_secret, region
        )

    def _create_oceanbase_client(
        self, access_key_id: str, access_key_secret: str, region: str
    ) -> OceanBaseClient:
        """Create OceanBase SDK client"""
        config = api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region_id=region
        )
        config.endpoint = f'oceanbasepro.{region}.aliyuncs.com'
        return OceanBaseClient(config)

    def _create_cms_client(
        self, access_key_id: str, access_key_secret: str, region: str
    ) -> CmsClient:
        """Create Cloud Monitor Service (CMS) client for metrics"""
        config = api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region_id=region
        )
        config.endpoint = f'metrics.{region}.aliyuncs.com'
        return CmsClient(config)

    def list_all_instances(self) -> List[Dict]:
        """
        List all OceanBase instances in the region with pagination

        Returns:
            List of instance information dictionaries
        """
        try:
            # Get all instances with explicit page_size
            request = oceanbase_models.DescribeInstancesRequest(page_size=100)
            response = self.oceanbase_client.describe_instances(request)

            instances = []
            if response.body.instances:
                for instance in response.body.instances:
                    instances.append({
                        'instance_id': instance.instance_id,
                        'instance_name': instance.instance_name,
                        'status': instance.state,
                        'series': instance.series,
                        'cpu': instance.cpu,
                        'memory': instance.mem,
                        'disk_size': instance.disk_size,
                        'used_disk_size': instance.used_disk_size if instance.used_disk_size else 0,
                        'disk_type': instance.disk_type,
                        'create_time': instance.create_time,
                        'available_zones': instance.available_zones,
                        'vpc_id': instance.vpc_id
                    })
            return instances
        except Exception as e:
            print(f"Error listing instances: {str(e)}")
            return []

    def get_instance_details(self, instance_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific OceanBase instance
        Includes capacity allocation metrics (allocated vs total resources)

        Args:
            instance_id: OceanBase instance ID

        Returns:
            Dictionary with instance details including capacity allocation
        """
        try:
            request = oceanbase_models.DescribeInstanceRequest(
                instance_id=instance_id
            )
            response = self.oceanbase_client.describe_instance(request)
            instance = response.body.instance

            # Extract CPU resource allocation
            total_cpu = 0
            used_cpu = 0  # This is ALLOCATED CPU to tenants
            unit_cpu = 0
            original_total_cpu = 0
            if instance.resource and instance.resource.cpu:
                cpu_obj = instance.resource.cpu
                total_cpu = getattr(cpu_obj, 'total_cpu', 0)
                used_cpu = getattr(cpu_obj, 'used_cpu', 0)
                unit_cpu = getattr(cpu_obj, 'unit_cpu', 0)
                original_total_cpu = getattr(cpu_obj, 'original_total_cpu', total_cpu)

            # Extract Memory resource allocation
            total_memory = 0
            used_memory = 0  # This is ALLOCATED MEMORY to tenants
            unit_memory = 0
            original_total_memory = 0
            if instance.resource and instance.resource.memory:
                memory_obj = instance.resource.memory
                total_memory = getattr(memory_obj, 'total_memory', 0)
                used_memory = getattr(memory_obj, 'used_memory', 0)
                unit_memory = getattr(memory_obj, 'unit_memory', 0)
                original_total_memory = getattr(memory_obj, 'original_total_memory', total_memory)

            # Extract Data Disk resource allocation
            total_disk = 0
            used_disk = 0  # This is ALLOCATED disk space
            data_used_size = 0  # This is ACTUAL data usage
            max_disk_used_pct = 0
            unit_disk_size = 0
            original_total_disk = 0
            if instance.resource and instance.resource.disk_size:
                disk_obj = instance.resource.disk_size
                total_disk = getattr(disk_obj, 'total_disk_size', 0)
                used_disk = getattr(disk_obj, 'used_disk_size', 0)
                data_used_size = getattr(disk_obj, 'data_used_size', 0)
                max_disk_used_pct = getattr(disk_obj, 'max_disk_used_percent', 0)
                unit_disk_size = getattr(disk_obj, 'unit_disk_size', 0)
                original_total_disk = getattr(disk_obj, 'original_total_disk_size', total_disk)

            # Extract Log Disk resource allocation
            total_log_disk = 0
            log_assigned = 0  # This is ALLOCATED log disk
            max_log_assigned_pct = 0
            unit_log_disk = 0
            original_total_log_disk = 0
            if instance.resource and hasattr(instance.resource, 'log_disk_size') and instance.resource.log_disk_size:
                log_disk_obj = instance.resource.log_disk_size
                total_log_disk = getattr(log_disk_obj, 'total_disk_size',
                                        getattr(log_disk_obj, 'total_log_disk', 0))
                log_assigned = getattr(log_disk_obj, 'log_assigned_size',
                                      getattr(log_disk_obj, 'used_log_disk_size', 0))
                max_log_assigned_pct = getattr(log_disk_obj, 'max_log_assigned_percent', 0)
                unit_log_disk = getattr(log_disk_obj, 'unit_disk_size',
                                       getattr(log_disk_obj, 'unit_log_disk', 0))
                original_total_log_disk = getattr(log_disk_obj, 'original_total_disk_size', total_log_disk)

            # Calculate capacity allocation percentages (handle None values)
            cpu_allocation_pct = (used_cpu / total_cpu * 100) if (total_cpu and total_cpu > 0) else 0
            memory_allocation_pct = (used_memory / total_memory * 100) if (total_memory and total_memory > 0) else 0
            storage_allocation_pct = (used_disk / total_disk * 100) if (total_disk and total_disk > 0) else 0
            log_disk_allocation_pct = (log_assigned / total_log_disk * 100) if (total_log_disk and total_log_disk > 0) else 0

            # Calculate available resources (handle None values)
            available_cpu = (total_cpu - used_cpu) if (total_cpu and used_cpu) else 0
            available_memory = (total_memory - used_memory) if (total_memory and used_memory) else 0
            available_storage = (total_disk - used_disk) if (total_disk and used_disk) else 0
            available_log_disk = (total_log_disk - log_assigned) if (total_log_disk and log_assigned) else 0

            return {
                'instance_id': instance.instance_id,
                'instance_name': instance.instance_name,
                'status': instance.status,
                'series': instance.series,

                # CPU Capacity Allocation
                'total_cpu': total_cpu if total_cpu is not None else 0,
                'allocated_cpu': used_cpu if used_cpu is not None else 0,  # NEW: CPU allocated to tenants
                'available_cpu': available_cpu if available_cpu is not None else 0,  # NEW: CPU still available

                # Memory Capacity Allocation
                'total_memory': total_memory if total_memory is not None else 0,
                'allocated_memory': used_memory if used_memory is not None else 0,  # NEW: Memory allocated to tenants
                'available_memory': available_memory if available_memory is not None else 0,  # NEW: Memory still available

                # Storage (Data Disk) Capacity Allocation
                'total_storage': total_disk if total_disk is not None else 0,
                'allocated_storage': used_disk if used_disk is not None else 0,  # NEW: Storage allocated
                'actual_data_usage': data_used_size if data_used_size is not None else 0,  # NEW: Actual data usage
                'available_storage': available_storage if available_storage is not None else 0,  # NEW: Storage still available

                # Log Disk Capacity Allocation
                'total_log_disk': total_log_disk if total_log_disk is not None else 0,
                'allocated_log_disk': log_assigned if log_assigned is not None else 0,  # NEW: Log disk allocated
                'available_log_disk': available_log_disk if available_log_disk is not None else 0,  # NEW: Log disk still available

                # Instance metadata
                'disk_type': instance.disk_type,
                'create_time': instance.create_time
            }
        except Exception as e:
            print(f"Error getting instance details for {instance_id}: {str(e)}")
            return None

    def list_tenants(self, instance_id: str) -> List[Dict]:
        """
        List all tenants in an OceanBase instance with pagination

        Args:
            instance_id: OceanBase instance ID

        Returns:
            List of tenant information dictionaries
        """
        try:
            # Get all tenants with explicit page_size
            request = oceanbase_models.DescribeTenantsRequest(
                instance_id=instance_id,
                page_size=100
            )
            response = self.oceanbase_client.describe_tenants(request)

            tenants = []
            if response.body.tenants:
                for tenant in response.body.tenants:
                    tenants.append({
                        'tenant_id': tenant.tenant_id,
                        'tenant_name': tenant.tenant_name,
                        # Note: cpu, memory, unit_num removed - now fetched via get_tenant_details()
                        # which provides better-named fields: tenant_allocated_cpu, tenant_allocated_memory, tenant_unit_num
                        'create_time': tenant.create_time,
                        'tenant_mode': tenant.tenant_mode if tenant.tenant_mode else 'N/A'
                    })
            return tenants
        except Exception as e:
            print(f"Error listing tenants for instance {instance_id}: {str(e)}")
            return []

    def get_tenant_details(self, instance_id: str, tenant_id: str) -> Optional[Dict]:
        """
        Get detailed tenant information including resource allocation

        Args:
            instance_id: OceanBase instance ID
            tenant_id: Tenant ID

        Returns:
            Dictionary with detailed tenant information including allocated resources
        """
        try:
            request = oceanbase_models.DescribeTenantRequest(
                instance_id=instance_id,
                tenant_id=tenant_id
            )
            response = self.oceanbase_client.describe_tenant(request)

            if response.body and response.body.tenant:
                tenant = response.body.tenant

                # Extract basic tenant info
                tenant_info = {
                    'tenant_id': tenant.tenant_id,
                    'tenant_name': tenant.tenant_name,
                    'tenant_mode': tenant.tenant_mode if tenant.tenant_mode else 'N/A',
                    'create_time': tenant.create_time,
                }

                # Extract max_connections only (no other connection details)
                if hasattr(tenant, 'tenant_connections') and tenant.tenant_connections:
                    connections = tenant.tenant_connections
                    if connections and len(connections) > 0:
                        primary_conn = connections[0]
                        tenant_info['max_connections'] = getattr(primary_conn, 'max_connection_num', 0)
                else:
                    tenant_info['max_connections'] = 0

                # Extract resource allocation from TenantResource
                if hasattr(tenant, 'tenant_resource') and tenant.tenant_resource:
                    resource = tenant.tenant_resource

                    # CPU allocation (total only, no per-unit)
                    if hasattr(resource, 'cpu') and resource.cpu:
                        cpu_obj = resource.cpu
                        tenant_info['tenant_allocated_cpu'] = getattr(cpu_obj, 'total_cpu', 0)

                    # Memory allocation (total only, no per-unit)
                    if hasattr(resource, 'memory') and resource.memory:
                        memory_obj = resource.memory
                        tenant_info['tenant_allocated_memory'] = getattr(memory_obj, 'total_memory', 0)

                    # Get unit_num for calculations
                    unit_num = getattr(resource, 'unit_num', 0)

                    # Disk allocation and usage
                    # NOTE: SDK only provides 'used_disk_size' in disk_size object
                    # Total allocated disk must be calculated from unit_num (not available in API)
                    if hasattr(resource, 'disk_size') and resource.disk_size:
                        disk_obj = resource.disk_size
                        # The SDK doesn't provide total_disk_size, only used_disk_size
                        # We'll use used_disk_size for both fields since total isn't available
                        tenant_info['tenant_allocated_disk'] = 0  # Not available in API
                        tenant_info['tenant_actual_disk_usage'] = getattr(disk_obj, 'used_disk_size', 0)

                    # Log disk allocation and usage
                    # NOTE: SDK only provides 'total_log_disk' and 'unit_log_disk'
                    # Used log disk size is not available in the DescribeTenant API
                    if hasattr(resource, 'log_disk_size') and resource.log_disk_size:
                        log_disk_obj = resource.log_disk_size
                        tenant_info['tenant_allocated_log_disk'] = getattr(log_disk_obj, 'total_log_disk', 0)
                        tenant_info['tenant_log_disk_usage'] = 0  # Not available in API - would need CloudMonitor metrics

                else:
                    # Fallback to basic tenant info if TenantResource not available
                    tenant_info['tenant_allocated_cpu'] = tenant.cpu if hasattr(tenant, 'cpu') else 0
                    tenant_info['tenant_allocated_memory'] = tenant.mem if hasattr(tenant, 'mem') else 0
                    tenant_info['tenant_allocated_disk'] = 0
                    tenant_info['tenant_actual_disk_usage'] = 0
                    tenant_info['tenant_allocated_log_disk'] = 0
                    tenant_info['tenant_log_disk_usage'] = 0

                return tenant_info

            return None

        except Exception as e:
            print(f"Error getting tenant details for {tenant_id}: {str(e)}")
            return None

    def get_metrics(
        self,
        instance_id: str,
        metric_name: str,
        period: int = 300,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get CloudMonitor metrics for an OceanBase instance

        Args:
            instance_id: OceanBase instance ID
            metric_name: Metric name (e.g., 'cpu_usage', 'memory_percent')
            period: Data aggregation period in seconds (default: 300)
            start_time: Start time in ISO format
            end_time: End time in ISO format

        Returns:
            Dictionary with metric data including avg, min, max, P95
        """
        try:
            if not end_time:
                end_time = datetime.now()
            else:
                end_time = datetime.fromisoformat(end_time)

            if not start_time:
                start_time = end_time - timedelta(days=1)  # Last 24 hours for faster retrieval
            else:
                start_time = datetime.fromisoformat(start_time)

            request = cms_models.DescribeMetricListRequest(
                namespace='acs_oceanbase',
                metric_name=metric_name,
                dimensions=f'[{{"instanceId":"{instance_id}"}}]',
                start_time=str(int(start_time.timestamp() * 1000)),
                end_time=str(int(end_time.timestamp() * 1000)),
                period=str(3600)  # 1 hour aggregation for faster response
            )

            response = self.cms_client.describe_metric_list(request)

            if response.body.datapoints:
                import json
                datapoints = json.loads(response.body.datapoints)

                # Filter datapoints for this specific instance
                # CloudMonitor returns data for all instances, need to filter by obClusterId
                if datapoints:
                    instance_datapoints = [
                        dp for dp in datapoints
                        if dp.get('obClusterId') == instance_id or dp.get('instanceId') == instance_id
                    ]

                    if instance_datapoints:
                        # CloudMonitor uses 'Average' for some metrics and 'Value' for others
                        values = []
                        for dp in instance_datapoints:
                            if dp.get('Average') is not None:
                                values.append(dp.get('Average'))
                            elif dp.get('Value') is not None:
                                values.append(dp.get('Value'))

                        if values:
                            # Calculate P95
                            sorted_values = sorted(values)
                            p95_index = int(len(sorted_values) * 0.95)
                            p95_value = sorted_values[p95_index] if p95_index < len(sorted_values) else sorted_values[-1]

                            # Calculate raw values first
                            raw_avg = sum(values) / len(values)
                            raw_min = min(values)
                            raw_max = max(values)
                            raw_p95 = p95_value

                            # Debug: Log if any values exceed 100%
                            if raw_max > 100.0 or raw_avg > 100.0 or raw_p95 > 100.0:
                                print(f"    ⚠ WARNING: {metric_name} exceeded 100% - Raw values: avg={raw_avg:.2f}, min={raw_min:.2f}, max={raw_max:.2f}, p95={raw_p95:.2f}")
                                print(f"      Sample values from API: {values[:5]}")

                            # Cap all values at 100% for utilization metrics (percentages should not exceed 100%)
                            avg_value = min(raw_avg, 100.0)
                            min_value = min(raw_min, 100.0)
                            max_value = min(raw_max, 100.0)
                            p95_value = min(raw_p95, 100.0)

                            return {
                                'metric_name': metric_name,
                                'avg': round(avg_value, 2),
                                'min': round(min_value, 2),
                                'max': round(max_value, 2),
                                'p95': round(p95_value, 2),
                                'datapoint_count': len(instance_datapoints),
                                # Include raw values for debugging
                                'raw_avg': round(raw_avg, 2),
                                'raw_max': round(raw_max, 2)
                            }

            return {
                'metric_name': metric_name,
                'avg': 0,
                'min': 0,
                'max': 0,
                'p95': 0,
                'datapoint_count': 0
            }

        except Exception as e:
            print(f"  Warning: Metrics unavailable for {metric_name}: {str(e)[:80]}")
            return None

    def get_tenant_metrics(
        self,
        instance_id: str,
        tenant_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive OceanBase tenant metrics including CPU, memory, sessions, and I/O
        Uses CloudMonitor API for metrics collection

        Args:
            instance_id: OceanBase instance ID
            tenant_id: Tenant ID
            start_time: Start time in ISO format (optional)
            end_time: End time in ISO format (optional)

        Returns:
            Dictionary with comprehensive tenant metrics (for weekly/monthly: HIGHEST values)
        """
        metrics = {}

        # OPTIMIZED: Only fetch metrics that are commonly available
        # Tested and verified to return data for most tenants
        # UPDATED: Renamed metrics to follow consistent pattern (qps_*, tps_*, sessions_*, connection_*)
        tenant_metric_map = {
            # CPU metrics - AVAILABLE
            'cpu_usage_percent_tenant': 'cpu_usage_percent',
            # 'cpu_usage_avg_cores_tenant': 'cpu_usage_avg_cores',  # May not be available for all tenants

            # Memory metrics - AVAILABLE
            'memory_usage_tenant': 'memory_usage_percent',
            # MemStore metrics - TEST IF AVAILABLE
            # 'memstore_percent_tenant': 'memstore_percent',
            # 'memstore_used_tenant': 'memstore_used_mb',
            # 'memstore_total_tenant': 'memstore_total_mb',

            # Session/Connection metrics - AVAILABLE (renamed to sessions_* pattern)
            'active_sessions_tenant': 'sessions',
            'all_session': 'connection',

            # SQL Performance metrics - AVAILABLE (renamed to qps_* pattern)
            'sql_all_count': 'qps',
            'sql_all_rt': 'sql_avg_rt_ms',
            # SQL breakdown by type - AVAILABLE (verified via testing)
            'sql_select_count': 'sql_select_qps',
            'sql_insert_count': 'sql_insert_qps',
            'sql_update_count': 'sql_update_qps',
            'sql_delete_count': 'sql_delete_qps',
            'sql_replace_count': 'sql_replace_qps',

            # Transaction metrics - AVAILABLE (renamed to tps_* pattern)
            'transaction_count': 'tps',
            # 'transaction_rt': 'transaction_avg_rt_us',  # Often returns NaN
            'transaction_partition_count': 'transaction_partition_tps',
            'trans_commit_log_count': 'trans_commit_log_count',
            'trans_commit_log_sync_rt': 'trans_commit_log_sync_rt_ms',

            # Transaction log size - AVAILABLE
            'clog_trans_log_total_size': 'clog_trans_log_size_mb',

            # I/O metrics - PARTIALLY AVAILABLE
            # 'io_count': 'io_ops_per_sec',  # NOT AVAILABLE (400 error)
            # 'io_rt': 'io_avg_rt_us',  # NOT AVAILABLE (400 error)
            # 'io_size': 'io_throughput_bytes',  # NOT AVAILABLE (400 error)
            'io_read_count': 'io_read_ops_per_sec',  # AVAILABLE
            'io_write_count': 'io_write_ops_per_sec',  # AVAILABLE
            'io_read_rt': 'io_read_rt_us',  # AVAILABLE
            'io_write_rt': 'io_write_rt_us',  # AVAILABLE
            # 'io_read_size': 'io_read_bytes_per_sec',  # NOT AVAILABLE (400 error)
            # 'io_write_size': 'io_write_bytes_per_sec',  # NOT AVAILABLE (400 error)

            # Cache metrics - TEST IF AVAILABLE
            # 'cache_hit': 'cache_hit_rate_percent',
            # 'cache_size': 'cache_size_mb',

            # Queue metrics - AVAILABLE
            'request_queue_time': 'request_queue_time_us',

            # Database wait events - TEST IF AVAILABLE
            # 'ob_waiteven_count': 'wait_event_count',
            # 'ob_sql_event': 'sql_event_count',

            # Storage metrics - TESTING
            # Note: These metrics will be fetched and merged into tenant data
            'ob_tenant_log_disk_total_bytes': 'log_disk_total_bytes',
            'ob_tenant_log_disk_used_bytes': 'log_disk_used_bytes',
            'ob_tenant_data_disk_total_bytes': 'data_disk_total_bytes',  # TESTING - for Allocated_Disk
            # 'ob_tenant_server_required_size': 'server_required_size_gb',
            # 'ob_tenant_server_data_size': 'data_size_gb',
            # 'ob_tenant_binlog_disk_used': 'binlog_disk_used_gb',

            # Network metrics - AVAILABLE (verified via testing)
            'net_recv': 'network_recv_bytes_per_sec',
            'net_send': 'network_sent_bytes_per_sec',

            # Uptime - TEST IF AVAILABLE
            # 'uptime': 'uptime_seconds',
        }

        for metric_name, output_field in tenant_metric_map.items():
            try:
                if not end_time:
                    end_dt = datetime.now()
                else:
                    end_dt = datetime.fromisoformat(end_time)

                if not start_time:
                    start_dt = end_dt - timedelta(hours=24)
                else:
                    start_dt = datetime.fromisoformat(start_time)

                request = cms_models.DescribeMetricListRequest(
                    namespace='acs_oceanbase',
                    metric_name=metric_name,
                    dimensions=f'[{{"obClusterId":"{instance_id}","obTenantId":"{tenant_id}"}}]',
                    start_time=str(int(start_dt.timestamp() * 1000)),
                    end_time=str(int(end_dt.timestamp() * 1000)),
                    period=str(3600)
                )

                response = self.cms_client.describe_metric_list(request)

                if response.body.datapoints:
                    import json
                    datapoints = json.loads(response.body.datapoints)

                    if datapoints:
                        # Extract values from datapoints
                        values = []
                        for dp in datapoints:
                            if dp.get('Average') is not None:
                                values.append(dp.get('Average'))
                            elif dp.get('Value') is not None:
                                values.append(dp.get('Value'))
                            elif dp.get('Maximum') is not None:
                                values.append(dp.get('Maximum'))
                            elif dp.get('Max') is not None:
                                values.append(dp.get('Max'))

                        if values:
                            # Determine metric type for proper capping
                            # Only cap percentage metrics at 100%
                            # Absolute metrics (GB, MB, bytes, counts, RT, QPS, TPS) should NOT be capped
                            is_percentage_metric = ('percent' in output_field or
                                                   ('usage' in metric_name and 'percent' in metric_name))

                            # Calculate raw values including P95
                            raw_avg = sum(values) / len(values)
                            raw_max = max(values)
                            raw_min = min(values)

                            # Calculate P95
                            sorted_values = sorted(values)
                            p95_index = int(len(sorted_values) * 0.95)
                            raw_p95 = sorted_values[p95_index] if p95_index < len(sorted_values) else sorted_values[-1]

                            if is_percentage_metric:
                                # Debug: Log if percentage metrics exceed 100%
                                if raw_max > 100.0 or raw_avg > 100.0 or raw_p95 > 100.0:
                                    print(f"    ⚠ WARNING: Tenant metric {metric_name} ({output_field}) exceeded 100% - Raw: avg={raw_avg:.2f}, max={raw_max:.2f}, p95={raw_p95:.2f}")
                                    print(f"      Sample values from API: {values[:3]}")

                                avg_val = min(raw_avg, 100.0)
                                max_val = min(raw_max, 100.0)
                                min_val = min(raw_min, 100.0)
                                p95_val = min(raw_p95, 100.0)
                            else:
                                avg_val = raw_avg
                                max_val = raw_max
                                min_val = raw_min
                                p95_val = raw_p95

                            metrics[f'{output_field}_avg'] = round(avg_val, 2)
                            metrics[f'{output_field}_max'] = round(max_val, 2)
                            metrics[f'{output_field}_min'] = round(min_val, 2)
                            metrics[f'{output_field}_p95'] = round(p95_val, 2)
            except Exception as e:
                # Skip metrics that are not available
                pass

        return metrics

    def fetch_tenants_parallel(
        self,
        instance_id: str,
        instance_name: str,
        tenants: List[Dict],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_workers: int = 5
    ) -> List[Dict]:
        """
        Fetch tenant metrics in parallel using threading

        Args:
            instance_id: OceanBase instance ID
            instance_name: Instance name for labeling
            tenants: List of tenant dictionaries
            start_time: Start time in ISO format
            end_time: End time in ISO format
            max_workers: Maximum number of concurrent threads (default: 5)

        Returns:
            List of tenant dictionaries with metrics
        """
        def fetch_single_tenant(tenant: Dict) -> Dict:
            """Fetch metrics for a single tenant"""
            try:
                # Add instance context
                tenant['instance_id'] = instance_id
                tenant['instance_name'] = instance_name

                # Get detailed tenant resource allocation (from DescribeTenant API)
                tenant_details = self.get_tenant_details(
                    instance_id,
                    tenant['tenant_id']
                )
                if tenant_details:
                    tenant.update(tenant_details)

                # Get comprehensive tenant metrics (from CloudMonitor API)
                tenant_metrics = self.get_tenant_metrics(
                    instance_id,
                    tenant['tenant_id'],
                    start_time=start_time,
                    end_time=end_time
                )
                if tenant_metrics:
                    tenant.update(tenant_metrics)

                # Post-process: Convert disk metrics from bytes to GB
                # CloudMonitor returns bytes, we need to populate GB fields

                # Convert log disk used bytes to GB and populate log_disk_usage
                if 'log_disk_used_bytes_avg' in tenant:
                    tenant['tenant_log_disk_usage'] = round(tenant['log_disk_used_bytes_avg'] / (1024**3), 2)

                # Convert data disk total bytes to GB and populate Allocated_Disk
                if 'data_disk_total_bytes_avg' in tenant:
                    tenant['tenant_allocated_disk'] = round(tenant['data_disk_total_bytes_avg'] / (1024**3), 2)

                return tenant
            except Exception as e:
                print(f"      ⚠ Error fetching metrics for tenant {tenant.get('tenant_id', 'unknown')}: {str(e)}")
                return tenant

        if not tenants:
            return []

        print(f"    Fetching metrics for {len(tenants)} tenants (parallel mode, {max_workers} workers)...")

        tenants_with_metrics = []
        completed_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_tenant = {
                executor.submit(fetch_single_tenant, tenant): tenant
                for tenant in tenants
            }

            # Process as they complete
            for future in as_completed(future_to_tenant):
                tenant = future_to_tenant[future]
                try:
                    result = future.result()
                    tenants_with_metrics.append(result)
                    completed_count += 1

                    # Progress update every 10 tenants
                    if completed_count % 10 == 0:
                        print(f"      Progress: {completed_count}/{len(tenants)} tenants processed...")
                except Exception as e:
                    print(f"      ⚠ Failed to process tenant {tenant.get('tenant_id', 'unknown')}: {str(e)}")
                    # Still add the tenant even if metrics failed
                    tenants_with_metrics.append(tenant)
                    completed_count += 1

        print(f"    ✓ Completed fetching metrics for {len(tenants_with_metrics)} tenant(s)")
        return tenants_with_metrics

    def get_utilization_metrics(
        self,
        instance_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        period_desc: str = "last 24 hours"
    ) -> Dict:
        """
        Get ALL instance-level CloudMonitor metrics with avg/min/max/P95

        Args:
            instance_id: OceanBase instance ID
            start_time: Start time in ISO format (optional)
            end_time: End time in ISO format (optional)
            period_desc: Description of the period (for logging)

        Returns:
            Dictionary with ALL available instance metrics (for weekly/monthly: HIGHEST values)
        """
        print(f"  Fetching ALL instance metrics ({period_desc})...")

        metrics = {}

        # OPTIMIZED: Only fetch metrics that are commonly available for OceanBase
        # Metrics that returned errors in testing are commented out to speed up extraction
        instance_metric_map = {
            # CPU metrics - AVAILABLE
            'cpu_usage': 'cpu',
            'cpu_percent': 'cpu_percent',  # AVAILABLE (verified via testing)

            # Memory metrics - AVAILABLE
            'memory_percent': 'memory',
            'memstore_percent': 'memstore_percent',

            # QPS/TPS metrics - AVAILABLE
            'qps': 'qps',
            'tps': 'tps',
            'qps_rt': 'qps_rt_ms',
            'tps_rt': 'tps_rt_ms',

            # Active sessions - AVAILABLE (verified via testing)
            'active_session': 'active_sessions',

            # Data size - NOT AVAILABLE
            # 'data_size': 'data_size_gb',  # Returns 400 error

            # Disk metrics - NOT AVAILABLE via CloudMonitor
            # Use DescribeInstance API instead (already fetched)
            # 'disk_usage': 'disk_usage_percent',  # Returns 400 error
            # 'disk_used': 'disk_used_gb',  # Returns 400 error
            # 'disk_total': 'disk_total_gb',  # Returns 400 error

            # Network metrics - NOT AVAILABLE
            # 'network_in': 'network_in_bytes_per_sec',  # Returns 400 error
            # 'network_out': 'network_out_bytes_per_sec',  # Returns 400 error

            # Connection metrics - NOT AVAILABLE
            # 'connection_count': 'connection_count',  # Returns 400 error
            # 'max_connections': 'max_connections_limit',  # Returns 400 error

            # Cache metrics - NOT AVAILABLE
            # 'cache_hit_rate': 'cache_hit_rate_percent',  # Returns 400 error

            # I/O metrics - PARTIALLY AVAILABLE
            'io_read_bytes': 'io_read_bytes_per_sec',
            'io_write_bytes': 'io_write_bytes_per_sec',
            # 'io_read_times': 'io_read_ops_per_sec',  # Returns 400 error
            # 'io_write_times': 'io_write_ops_per_sec',  # Returns 400 error
            # 'io_util': 'io_util_percent',  # Returns 400 error

            # SQL metrics - NOT AVAILABLE at instance level
            # Available at tenant level only
            # 'sql_count': 'sql_count_per_sec',  # Returns 400 error
            # 'sql_rt': 'sql_rt_ms',  # Returns 400 error
            # 'sql_select': 'sql_select_per_sec',  # Returns 400 error
            # 'sql_insert': 'sql_insert_per_sec',  # Returns 400 error
            # 'sql_update': 'sql_update_per_sec',  # Returns 400 error
            # 'sql_delete': 'sql_delete_per_sec',  # Returns 400 error
        }

        # Fetch only available metrics (much faster!)
        for metric_name, output_prefix in instance_metric_map.items():
            metric_data = self.get_metrics(instance_id, metric_name, start_time=start_time, end_time=end_time)
            if metric_data:
                metrics[f'{output_prefix}_avg'] = metric_data.get('avg', 0)
                metrics[f'{output_prefix}_min'] = metric_data.get('min', 0)
                metrics[f'{output_prefix}_max'] = metric_data.get('max', 0)
                metrics[f'{output_prefix}_p95'] = metric_data.get('p95', 0)

        # CPU metrics (legacy format for backward compatibility)
        cpu_metrics = self.get_metrics(instance_id, 'cpu_usage', start_time=start_time, end_time=end_time)
        if cpu_metrics:
            # Show if values were capped
            capped_indicator = ""
            if cpu_metrics.get('raw_max', 0) > 100.0:
                capped_indicator = f" (capped from {cpu_metrics.get('raw_max', 0)}%)"
            print(f"    CPU: avg={cpu_metrics.get('avg', 0)}%, min={cpu_metrics.get('min', 0)}%, max={cpu_metrics.get('max', 0)}%, P95={cpu_metrics.get('p95', 0)}%{capped_indicator}")

        # Memory metrics
        mem_metrics = self.get_metrics(instance_id, 'memory_percent', start_time=start_time, end_time=end_time)
        if mem_metrics:
            # Store actual avg/min/max/p95 values (already capped at 100%)
            metrics['memory_avg'] = mem_metrics.get('avg', 0)
            metrics['memory_min'] = mem_metrics.get('min', 0)
            metrics['memory_max'] = mem_metrics.get('max', 0)
            metrics['memory_p95'] = mem_metrics.get('p95', 0)

            # Show if values were capped
            capped_indicator = ""
            if mem_metrics.get('raw_max', 0) > 100.0:
                capped_indicator = f" (capped from {mem_metrics.get('raw_max', 0)}%)"
            print(f"    Memory: avg={mem_metrics.get('avg', 0)}%, min={mem_metrics.get('min', 0)}%, max={mem_metrics.get('max', 0)}%, P95={mem_metrics.get('p95', 0)}%{capped_indicator}")

        # Disk metrics - NOT AVAILABLE in CloudMonitor API for OceanBase
        # Disk utilization is calculated from instance details instead (used_storage / total_storage)
        # CloudMonitor does not provide disk usage metrics for OceanBase instances
        # Verified 2025-12-30: disk_usage, disk_percent, disk_usage_percent all return 400 errors

        return metrics

    def get_all_metrics(self, instance_id: str) -> Dict:
        """
        Get comprehensive metrics for an OceanBase instance
        Uses instance resource data and tenant metrics

        Args:
            instance_id: OceanBase instance ID

        Returns:
            Dictionary with all available metrics
        """
        # Get instance details which includes resource usage
        instance_details = self.get_instance_details(instance_id)

        # Get utilization metrics
        utilization_metrics = self.get_utilization_metrics(instance_id)

        # Try to get tenant metrics
        tenant_metrics = self.get_tenant_metrics(instance_id)

        metrics = {
            'instance_details': instance_details,
            'utilization_metrics': utilization_metrics,
            'tenant_metrics': tenant_metrics
        }

        return metrics
