# FramePack Cache Configuration Guide

This guide explains how to configure customized cache usage and localized storage in FramePack.

## Overview

FramePack now supports a flexible cache configuration system that allows you to:
- Customize cache directories and storage locations
- Configure TeaCache parameters for optimal performance
- Support localized storage based on your region and language
- Automatically manage cache cleanup and size limits

## Configuration Files

FramePack looks for configuration files in the following order:
1. `framepack_cache_config.json` in the current directory
2. `~/.config/FramePack/cache_config.json` (Linux/macOS)
3. `%APPDATA%/FramePack/cache_config.json` (Windows)

## Configuration Options

### Cache Settings

```json
{
  "cache": {
    "hf_cache_dir": "./hf_download",           // HuggingFace models cache directory
    "model_cache_dir": "./models",             // Local models cache directory  
    "temp_cache_dir": "./temp",                // Temporary files directory
    "max_cache_size_gb": 50,                   // Maximum total cache size in GB
    "auto_cleanup": true,                      // Enable automatic cleanup
    "cleanup_threshold_gb": 40                 // Cleanup when cache exceeds this size
  }
}
```

### TeaCache Settings

TeaCache is a performance optimization that caches computation results to speed up video generation:

```json
{
  "teacache": {
    "enabled": true,                           // Enable/disable TeaCache
    "rel_l1_thresh": 0.15,                    // Similarity threshold (0.1-0.3)
    "rescale_coefficients": [                  // Polynomial coefficients for rescaling
      732.3226126,
      -401.131952,
      67.5869174,
      -3.149878,
      0.0961237896
    ]
  }
}
```

**TeaCache Threshold Guidelines:**
- `0.10`: Maximum speed (1.6x faster), may reduce quality
- `0.15`: Balanced speed/quality (2.1x faster) - **Recommended**
- `0.20`: Conservative setting (1.3x faster), best quality

### Localization Settings

```json
{
  "localization": {
    "language": "auto",                        // Language code (auto, en, zh, ja, ko)
    "region": "auto",                          // Region code (auto, US, CN, JP, KR)
    "use_system_locale": true                  // Use system locale if auto
  }
}
```

### Storage Settings

```json
{
  "storage": {
    "prefer_local_storage": true,              // Prefer local over network storage
    "local_storage_priority": ["ssd", "hdd", "network"], // Storage priority order
    "backup_locations": [                      // Additional backup cache locations
      "/data/framepack_cache",
      "~/Documents/FramePack/cache"
    ]
  }
}
```

## Using the Configuration Utility

FramePack includes a command-line utility to help configure cache settings:

### Show Current Configuration
```bash
python configure_cache.py --show
```

### Set Custom Cache Directory
```bash
python configure_cache.py --set-cache-dir /path/to/cache
```

### Configure TeaCache Threshold
```bash
python configure_cache.py --set-teacache-threshold 0.12
```

### Set Maximum Cache Size
```bash
python configure_cache.py --set-max-cache-size 100
```

### Load Locale-Specific Templates
```bash
# Load Chinese configuration
python configure_cache.py --load-template zh_CN

# Load Japanese configuration  
python configure_cache.py --load-template ja_JP

# Load English (US) configuration
python configure_cache.py --load-template en_US
```

### Create Cache Directories
```bash
python configure_cache.py --create-dirs
```

## Pre-configured Templates

FramePack includes several pre-configured templates for different regions:

### English (US) - `configs/cache_config_en_US.json`
- Standard cache size (50GB)
- Balanced TeaCache settings
- Local storage preference

### Chinese (CN) - `configs/cache_config_zh_CN.json`  
- Larger cache size (100GB)
- Optimized TeaCache for quality
- Multiple backup locations

### Japanese (JP) - `configs/cache_config_ja_JP.json`
- Medium cache size (75GB)
- Conservative TeaCache settings
- Local storage priority

## Platform-Specific Default Locations

### Windows
- Cache: `%LOCALAPPDATA%\FramePack`
- Config: `%APPDATA%\FramePack`

### macOS
- Cache: `~/Library/Caches/FramePack`
- Config: `~/.config/FramePack`

### Linux
- Cache: `~/.cache/FramePack`
- Config: `~/.config/FramePack`

## Advanced Configuration

### Environment Variables
You can override certain settings using environment variables:
- `FRAMEPACK_CACHE_DIR`: Override HuggingFace cache directory
- `FRAMEPACK_CONFIG_PATH`: Path to custom configuration file

### Custom Rescale Coefficients
The TeaCache rescale coefficients can be fine-tuned for your specific hardware:

```python
from diffusers_helper.cache_config import get_cache_config

config = get_cache_config()
# Set custom coefficients for your GPU
config.set('teacache.rescale_coefficients', [800.0, -450.0, 70.0, -3.5, 0.1])
config.save()
```

## Migration from Previous Versions

If you're upgrading from a previous version of FramePack:

1. Your existing `./hf_download` directory will continue to work
2. Run `python configure_cache.py --show` to see current settings
3. Optionally configure new settings for better performance
4. Use `python configure_cache.py --create-dirs` to create additional cache directories

## Troubleshooting

### Cache Directory Issues
- Ensure the cache directory is writable
- Check available disk space
- Verify directory permissions

### TeaCache Performance
- Lower threshold = faster but potentially lower quality
- Higher threshold = slower but better quality
- Monitor your specific use case and adjust accordingly

### Configuration Validation
The system automatically validates configuration values:
- Cache sizes must be positive numbers
- TeaCache threshold must be between 0 and 1
- Cleanup threshold must be less than max cache size

## API Reference

### Python API
```python
from diffusers_helper.cache_config import CacheConfig, get_cache_config

# Get global configuration
config = get_cache_config()

# Get specific values
hf_cache_dir = config.get_hf_cache_dir()
teacache_config = config.get_teacache_config()

# Set values
config.set('cache.max_cache_size_gb', 100)
config.save()

# Create custom configuration
custom_config = CacheConfig('/path/to/custom/config.json')
```

For more information, see the source code in `diffusers_helper/cache_config.py`.