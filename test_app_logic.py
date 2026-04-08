"""Test the fixed data display logic"""
import os
from dotenv import load_dotenv
from src.database import DatabricksConnection
import pandas as pd

load_dotenv()

# Create connection and fetch data
db = DatabricksConnection()
if not db.connect():
    print("❌ Failed to connect to Databricks")
    exit(1)

print("✅ Connected to Databricks\n")

# Load all data
df_annual = db.get_annual_production_data()
df_efficiency = db.get_production_efficiency_data()
df_water_cut = db.get_water_cut_analysis_data()
df_optimization = db.get_optimization_candidates_data()

print("=" * 80)
print("DATA AVAILABILITY CHECK")
print("=" * 80)
print(f"TABLE 1 (Annual Production):        {df_annual.shape[0]} rows")
print(f"TABLE 2 (Production Efficiency):    {df_efficiency.shape[0]} rows")
print(f"TABLE 3 (Water Cut Analysis):       {df_water_cut.shape[0]} rows")
print(f"TABLE 4 (Optimization Candidates):  {df_optimization.shape[0]} rows")

print("\n" + "=" * 80)
print("FIELD OVERVIEW PAGE TEST")
print("=" * 80)

# Simulate Field Overview page logic
df_for_metrics = df_annual if (df_annual is not None and not df_annual.empty) else \
                 (df_efficiency if (df_efficiency is not None and not df_efficiency.empty) else df_water_cut)

if df_for_metrics is not None and not df_for_metrics.empty:
    print(f"✅ Data source: TABLE {'1' if len(df_annual) > 0 else '2'}")
    latest_year = df_for_metrics['year'].max()
    df_latest = df_for_metrics[df_for_metrics['year'] == latest_year]
    print(f"✅ Latest year: {latest_year}")
    print(f"✅ Active wells: {len(df_latest)}")
    print(f"✅ Total oil: {df_latest['oil'].sum():,.0f} Sm³")
    print(f"✅ Total water: {df_latest.get('water', pd.Series()).sum():,.0f} Sm³")
    print(f"\nFirst 3 wells:")
    print(df_latest[['wellbore_name', 'year', 'oil']].head(3).to_string())
else:
    print("❌ No data available")

print("\n" + "=" * 80)
print("WELL PERFORMANCE PAGE TEST")
print("=" * 80)

# Simulate Well Performance page logic
df_for_wells = df_water_cut if (df_water_cut is not None and not df_water_cut.empty) else df_efficiency

if df_for_wells is not None and not df_for_wells.empty:
    wells = sorted(df_for_wells['wellbore_name'].unique().astype(str).tolist())
    print(f"✅ Available wells: {len(wells)}")
    print(f"Wells: {wells[:5]}")  # Show first 5
    
    # Mock selecting a well
    selected_well = wells[0] if wells else None
    if selected_well:
        well_data = df_efficiency[df_efficiency['wellbore_name'] == selected_well] if df_efficiency is not None and not df_efficiency.empty else pd.DataFrame()
        
        if not well_data.empty:
            print(f"\n✅ Selected well: {selected_well}")
            print(f"✅ Data points: {len(well_data)}")
            latest = well_data[well_data['year'] == well_data['year'].max()].iloc[0]
            print(f"   - Year: {latest['year']}")
            print(f"   - Oil: {latest['oil']:,.0f} Sm³")
            print(f"   - Gas: {latest['gas']:,.0f} Sm³")
            print(f"   - Efficiency Flag: {latest['efficiency_flag']}")
        else:
            print(f"❌ No data for well {selected_well}")
else:
    print("❌ No wells data available")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE - Dashboard should now display real data!")
print("=" * 80)
