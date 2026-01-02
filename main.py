#!/usr/bin/env python3
"""
OceanBase Reporter - Capacity Assessment Tool
Extracts OceanBase instance and tenant information from Alibaba Cloud
and exports to CSV for capacity assessment.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from auth import AliyunAuth
from oceanbase_client import OceanBaseReporter
from csv_exporter import CSVExporter
from excel_exporter import ExcelExporter
from datetime import datetime, timedelta


def load_config(config_path: str = 'config/config.json') -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}, using defaults")
        return {}


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Extract OceanBase capacity assessment reports from Alibaba Cloud'
    )
    parser.add_argument(
        '--config',
        default='config/config.json',
        help='Path to configuration file (default: config/config.json)'
    )
    parser.add_argument(
        '--instances',
        nargs='+',
        help='Specific OceanBase instance IDs to process (optional)'
    )
    parser.add_argument(
        '--region',
        help='Alibaba Cloud region (overrides config)'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for CSV files (default: output)'
    )
    parser.add_argument(
        '--list-only',
        action='store_true',
        help='Only list instances without extracting metrics'
    )
    parser.add_argument(
        '--frequency',
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help='Report frequency: daily (24h), weekly (7 days HIGHEST), monthly (30 days HIGHEST) - default: daily'
    )
    parser.add_argument(
        '--lookback-days',
        type=int,
        default=None,
        help='Number of days to look back for metrics (overrides frequency default). Example: --lookback-days 7 for 7-day P95 in daily reports'
    )
    parser.add_argument(
        '--parallel-workers',
        type=int,
        default=20,
        help='Number of parallel workers for tenant metric fetching (default: 20, recommended: 20-50 for faster extraction)'
    )
    parser.add_argument(
        '--instance-workers',
        type=int,
        default=10,
        help='Number of parallel workers for instance processing (default: 10, recommended: 5-15 depending on instance count)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("OceanBase Capacity Assessment Reporter")
    print("=" * 70)
    print()

    # Determine time period based on frequency
    end_time = datetime.now()

    # Check if custom lookback days is specified
    if args.lookback_days:
        start_time = end_time - timedelta(days=args.lookback_days)
        period_desc = f"Last {args.lookback_days} days (HIGHEST utilization including P95)"
    elif args.frequency == 'daily':
        start_time = end_time - timedelta(days=1)  # Last 24 hours
        period_desc = "Last 24 hours"
    elif args.frequency == 'weekly':
        start_time = end_time - timedelta(days=7)  # Last 7 days
        period_desc = "Last 7 days (HIGHEST utilization)"
    elif args.frequency == 'monthly':
        start_time = end_time - timedelta(days=30)  # Last 30 days
        period_desc = "Last 30 days (HIGHEST utilization)"

    print(f"Report Frequency: {args.frequency.upper()}")
    print(f"Time Period: {period_desc}")
    if args.lookback_days:
        print(f"Custom Lookback: {args.lookback_days} days")
    print(f"Instance Workers: {args.instance_workers} (parallel instance processing)")
    print(f"Tenant Workers: {args.parallel_workers} (parallel tenant metric fetching)")
    print()

    # Load configuration
    config = load_config(args.config)

    # Initialize authentication
    try:
        auth = AliyunAuth()
        credentials = auth.get_credentials()
        region = args.region or config.get('region', credentials['region'])
        print(f"Using region: {region}")
        print()
    except Exception as e:
        print(f"✗ Authentication failed: {str(e)}")
        return 1

    # Initialize OceanBase client
    try:
        reporter = OceanBaseReporter(
            access_key_id=credentials['access_key_id'],
            access_key_secret=credentials['access_key_secret'],
            region=region
        )
        print("✓ OceanBase client initialized")
    except Exception as e:
        print(f"✗ Failed to initialize OceanBase client: {str(e)}")
        return 1

    # Initialize CSV exporter
    exporter = CSVExporter(output_dir=args.output_dir)
    print(f"✓ CSV exporter initialized (output: {args.output_dir}/)")

    # Initialize Excel exporter
    excel_exporter = ExcelExporter(output_dir=args.output_dir)
    print(f"✓ Excel exporter initialized")
    print()

    # Determine which instances to process
    if args.instances:
        instance_ids = args.instances
        print(f"Processing specified instances: {', '.join(instance_ids)}")
    else:
        print("Discovering all OceanBase instances...")
        all_instances = reporter.list_all_instances()
        if not all_instances:
            print("✗ No OceanBase instances found")
            return 1

        instance_ids = [inst['instance_id'] for inst in all_instances]
        print(f"✓ Found {len(instance_ids)} instance(s)")

    print()

    if args.list_only:
        print("List-only mode: Exiting without extracting metrics")
        return 0

    # Process instances in parallel
    comprehensive_data = []
    tenants_data = []

    def process_single_instance(instance_id: str, idx: int) -> tuple:
        """
        Process a single OceanBase instance and its tenants

        Returns:
            Tuple of (instance_data, tenants_list, instance_name, success)
        """
        try:
            # Get instance details
            instance_details = reporter.get_instance_details(instance_id)
            if not instance_details:
                return None, [], instance_id, False

            instance_name = instance_details.get('instance_name', 'N/A')

            # Prepare instance data
            instance_data = instance_details.copy()

            # Calculate disk utilization percentage
            if instance_details.get('total_storage') and instance_details.get('total_storage') > 0:
                used_disk = instance_data.get('used_storage', 0)
                total_disk = instance_details.get('total_storage', 0)
                if total_disk > 0:
                    disk_util_pct = (used_disk / total_disk) * 100
                    instance_data['disk_utilization_pct'] = round(disk_util_pct, 2)

            # Get utilization metrics (avg/min/max/P95)
            utilization_metrics = reporter.get_utilization_metrics(
                instance_id,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                period_desc=period_desc
            )
            if utilization_metrics:
                instance_data.update(utilization_metrics)

            # Get tenants
            tenants = reporter.list_tenants(instance_id)

            # Fetch tenant metrics in parallel
            tenants_with_metrics = []
            if tenants:
                tenants_with_metrics = reporter.fetch_tenants_parallel(
                    instance_id=instance_id,
                    instance_name=instance_name,
                    tenants=tenants,
                    start_time=start_time.isoformat(),
                    end_time=end_time.isoformat(),
                    max_workers=args.parallel_workers
                )

            return instance_data, tenants_with_metrics, instance_name, True

        except Exception as e:
            print(f"\n⚠️  Error processing instance {instance_id}: {str(e)}")
            return None, [], instance_id, False

    # Use ThreadPoolExecutor for parallel instance processing
    from concurrent.futures import ThreadPoolExecutor, as_completed

    print(f"Processing {len(instance_ids)} instances with {args.instance_workers} parallel workers...")
    print()

    completed_count = 0
    with ThreadPoolExecutor(max_workers=args.instance_workers) as executor:
        # Submit all instance processing tasks
        future_to_instance = {
            executor.submit(process_single_instance, instance_id, idx): (instance_id, idx)
            for idx, instance_id in enumerate(instance_ids, 1)
        }

        # Process results as they complete
        for future in as_completed(future_to_instance):
            instance_id, idx = future_to_instance[future]
            try:
                instance_data, instance_tenants, instance_name, success = future.result()

                if success and instance_data:
                    comprehensive_data.append(instance_data)
                    tenants_data.extend(instance_tenants)
                    completed_count += 1

                    print(f"[{completed_count}/{len(instance_ids)}] ✓ Completed: {instance_name} ({instance_id}) - {len(instance_tenants)} tenant(s)")
                else:
                    print(f"[{idx}/{len(instance_ids)}] ✗ Failed: {instance_id}")

            except Exception as e:
                print(f"[{idx}/{len(instance_ids)}] ✗ Exception processing {instance_id}: {str(e)}")

    print()
    print(f"✓ Parallel processing completed: {completed_count}/{len(instance_ids)} instances successful")
    print()

    # Export comprehensive reports
    print("=" * 70)
    print("Generating Reports")
    print("=" * 70)
    print(f"Report Type: {args.frequency.upper()}")
    print()

    # Add frequency suffix to filenames
    freq_suffix = f"_{args.frequency}" if args.frequency != 'daily' else ""

    # Generate consolidated Excel report with multiple tabs
    print()
    print("Generating consolidated Excel report...")
    if comprehensive_data and tenants_data:
        # Create temporary CSV files for Excel generation
        import tempfile
        import os

        # Create temporary CSV files
        temp_dir = tempfile.mkdtemp()
        capacity_csv_path = os.path.join(temp_dir, f'oceanbase_capacity_assessment{freq_suffix}.csv')
        tenants_csv_path = os.path.join(temp_dir, f'oceanbase_tenants{freq_suffix}.csv')

        # NOTE: connection_utilization_pct calculation removed per user request (2026-01-02)
        # Previously calculated: (sessions_avg / max_connections) * 100
        # Column has been removed from the Tenants Report tab

        # Export to temporary CSV files
        import pandas as pd
        pd.DataFrame(comprehensive_data).to_csv(capacity_csv_path, index=False)
        pd.DataFrame(tenants_data).to_csv(tenants_csv_path, index=False)

        # Determine frequency label for Excel
        frequency_label = args.frequency.capitalize()

        # Generate Excel report from temporary CSV files
        excel_exporter.export_consolidated_report(
            capacity_csv_path=capacity_csv_path,
            tenants_csv_path=tenants_csv_path,
            report_frequency=frequency_label
        )

        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir)
    else:
        print("⚠ Skipping Excel report - CSV files not available")

    print()
    print("=" * 70)
    print(f"✓ Report generation completed successfully")
    print(f"  Report Type: {args.frequency.upper()}")
    print(f"  Time Period: {period_desc}")
    print(f"  Total instances processed: {len(comprehensive_data)}")
    print(f"  Total tenants found: {len(tenants_data)}")
    if comprehensive_data and tenants_data:
        print(f"  Excel report: {args.output_dir}/{datetime.now().strftime('%Y%m%d')}/{frequency_label.capitalize()}/")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
