"""Direct test of Databricks data fetching and filtering"""
import os
from dotenv import load_dotenv
from src.database import DatabricksConnection

load_dotenv()

# Create connection
db = DatabricksConnection()
if db.connect():
    print("✅ Connected to Databricks")
    
    # Fetch from table 2 (production efficiency)
    query = """
    SELECT * FROM 
    databricks_course_ws.oilgasproductionschema.gold_well_production_efficiency 
    ORDER BY year DESC, wellbore_name
    LIMIT 20
    """
    
    # This will include the filtering logic
    df = db.fetch_dataframe(query)
    
    print(f"\n📊 Data shape after filtering: {df.shape}")
    print(f"\n📋 Column names: {df.columns.tolist()}")
    print(f"\n📝 First 5 rows:")
    print(df.head())
    print(f"\n📝 Data types:")
    print(df.dtypes)
else:
    print("❌ Failed to connect to Databricks")
