"""Simple test of database connections and data availability"""
import os
import sys
os.chdir("c:\\Users\\Arun Prakash C\\Oil-gas-production-repo")
sys.path.insert(0, "src")

from dotenv import load_dotenv
load_dotenv()

from database import DatabricksConnection

print("Starting test...")
db = DatabricksConnection()
print(f"Connection object created")

if db.connect():
    print("✅ Connected!")
    
    # Get efficiency data
    df_eff = db.get_production_efficiency_data()
    print(f"✅ Efficiency data: {df_eff.shape[0]} rows, {df_eff.shape[1]} cols")
    
    if not df_eff.empty:
        # Get unique wells
        wells = df_eff['wellbore_name'].unique().tolist()
        print(f"✅ Wells found: {len(wells)}")
        print(f"   First well: {wells[0]}")
        
        # Get latest year
        latest_year = df_eff['year'].max()
        print(f"✅ Latest year: {latest_year}")
        
        # Show data
        df_year = df_eff[df_eff['year'] == latest_year]
        print(f"✅ Records in {latest_year}: {len(df_year)}")
        
        if len(df_year) > 0:
            first = df_year.iloc[0]
            print(f"   First record oil: {first['oil']}")
else:
    print("❌ Connection failed")
