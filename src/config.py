"""Configuration management for the batch pipeline"""

import json
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for extractors"""
    
    def __init__(self, config_file: str):
        """
        Initialize configuration from file
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_file}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def get_source(self, source_name: str) -> Dict[str, Any]:
        """Get configuration for a specific source"""
        sources = self.config.get("sources", {})
        if source_name not in sources:
            raise ValueError(f"Source not found: {source_name}")
        return sources[source_name]
    
    def list_sources(self) -> list:
        """List all configured sources"""
        return list(self.config.get("sources", {}).keys())
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_keys = ["sources"]
        for key in required_keys:
            if key not in self.config:
                logger.error(f"Missing required config key: {key}")
                return False
        
        sources = self.config.get("sources", {})
        if not sources:
            logger.error("No sources configured")
            return False
        
        return True
