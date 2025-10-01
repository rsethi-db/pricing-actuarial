"""
Configuration management for the pricing cell automation app.
"""
import os
import logging
import yaml
from databricks.sdk.core import Config

# ==============================
# Logging Setup
# ==============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppConfig:
    """Application configuration manager."""
    
    def __init__(self, config_file="app.yaml"):
        """Initialize configuration from YAML file."""
        self.config_file = config_file
        self._load_config()
        self._validate_config()
        self._setup_databricks_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_file) as f:
                self.config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _validate_config(self):
        """Validate configuration parameters."""
        required_keys = ["databricks"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        databricks_config = self.config["databricks"]
        required_databricks_keys = ["host", "warehouse_http_path", "ai_endpoint"]
        for key in required_databricks_keys:
            if key not in databricks_config:
                raise ValueError(f"Missing required databricks configuration key: {key}")
        
        # Validate host format
        db_host = databricks_config["host"]
        if db_host.startswith("https://") or db_host.startswith("http://"):
            raise ValueError("DATABRICKS_HOST should NOT include 'https://' or 'http://'. Use only the hostname.")
        
        logger.info(f"Using Databricks host: {db_host}")
        logger.info(f"Using warehouse HTTP path: {databricks_config['warehouse_http_path']}")
    
    def _setup_databricks_config(self):
        """Setup Databricks SDK configuration."""
        try:
            self.db_cfg = Config()
            self.db_cfg.host = self.config["databricks"]["host"]
        except Exception as e:
            logger.warning(f"Could not initialize Databricks SDK config: {e}")
            # Create a minimal config object for basic functionality
            self.db_cfg = type('MockConfig', (), {
                'host': self.config["databricks"]["host"],
                'token': os.getenv('DATABRICKS_TOKEN', '')
            })()
    
    @property
    def databricks_host(self):
        """Get Databricks host."""
        return self.config["databricks"]["host"]
    
    @property
    def warehouse_http_path(self):
        """Get warehouse HTTP path."""
        return self.config["databricks"]["warehouse_http_path"]
    
    @property
    def ai_endpoint(self):
        """Get AI endpoint name."""
        return self.config["databricks"]["ai_endpoint"]
    
    @property
    def databricks_config(self):
        """Get Databricks SDK configuration."""
        return self.db_cfg

# Global configuration instance
app_config = AppConfig()
