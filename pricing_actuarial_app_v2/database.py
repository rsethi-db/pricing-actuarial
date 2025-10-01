"""
Database operations for the pricing cell automation app.
"""
import logging
from databricks import sql
from config import app_config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.config = app_config
    
    def get_sql_connection(self, timeout_seconds=300):
        """Get a SQL connection to Databricks."""
        try:
            conn = sql.connect(
                server_hostname=self.config.databricks_config.host,
                http_path=self.config.warehouse_http_path,
                credentials_provider=lambda: self.config.databricks_config.authenticate,
                _query_timeout_limit=timeout_seconds,
                _session_timeout_limit=timeout_seconds + 60,
            )
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
