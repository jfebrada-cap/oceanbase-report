"""
Authentication module for Alibaba Cloud
Reads credentials from ~/.aliyun/config.json
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional


class AliyunAuth:
    """Handle Alibaba Cloud authentication"""

    def __init__(self):
        self.config_path = Path.home() / '.aliyun' / 'config.json'
        self.credentials = None
        self._load_credentials()

    def _load_credentials(self) -> None:
        """Load credentials from Aliyun config file"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(
                    f"Aliyun config not found at {self.config_path}. "
                    "Please run 'aliyun configure' to set up credentials."
                )

            with open(self.config_path, 'r') as f:
                config = json.load(f)

            # Get the current profile (usually 'default')
            current_profile = config.get('current', 'default')
            profiles = config.get('profiles', [])

            # Find the current profile
            for profile in profiles:
                if profile.get('name') == current_profile:
                    self.credentials = {
                        'access_key_id': profile.get('access_key_id'),
                        'access_key_secret': profile.get('access_key_secret'),
                        'region': profile.get('region_id', 'cn-hangzhou')
                    }
                    break

            if not self.credentials:
                raise ValueError(f"Profile '{current_profile}' not found in config")

            print(f"✓ Loaded credentials for profile: {current_profile}")
            print(f"✓ Region: {self.credentials['region']}")

        except Exception as e:
            raise Exception(f"Failed to load Aliyun credentials: {str(e)}")

    def get_credentials(self) -> Dict[str, str]:
        """Return credentials dictionary"""
        if not self.credentials:
            raise Exception("Credentials not loaded")
        return self.credentials

    def get_access_key_id(self) -> str:
        """Get access key ID"""
        return self.credentials['access_key_id']

    def get_access_key_secret(self) -> str:
        """Get access key secret"""
        return self.credentials['access_key_secret']

    def get_region(self) -> str:
        """Get region"""
        return self.credentials['region']
