# Cache Configuration System for FramePack
# Supports customizable cache usage and localized storage

import os
import json
import platform
from pathlib import Path
from typing import Dict, Optional, Union, Any


class CacheConfig:
    """Configuration manager for FramePack cache settings."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize cache configuration.
        
        Args:
            config_path: Path to custom configuration file. If None, uses default locations.
        """
        self.config_path = config_path
        self._config = self._load_config()
        
    def _get_default_cache_dir(self) -> str:
        """Get default cache directory based on platform and locale."""
        system = platform.system().lower()
        
        if system == 'windows':
            base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~/AppData/Local'))
        elif system == 'darwin':  # macOS
            base_dir = os.path.expanduser('~/Library/Caches')
        else:  # Linux and others
            base_dir = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
            
        return os.path.join(base_dir, 'FramePack')
    
    def _get_default_config_paths(self) -> list:
        """Get list of default configuration file paths to check."""
        paths = []
        
        # Current directory
        paths.append(os.path.join(os.getcwd(), 'framepack_cache_config.json'))
        
        # User config directory
        if platform.system().lower() == 'windows':
            config_dir = os.environ.get('APPDATA', os.path.expanduser('~/AppData/Roaming'))
        else:
            config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        paths.append(os.path.join(config_dir, 'FramePack', 'cache_config.json'))
        
        return paths
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'cache': {
                'hf_cache_dir': os.path.join(self._get_default_cache_dir(), 'hf_download'),
                'model_cache_dir': os.path.join(self._get_default_cache_dir(), 'models'),
                'temp_cache_dir': os.path.join(self._get_default_cache_dir(), 'temp'),
                'max_cache_size_gb': 50,
                'auto_cleanup': True,
                'cleanup_threshold_gb': 40
            },
            'teacache': {
                'enabled': True,
                'rel_l1_thresh': 0.15,
                'rescale_coefficients': [
                    7.33226126e+02, -4.01131952e+02, 6.75869174e+01, 
                    -3.14987800e+00, 9.61237896e-02
                ]
            },
            'localization': {
                'language': 'auto',  # auto, en, zh, ja, ko, etc.
                'region': 'auto',    # auto, US, CN, JP, KR, etc.
                'use_system_locale': True
            },
            'storage': {
                'prefer_local_storage': True,
                'local_storage_priority': ['ssd', 'hdd', 'network'],
                'backup_locations': []
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        config = self._get_default_config()
        
        # Check for custom config path from environment
        env_config_path = os.environ.get('FRAMEPACK_CONFIG_PATH')
        
        config_paths = []
        if env_config_path:
            config_paths.append(env_config_path)
        if self.config_path:
            config_paths.append(self.config_path)
        config_paths.extend(self._get_default_config_paths())
        
        for path in config_paths:
            if os.path.isfile(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                    # Validate user config
                    self._validate_config(user_config)
                    # Merge user config with defaults
                    config = self._merge_configs(config, user_config)
                    self.config_path = path
                    break
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Failed to load config from {path}: {e}")
                    continue
                except ValueError as e:
                    print(f"Warning: Invalid configuration in {path}: {e}")
                    continue
        
        # Apply environment variable overrides
        self._apply_env_overrides(config)
        
        return config
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration values."""
        if 'cache' in config:
            cache_config = config['cache']
            if 'max_cache_size_gb' in cache_config:
                max_size = cache_config['max_cache_size_gb']
                if not isinstance(max_size, (int, float)) or max_size <= 0:
                    raise ValueError("max_cache_size_gb must be a positive number")
            
            if 'cleanup_threshold_gb' in cache_config:
                threshold = cache_config['cleanup_threshold_gb']
                if not isinstance(threshold, (int, float)) or threshold <= 0:
                    raise ValueError("cleanup_threshold_gb must be a positive number")
                    
                max_size = cache_config.get('max_cache_size_gb', 50)
                if threshold >= max_size:
                    raise ValueError("cleanup_threshold_gb must be less than max_cache_size_gb")
        
        if 'teacache' in config:
            teacache_config = config['teacache']
            if 'rel_l1_thresh' in teacache_config:
                thresh = teacache_config['rel_l1_thresh']
                if not isinstance(thresh, (int, float)) or thresh <= 0 or thresh > 1:
                    raise ValueError("rel_l1_thresh must be between 0 and 1")
            
            if 'rescale_coefficients' in teacache_config:
                coeffs = teacache_config['rescale_coefficients']
                if not isinstance(coeffs, list) or len(coeffs) != 5:
                    raise ValueError("rescale_coefficients must be a list of 5 numbers")
                if not all(isinstance(c, (int, float)) for c in coeffs):
                    raise ValueError("All rescale_coefficients must be numbers")
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """Apply environment variable overrides."""
        # Override HF cache directory
        env_cache_dir = os.environ.get('FRAMEPACK_CACHE_DIR')
        if env_cache_dir:
            config['cache']['hf_cache_dir'] = env_cache_dir
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user configuration with defaults."""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'cache.hf_cache_dir')."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        save_path = path or self.config_path
        
        if not save_path:
            # Use default config directory
            config_dir = os.path.dirname(self._get_default_config_paths()[1])
            os.makedirs(config_dir, exist_ok=True)
            save_path = self._get_default_config_paths()[1]
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
            
        self.config_path = save_path
    
    def ensure_cache_directories(self) -> None:
        """Ensure all configured cache directories exist."""
        directories = [
            self.get('cache.hf_cache_dir'),
            self.get('cache.model_cache_dir'),
            self.get('cache.temp_cache_dir')
        ]
        
        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def get_hf_cache_dir(self) -> str:
        """Get HuggingFace cache directory."""
        return self.get('cache.hf_cache_dir')
    
    def get_teacache_config(self) -> Dict[str, Any]:
        """Get TeaCache configuration."""
        return {
            'enabled': self.get('teacache.enabled', True),
            'rel_l1_thresh': self.get('teacache.rel_l1_thresh', 0.15),
            'rescale_coefficients': self.get('teacache.rescale_coefficients')
        }
    
    def cleanup_cache(self) -> None:
        """Clean up cache if auto cleanup is enabled and threshold is exceeded."""
        if not self.get('cache.auto_cleanup', True):
            return
            
        max_size = self.get('cache.max_cache_size_gb', 50)
        threshold = self.get('cache.cleanup_threshold_gb', 40)
        
        # This would implement actual cleanup logic
        # For now, just a placeholder
        print(f"Cache cleanup check: max={max_size}GB, threshold={threshold}GB")


# Global configuration instance
_global_config = None

def get_cache_config() -> CacheConfig:
    """Get global cache configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = CacheConfig()
    return _global_config

def set_cache_config(config: CacheConfig) -> None:
    """Set global cache configuration instance."""
    global _global_config
    _global_config = config