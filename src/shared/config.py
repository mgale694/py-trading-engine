"""Configuration management for services."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None, env: str = 'dev'):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file
            env: Environment name (dev, prod)
        """
        self.env = env
        self.config: Dict[str, Any] = {}
        
        if config_file:
            self.load_from_file(config_file)
        else:
            # Try to load default config based on environment
            default_config = Path(__file__).parent.parent.parent / 'config' / f'{env}.yaml'
            if default_config.exists():
                self.load_from_file(str(default_config))
        
        # Override with environment variables
        self.load_from_env()
    
    def load_from_file(self, file_path: str):
        """Load configuration from YAML file."""
        try:
            with open(file_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Configuration loaded from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
    
    def load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'RABBITMQ_HOST': ('rabbitmq', 'host'),
            'RABBITMQ_PORT': ('rabbitmq', 'port'),
            'KDB_HOST': ('kdb', 'host'),
            'KDB_PORT': ('kdb', 'port'),
            'DB_PATH': ('database', 'path'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self.set_nested(config_path, value)
    
    def set_nested(self, path: tuple, value: Any):
        """Set a nested configuration value."""
        current = self.config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        current = self.config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def get_rabbitmq_config(self) -> Dict[str, Any]:
        """Get RabbitMQ configuration."""
        return {
            'host': self.get('rabbitmq.host', 'localhost'),
            'port': self.get('rabbitmq.port', 5672),
            'username': self.get('rabbitmq.username'),
            'password': self.get('rabbitmq.password'),
        }
    
    def get_kdb_config(self) -> Dict[str, Any]:
        """Get KDB+ configuration."""
        return {
            'host': self.get('kdb.host', 'localhost'),
            'port': self.get('kdb.port', 8080),
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            'transactional': self.get('database.transactional', 'src/database/transactional/trading_engine.db'),
            'analytics': self.get('database.analytics', 'src/database/analytics/analytics.db'),
            'utilities': self.get('database.utilities', 'src/database/utilities/utilities.db'),
        }
    
    def get_dev_config(self) -> Dict[str, Any]:
        """Get development configuration."""
        return {
            'initialize_mock_data': self.get('dev.initialize_mock_data', False),
            'mock_data': self.get('dev.mock_data', {}),
            'enable_simulated_traders': self.get('dev.enable_simulated_traders', False),
            'simulated_traders': self.get('dev.simulated_traders', {}),
        }
    
    def should_initialize_mock_data(self) -> bool:
        """Check if mock data should be initialized."""
        return self.env == 'dev' and self.get('dev.initialize_mock_data', False)
    
    def should_enable_simulated_traders(self) -> bool:
        """Check if simulated traders should be enabled."""
        return self.env == 'dev' and self.get('dev.enable_simulated_traders', False)
