#!/usr/bin/env python3
"""
FramePack Cache Configuration Utility

This utility helps configure cache settings for FramePack, including:
- Custom cache directories
- TeaCache parameters
- Localized storage options
"""

import argparse
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import diffusers_helper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diffusers_helper.cache_config import CacheConfig


def show_current_config():
    """Show current configuration."""
    config = CacheConfig()
    print("Current FramePack Cache Configuration:")
    print("=" * 40)
    print(f"HuggingFace Cache Directory: {config.get_hf_cache_dir()}")
    print(f"Model Cache Directory: {config.get('cache.model_cache_dir')}")
    print(f"Temp Cache Directory: {config.get('cache.temp_cache_dir')}")
    print(f"Max Cache Size: {config.get('cache.max_cache_size_gb')} GB")
    print(f"Auto Cleanup: {config.get('cache.auto_cleanup')}")
    print(f"Cleanup Threshold: {config.get('cache.cleanup_threshold_gb')} GB")
    print()
    print("TeaCache Settings:")
    print(f"  Enabled: {config.get('teacache.enabled')}")
    print(f"  Threshold: {config.get('teacache.rel_l1_thresh')}")
    print()
    print("Localization:")
    print(f"  Language: {config.get('localization.language')}")
    print(f"  Region: {config.get('localization.region')}")
    print(f"  Use System Locale: {config.get('localization.use_system_locale')}")
    

def set_cache_directory(directory):
    """Set the HuggingFace cache directory."""
    config = CacheConfig()
    abs_dir = os.path.abspath(directory)
    config.set('cache.hf_cache_dir', abs_dir)
    config.save()
    print(f"HuggingFace cache directory set to: {abs_dir}")


def set_teacache_threshold(threshold):
    """Set TeaCache threshold."""
    config = CacheConfig()
    try:
        threshold = float(threshold)
        if threshold <= 0 or threshold > 1:
            print("Error: Threshold must be between 0 and 1")
            return False
        config.set('teacache.rel_l1_thresh', threshold)
        config.save()
        print(f"TeaCache threshold set to: {threshold}")
        return True
    except ValueError:
        print("Error: Threshold must be a number")
        return False


def set_max_cache_size(size_gb):
    """Set maximum cache size."""
    config = CacheConfig()
    try:
        size_gb = float(size_gb)
        if size_gb <= 0:
            print("Error: Cache size must be positive")
            return False
        config.set('cache.max_cache_size_gb', size_gb)
        config.save()
        print(f"Maximum cache size set to: {size_gb} GB")
        return True
    except ValueError:
        print("Error: Cache size must be a number")
        return False


def load_config_template(locale):
    """Load a configuration template for the given locale."""
    config_dir = os.path.join(os.path.dirname(__file__), 'configs')
    template_file = f"cache_config_{locale}.json"
    template_path = os.path.join(config_dir, template_file)
    
    if not os.path.exists(template_path):
        print(f"Error: Template for locale '{locale}' not found")
        print("Available templates:")
        for f in os.listdir(config_dir):
            if f.startswith('cache_config_') and f.endswith('.json'):
                locale_name = f[13:-5]  # Remove 'cache_config_' and '.json'
                print(f"  {locale_name}")
        return False
    
    try:
        config = CacheConfig()
        with open(template_path, 'r', encoding='utf-8') as f:
            template_config = json.load(f)
        
        # Merge template with current config
        for key, value in template_config.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    config.set(f"{key}.{subkey}", subvalue)
            else:
                config.set(key, value)
        
        config.save()
        print(f"Configuration template '{locale}' loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading template: {e}")
        return False


def create_directories():
    """Create all configured cache directories."""
    config = CacheConfig()
    config.ensure_cache_directories()
    print("Cache directories created successfully")


def main():
    parser = argparse.ArgumentParser(
        description="FramePack Cache Configuration Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --show                           # Show current configuration
  %(prog)s --set-cache-dir ./my_cache       # Set custom cache directory
  %(prog)s --set-teacache-threshold 0.12    # Set TeaCache threshold
  %(prog)s --set-max-cache-size 100         # Set max cache size to 100GB
  %(prog)s --load-template zh_CN             # Load Chinese configuration
  %(prog)s --create-dirs                     # Create all cache directories
        """
    )
    
    parser.add_argument('--show', action='store_true',
                        help='Show current configuration')
    parser.add_argument('--set-cache-dir', metavar='DIR',
                        help='Set HuggingFace cache directory')
    parser.add_argument('--set-teacache-threshold', metavar='THRESHOLD',
                        help='Set TeaCache threshold (0.0-1.0)')
    parser.add_argument('--set-max-cache-size', metavar='SIZE_GB',
                        help='Set maximum cache size in GB')
    parser.add_argument('--load-template', metavar='LOCALE',
                        help='Load configuration template (e.g., en_US, zh_CN, ja_JP)')
    parser.add_argument('--create-dirs', action='store_true',
                        help='Create all configured cache directories')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    if args.show:
        show_current_config()
    
    if args.set_cache_dir:
        set_cache_directory(args.set_cache_dir)
    
    if args.set_teacache_threshold:
        set_teacache_threshold(args.set_teacache_threshold)
    
    if args.set_max_cache_size:
        set_max_cache_size(args.set_max_cache_size)
    
    if args.load_template:
        load_config_template(args.load_template)
    
    if args.create_dirs:
        create_directories()


if __name__ == '__main__':
    main()