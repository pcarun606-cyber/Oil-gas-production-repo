"""
Databricks connection and database operations module
"""

import os
import logging
from typing import Optional, List, Dict, Any
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Databricks SQL connector, but allow graceful failure
try:
    from databricks.sql import connect
    from databricks.sql.client import Connection
    DATABRICKS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Databricks SQL connector not available: {str(e)}")
    DATABRICKS_AVAILABLE = False
    Connection = None


class DatabricksConnection:
    """
    Manages Databricks SQL connection and queries
    """
    
    def __init__(self):
        """Initialize Databricks connection using environment variables"""
        self.host = os.getenv('DATABRICKS_HOST')
        self.token = os.getenv('DATABRICKS_TOKEN')
        self.catalog = os.getenv('DATABRICKS_CATALOG')
        self.schema = os.getenv('DATABRICKS_SCHEMA')
        self.warehouse_id = os.getenv('DATABRICKS_WAREHOUSE_ID')
        self.connection: Optional[Connection] = None
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate that all required Databricks configuration is set"""
        missing_vars = []
        
        if not self.host or 'your-workspace' in str(self.host).lower():
            missing_vars.append('DATABRICKS_HOST')
        if not self.token or 'your_databricks' in str(self.token).lower():
            missing_vars.append('DATABRICKS_TOKEN')
        if not self.catalog or 'your_' in str(self.catalog).lower():
            missing_vars.append('DATABRICKS_CATALOG')
        if not self.schema or 'your_' in str(self.schema).lower():
            missing_vars.append('DATABRICKS_SCHEMA')
        if not self.warehouse_id:
            missing_vars.append('DATABRICKS_WAREHOUSE_ID')
        
        if missing_vars:
            logger.warning(
                f"Missing required Databricks configuration: {', '.join(missing_vars)}"
            )
    
    def connect(self) -> bool:
        """
        Establish connection to Databricks
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Check if Databricks SQL connector is available
            if not DATABRICKS_AVAILABLE:
                logger.warning("Databricks SQL connector not installed. Using sample data.")
                return False
            
            if not self.host or not self.token:
                logger.warning("Databricks credentials not configured. Using sample data.")
                return False
            
            if not self.warehouse_id:
                logger.warning("SQL warehouse ID not configured. Using sample data.")
                return False
            
            # Use SQL warehouse HTTP path
            http_path = f"/sql/1.0/warehouses/{self.warehouse_id}"
            
            self.connection = connect(
                server_hostname=self.host.replace("https://", "").rstrip("/"),
                http_path=http_path,
                access_token=self.token
            )
            logger.info("Successfully connected to Databricks")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Databricks: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Close Databricks connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Disconnected from Databricks")
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[tuple]:
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            List of tuples containing query results
        """
        if not self.connection:
            if not self.connect():
                raise ConnectionError("Failed to establish Databricks connection")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise
    
    def fetch_dataframe(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a query and return results as pandas DataFrame
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            pandas DataFrame with query results
        """
        if not self.connection:
            if not self.connect():
                raise ConnectionError("Failed to establish Databricks connection")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all results
            results = cursor.fetchall()
            cursor.close()
            
            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            logger.info(f"Fetched {len(df)} rows from Databricks")
            return df
        except Exception as e:
            logger.error(f"DataFrame fetch error: {str(e)}")
            raise
    
    def get_production_data(self, well_name: Optional[str] = None) -> pd.DataFrame:
        """Fetch production data from Databricks"""
        query = f"SELECT * FROM {self.catalog}.{self.schema}.production_data"
        if well_name:
            query += f" WHERE well_name = '{well_name}'"
        query += " ORDER BY measurement_date DESC"
        return self.fetch_dataframe(query)
    
    def get_well_forecast_data(self) -> pd.DataFrame:
        """Fetch well forecast data from Databricks"""
        query = f"SELECT * FROM {self.catalog}.{self.schema}.well_forecasts ORDER BY forecast_date DESC"
        return self.fetch_dataframe(query)
    
    def get_monthly_summary(self) -> pd.DataFrame:
        """Fetch monthly production summary from Databricks"""
        query = f"SELECT * FROM {self.catalog}.{self.schema}.monthly_summary ORDER BY month_date DESC"
        return self.fetch_dataframe(query)
    
    def get_annual_production_data(self) -> pd.DataFrame:
        """Fetch GOLD TABLE 1 - Annual production"""
        query = f"SELECT * FROM {self.catalog}.{self.schema}.gold_well_annual_production ORDER BY year DESC, wellbore_name"
        return self.fetch_dataframe(query)
    
    def get_production_efficiency_data(self) -> pd.DataFrame:
        """Fetch GOLD TABLE 2 - Production efficiency"""
        query = f"SELECT * FROM {self.catalog}.{self.schema}.gold_well_production_efficiency ORDER BY year DESC, wellbore_name"
        return self.fetch_dataframe(query)
    
    def get_water_cut_analysis_data(self) -> pd.DataFrame:
        """Fetch GOLD TABLE 3 - Water cut analysis"""
        query = f"SELECT * FROM {self.catalog}.{self.schema}.gold_well_water_cut_analysis ORDER BY year DESC, wellbore_name"
        return self.fetch_dataframe(query)
    
    def get_optimization_candidates_data(self) -> pd.DataFrame:
        """Fetch GOLD TABLE 4 - Optimization candidates"""
        query = f"SELECT * FROM {self.catalog}.{self.schema}.gold_well_optimization_candidates ORDER BY year DESC, wellbore_name"
        return self.fetch_dataframe(query)


def get_databricks_connection() -> Optional[DatabricksConnection]:
    """
    Factory function to create and return a Databricks connection
    
    Returns:
        DatabricksConnection instance or None if creation fails
    """
    try:
        return DatabricksConnection()
    except Exception as e:
        logger.error(f"Failed to create Databricks connection: {str(e)}")
        return None
