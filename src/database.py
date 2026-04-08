"""
Databricks connection and database operations module
"""

import os
import logging
from typing import Optional, List, Dict, Any
import pandas as pd

# Configure logging with detailed format to show API calls
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Enable debug logging for Databricks SQL connector
logging.getLogger('databricks.sql').setLevel(logging.DEBUG)
logging.getLogger('databricks.sql.auth').setLevel(logging.DEBUG)
logging.getLogger('databricks.sql.session').setLevel(logging.DEBUG)
logging.getLogger('databricks.sql.client').setLevel(logging.DEBUG)
logging.getLogger('databricks.sql.backend').setLevel(logging.DEBUG)

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
        
        logger.info("🔍 Validating Databricks configuration...")
        logger.info(f"  HOST: {'✅' if self.host and 'your-workspace' not in str(self.host).lower() else '❌'} {self.host[:30] if self.host else 'NOT SET'}...")
        logger.info(f"  TOKEN: {'✅' if self.token and 'your_databricks' not in str(self.token).lower() else '❌'} {self.token[:10] if self.token else 'NOT SET'}...")
        logger.info(f"  CATALOG: {'✅' if self.catalog and 'your_' not in str(self.catalog).lower() else '❌'} {self.catalog if self.catalog else 'NOT SET'}")
        logger.info(f"  SCHEMA: {'✅' if self.schema and 'your_' not in str(self.schema).lower() else '❌'} {self.schema if self.schema else 'NOT SET'}")
        logger.info(f"  WAREHOUSE_ID: {'✅' if self.warehouse_id else '❌'} {self.warehouse_id if self.warehouse_id else 'NOT SET'}")
        
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
        else:
            logger.info("✅ All Databricks configuration variables are set")
    
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
            
            logger.info("=" * 80)
            logger.info("🔌 DATABRICKS CONNECTION ATTEMPT")
            logger.info("=" * 80)
            logger.info(f"Attempting Databricks connection with host: {self.host}")
            
            if not self.host or not self.token:
                logger.warning(f"Missing credentials - Host: {bool(self.host)}, Token: {bool(self.token)}")
                logger.warning("Databricks credentials not configured. Using sample data.")
                return False
            
            if not self.warehouse_id:
                logger.warning("SQL warehouse ID not configured. Using sample data.")
                return False
            
            # Use SQL warehouse HTTP path
            http_path = f"/sql/1.0/warehouses/{self.warehouse_id}"
            server_hostname = self.host.replace("https://", "").rstrip("/")
            
            logger.info("🔧 Connection Configuration:")
            logger.info(f"  Server Hostname: {server_hostname}")
            logger.info(f"  HTTP Path: {http_path}")
            logger.info(f"  Catalog: {self.catalog}")
            logger.info(f"  Schema: {self.schema}")
            logger.info(f"  Warehouse ID: {self.warehouse_id}")
            logger.info(f"  Token: {self.token[:10]}...{self.token[-5:]}")
            
            logger.info("📡 Initiating HTTP connection to Databricks...")
            self.connection = connect(
                server_hostname=server_hostname,
                http_path=http_path,
                access_token=self.token
            )
            logger.info("=" * 80)
            logger.info("✅ Successfully connected to Databricks SQL Warehouse")
            logger.info("=" * 80)
            return True
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ Failed to connect to Databricks: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error("=" * 80)
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
            logger.info("No cached connection, attempting to create one...")
            if not self.connect():
                raise ConnectionError("Failed to establish Databricks connection")
        
        try:
            # Log the full query with parameters
            logger.info("=" * 80)
            logger.info("🔄 SQL QUERY EXECUTION")
            logger.info("=" * 80)
            logger.info(f"CATALOG: {self.catalog}")
            logger.info(f"SCHEMA: {self.schema}")
            logger.info(f"SQL QUERY:\n{query}")
            if params:
                logger.info(f"PARAMETERS: {params}")
            logger.info("=" * 80)
            
            cursor = self.connection.cursor()
            logger.info("📤 Sending query to Databricks SQL Warehouse...")
            cursor.execute(query, params)
            logger.info("✅ Query executed successfully")
            
            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description]
            logger.info(f"📊 Result columns: {columns}")
            
            # Fetch all results
            logger.info("📥 Fetching results from Databricks...")
            results = cursor.fetchall()
            cursor.close()
            
            # Create DataFrame
            df = pd.DataFrame(results, columns=columns)
            logger.info(f"✅ Successfully fetched {len(df)} raw rows from Databricks")
            logger.info(f"DataFrame shape: {df.shape}")
            
            # Data quality check BEFORE filtering
            if len(df) > 0:
                null_counts = df.isnull().sum()
                null_summary = {col: int(count) for col, count in null_counts.items() if count > 0}
                if null_summary:
                    logger.warning(f"⚠️ NULL values detected in raw data:")
                    for col, count in null_summary.items():
                        logger.warning(f"   {col}: {count}/{len(df)} rows are NULL ({count/len(df)*100:.1f}%)")
            
            # Filter out rows where key columns are NULL or contain string 'nan'
            # First, replace string 'nan' with actual NaN for all columns
            df = df.replace({'nan': None})
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: None if isinstance(x, str) and x.lower() == 'nan' else x)
            
            # Identify key columns (usually the first text column and numeric columns)
            key_columns = []
            for col in columns:
                if col.lower() in ['wellbore_name', 'well_name', 'well_id', 'name', 'id', 'wellbore']:
                    key_columns.append(col)
            
            if key_columns:
                logger.info(f"🔍 Filtering out NULL/missing rows using key columns: {key_columns}")
                df_before = len(df)
                df = df.dropna(subset=key_columns)
                df_after = len(df)
                logger.info(f"📊 Filtered from {df_before} rows to {df_after} valid rows (removed {df_before - df_after} NULL/missing rows)")
            else:
                # If no key columns found, drop rows where all values are NULL
                logger.info(f"🔍 Filtering out completely empty rows")
                df_before = len(df)
                df = df.dropna(how='all')
                df_after = len(df)
                logger.info(f"📊 Filtered from {df_before} rows to {df_after} valid rows (removed {df_before - df_after} empty rows)")
            
            # Show first valid row if available
            if len(df) > 0:
                logger.info(f"✅ First valid row sample: {df.head(1).to_dict('records')}")
            else:
                logger.warning(f"⚠️ No valid rows found after filtering!")
                logger.warning(f"Original data had {df_before} rows but all were NULL/empty")
            
            logger.info("=" * 80)
            return df
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ DataFrame fetch error: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error("=" * 80)
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
        table_name = f"{self.catalog}.{self.schema}.gold_well_annual_production"
        logger.info(f"📊 Fetching GOLD TABLE 1: gold_well_annual_production")
        query = f"SELECT * FROM {table_name} ORDER BY year DESC, wellbore_name"
        return self.fetch_dataframe(query)
    
    def get_production_efficiency_data(self) -> pd.DataFrame:
        """Fetch GOLD TABLE 2 - Production efficiency"""
        table_name = f"{self.catalog}.{self.schema}.gold_well_production_efficiency"
        logger.info(f"⚡ Fetching GOLD TABLE 2: gold_well_production_efficiency")
        query = f"SELECT * FROM {table_name} ORDER BY year DESC, wellbore_name"
        return self.fetch_dataframe(query)
    
    def get_water_cut_analysis_data(self) -> pd.DataFrame:
        """Fetch GOLD TABLE 3 - Water cut analysis"""
        table_name = f"{self.catalog}.{self.schema}.gold_well_water_cut_analysis"
        logger.info(f"💧 Fetching GOLD TABLE 3: gold_well_water_cut_analysis")
        query = f"SELECT * FROM {table_name} ORDER BY year DESC, wellbore_name"
        return self.fetch_dataframe(query)
    
    def get_optimization_candidates_data(self) -> pd.DataFrame:
        """Fetch GOLD TABLE 4 - Optimization candidates"""
        table_name = f"{self.catalog}.{self.schema}.gold_well_optimization_candidates"
        logger.info(f"🎯 Fetching GOLD TABLE 4: gold_well_optimization_candidates")
        query = f"SELECT * FROM {table_name} ORDER BY year DESC, wellbore_name"
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
