"""
Database operations for the pricing cell automation app.
"""
import logging
import os
import ssl
from databricks import sql
from config import app_config

logger = logging.getLogger(__name__)

# For local development: disable SSL verification globally
# This is safe because it only affects local development, not production
if not os.environ.get('DATABRICKS_APP_ID'):
    logger.info("Local development detected: disabling SSL verification globally")
    ssl._create_default_https_context = ssl._create_unverified_context

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.config = app_config
    
    def get_sql_connection(self, timeout_seconds=300):
        """Get a SQL connection to Databricks."""
        try:
            import os
            import ssl
            
            # Check if we're in a Databricks Apps environment
            is_databricks_app = os.environ.get('DATABRICKS_APP_ID') is not None
            
            # SSL configuration for local development
            # For local dev, disable SSL verification to avoid cert issues
            if not is_databricks_app:
                # Disable SSL verification warnings for local development
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                logger.info("SSL verification disabled for local development")
            
            _tls_no_verify = not is_databricks_app
            
            logger.info(f"SSL verification: {'disabled' if _tls_no_verify else 'enabled'} (is_databricks_app={is_databricks_app})")
            
            if is_databricks_app:
                # In Databricks Apps, check for available authentication methods
                logger.info("Databricks Apps environment detected")
                
                # Check if there's a token in environment (Databricks Apps might set this)
                app_token = os.environ.get('DATABRICKS_TOKEN') or os.environ.get('DATABRICKS_ACCESS_TOKEN')
                
                if app_token:
                    logger.info("Using DATABRICKS_TOKEN from app environment")
                    conn = sql.connect(
                        server_hostname=self.config.databricks_config.host,
                        http_path=self.config.warehouse_http_path,
                        access_token=app_token,
                        _query_timeout_limit=timeout_seconds,
                        _session_timeout_limit=timeout_seconds + 60,
                    )
                else:
                    # Try to get token from Databricks SDK (for Databricks Apps)
                    logger.info("Attempting to get token from Databricks SDK")
                    try:
                        from databricks.sdk import WorkspaceClient
                        w = WorkspaceClient()
                        token = w.config.authenticate()
                        
                        logger.info("Successfully obtained token from Databricks SDK")
                        conn = sql.connect(
                            server_hostname=self.config.databricks_config.host,
                            http_path=self.config.warehouse_http_path,
                            access_token=token,
                            _query_timeout_limit=timeout_seconds,
                            _session_timeout_limit=timeout_seconds + 60,
                        )
                    except Exception as e:
                        logger.error(f"SDK authentication failed: {e}")
                        logger.error(f"Please add DATABRICKS_TOKEN environment variable to your app configuration")
                        logger.error("Environment variables available: " + str([k for k in os.environ.keys() if 'DATABRICKS' in k or 'TOKEN' in k]))
                        raise RuntimeError(f"Databricks Apps authentication failed. Please set DATABRICKS_TOKEN environment variable in your app configuration. Error: {e}")
            else:
                # For local development, use OAuth or token authentication
                token = os.environ.get('DATABRICKS_TOKEN')
                
                if token:
                    # Use personal access token if available
                    logger.info("Using DATABRICKS_TOKEN for authentication")
                    conn = sql.connect(
                        server_hostname=self.config.databricks_config.host,
                        http_path=self.config.warehouse_http_path,
                        access_token=token,
                        _tls_no_verify=_tls_no_verify,
                        _tls_verify_hostname=False if _tls_no_verify else True,
                        _query_timeout_limit=timeout_seconds,
                        _session_timeout_limit=timeout_seconds + 60,
                    )
                else:
                    # Try to use OAuth from Databricks CLI
                    logger.info("Attempting OAuth authentication from Databricks CLI")
                    try:
                        from databricks.sdk import WorkspaceClient
                        # Get OAuth token from WorkspaceClient
                        w = WorkspaceClient(host=f"https://{self.config.databricks_config.host}")
                        oauth_token = w.config.authenticate()
                        
                        conn = sql.connect(
                            server_hostname=self.config.databricks_config.host,
                            http_path=self.config.warehouse_http_path,
                            access_token=oauth_token,
                            _tls_no_verify=_tls_no_verify,
                            _tls_verify_hostname=False if _tls_no_verify else True,
                            _query_timeout_limit=timeout_seconds,
                            _session_timeout_limit=timeout_seconds + 60,
                        )
                    except Exception as oauth_error:
                        logger.error(f"OAuth authentication failed: {oauth_error}")
                        logger.error("Please set DATABRICKS_TOKEN environment variable or run: databricks auth login --host https://e2-demo-field-eng.cloud.databricks.com")
                        raise RuntimeError("No valid authentication available. Please set DATABRICKS_TOKEN or run 'databricks auth login'")
            
            logger.info("Successfully connected to Databricks SQL Warehouse")
            return conn
        except Exception as e:
            logger.exception("Failed to create SQL connection")
            raise
    
    def execute_query(self, query, timeout_seconds=300):
        """Execute a SQL query and return results."""
        conn = None
        cursor = None
        try:
            conn = self.get_sql_connection(timeout_seconds)
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Try to fetch results if it's a SELECT query
            try:
                result = cursor.fetchall_arrow().to_pandas()
                return result
            except:
                # If it's not a SELECT query, return None
                return None
        except Exception as e:
            logger.exception(f"Failed to execute query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_multiple_queries(self, queries, timeout_seconds=300):
        """Execute multiple SQL queries in sequence."""
        conn = None
        cursor = None
        try:
            conn = self.get_sql_connection(timeout_seconds)
            cursor = conn.cursor()
            
            results = []
            for query in queries:
                cursor.execute(query)
                try:
                    result = cursor.fetchall_arrow().to_pandas()
                    results.append(result)
                except:
                    results.append(None)
            
            return results
        except Exception as e:
            logger.exception(f"Failed to execute multiple queries: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Global database manager instance
db_manager = DatabaseManager()
