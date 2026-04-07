import streamlit as st

# CRITICAL: set_page_config must be first streamlit command
st.set_page_config(
    page_title="Production Dashboard",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# NOW import everything else
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import logging
import os
import sys

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from database import get_databricks_connection
except Exception as e:
    logging.warning(f"Failed to import database: {e}")
    get_databricks_connection = None

# Apply minimal CSS
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #1a202c;
}
[data-testid="stSidebar"] {
    background-color: #0f1419;
}
* { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_db_connection():
    try:
        if get_databricks_connection is None:
            return None
        db = get_databricks_connection()
        if db and db.connect():
            return db
        return None
    except Exception as e:
        logging.error(f"DB Connection error: {e}")
        return None

# Sample data generator
def get_sample_annual_data():
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': np.random.uniform(8000, 18000),
                'gas': np.random.uniform(15000, 30000),
                'water': np.random.uniform(3000, 10000),
                'gas_injection': np.random.uniform(20000, 35000),
                'water_injection': np.random.uniform(5000, 10000),
            })
    return pd.DataFrame(data)

def get_sample_efficiency_data():
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil_per_injection': np.random.uniform(0.3, 0.8),
                'gas_per_injection': np.random.uniform(0.5, 1.5),
                'efficiency_flag': 'LOW' if np.random.random() > 0.6 else 'NORMAL'
            })
    return pd.DataFrame(data)

def get_sample_water_cut_data():
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            water_cut = np.random.uniform(10, 80)
            data.append({
                'wellbore_name': well,
                'year': year,
                'water_cut_pct': water_cut,
                'water_issue_flag': 'HIGH_WATER' if water_cut > 50 else 'NORMAL'
            })
    return pd.DataFrame(data)

def get_sample_optimization_data():
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            ratio = np.random.uniform(0.2, 0.8)
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil_to_fluid_ratio': ratio,
                'optimization_candidate': 'YES' if ratio < 0.4 else 'NO'
            })
    return pd.DataFrame(data)

# MAIN APP - Wrapped in try-except
try:
    st.title("Oil & Gas Production Dashboard")
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Field Overview"
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Production Dashboard")
        st.markdown("Oil & Gas Surveillance")
        st.markdown("---")
        
        pages = ["Field Overview", "Well Performance", "Production Planning", "Forecast & Reserves", "Actions & Alerts"]
        selected_page = st.selectbox("Select Page", pages)
        st.session_state.page = selected_page
    
    # Get database connection
    db = get_db_connection()
    
    # Show connection status
    if db is None:
        st.info("📊 Operating in sample data mode (Databricks unavailable)")
    
    # FIELD OVERVIEW
    if st.session_state.page == "Field Overview":
        st.subheader("Field Overview")
        st.write("Production overview for all wells")
        
        df_annual = get_sample_annual_data()
        latest_year = df_annual['year'].max()
        df_latest = df_annual[df_annual['year'] == latest_year]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Oil (Sm³)", f"{df_latest['oil'].sum():,.0f}")
        with col2:
            st.metric("Total Gas (Sm³)", f"{df_latest['gas'].sum():,.0f}")
        with col3:
            st.metric("Total Water (Sm³)", f"{df_latest['water'].sum():,.0f}")
        with col4:
            st.metric("Active Wells", len(df_latest))
        with col5:
            st.metric("Latest Year", int(latest_year))
        
        st.subheader(f"Annual Production - Year {latest_year}")
        st.dataframe(df_latest[['wellbore_name', 'oil', 'gas', 'water']], use_container_width=True)
    
    # WELL PERFORMANCE
    elif st.session_state.page == "Well Performance":
        st.subheader("Well Performance")
        st.write("Individual well analysis")
        
        df_annual = get_sample_annual_data()
        wells = sorted(df_annual['wellbore_name'].unique())
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_well = st.selectbox("Select Well", wells)
        with col2:
            st.button("Export")
        
        well_data = df_annual[df_annual['wellbore_name'] == selected_well]
        
        if not well_data.empty:
            latest = well_data[well_data['year'] == well_data['year'].max()].iloc[0]
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("Oil (Sm³)", f"{latest['oil']:,.0f}")
            with col2:
                st.metric("Gas (Sm³)", f"{latest['gas']:,.0f}")
            with col3:
                st.metric("Water (Sm³)", f"{latest['water']:,.0f}")
            with col4:
                st.metric("Gas Inj", f"{latest['gas_injection']:,.0f}")
            with col5:
                st.metric("Water Inj", f"{latest['water_injection']:,.0f}")
            with col6:
                st.metric("Year", int(latest['year']))
            
            st.subheader(f"{selected_well} - Production History")
            st.dataframe(well_data[['year', 'oil', 'gas', 'water']], use_container_width=True)
    
    # PRODUCTION PLANNING
    elif st.session_state.page == "Production Planning":
        st.subheader("Production Planning")
        st.write("Production forecast and planning")
        
        df_annual = get_sample_annual_data()
        df_optim = get_sample_optimization_data()
        
        col1, col2 = st.columns(2)
        with col1:
            schedule = st.selectbox("Plan Schedule", ["3 months", "6 months", "1 year"])
        with col2:
            scope = st.selectbox("Scope", ["Overall Field"] + sorted(df_annual['wellbore_name'].unique()))
        
        latest_year = df_annual['year'].max()
        df_latest = df_annual[df_annual['year'] == latest_year]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Oil", f"{df_latest['oil'].mean():,.0f}")
        with col2:
            st.metric("Avg Gas", f"{df_latest['gas'].mean():,.0f}")
        with col3:
            st.metric("Avg Water", f"{df_latest['water'].mean():,.0f}")
        with col4:
            st.metric("Wells", len(df_latest))
        
        st.subheader("Optimization Candidates")
        df_opt_latest = df_optim[df_optim['year'] == latest_year]
        opt_candidates = df_opt_latest[df_opt_latest['optimization_candidate'] == 'YES']
        
        if not opt_candidates.empty:
            st.info(f"Found {len(opt_candidates)} optimization candidates")
            st.dataframe(opt_candidates[['wellbore_name', 'oil_to_fluid_ratio']], use_container_width=True)
        else:
            st.info("No optimization candidates at this time")
    
    # FORECAST & RESERVES
    elif st.session_state.page == "Forecast & Reserves":
        st.subheader("Forecast & Reserves")
        st.write("Historical and forecast data")
        
        df_annual = get_sample_annual_data()
        
        total_oil = df_annual['oil'].sum()
        total_gas = df_annual['gas'].sum()
        total_water = df_annual['water'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cum. Oil Reserves", f"{total_oil:,.0f}")
        with col2:
            st.metric("Cum. Gas Reserves", f"{total_gas:,.0f}")
        with col3:
            st.metric("Cum. Water", f"{total_water:,.0f}")
        
        st.subheader("Historical Production")
        st.dataframe(df_annual, use_container_width=True)
    
    # ACTIONS & ALERTS
    elif st.session_state.page == "Actions & Alerts":
        st.subheader("Actions & Alerts")
        st.write("Critical alerts and actions")
        
        df_water = get_sample_water_cut_data()
        df_optim = get_sample_optimization_data()
        
        latest_year = df_water['year'].max()
        
        st.subheader("⚠️ Water Cut Alerts")
        high_water = df_water[(df_water['year'] == latest_year) & (df_water['water_issue_flag'] == 'HIGH_WATER')]
        
        if not high_water.empty:
            st.warning(f"Found {len(high_water)} wells with high water cut")
            st.dataframe(high_water[['wellbore_name', 'water_cut_pct']], use_container_width=True)
        else:
            st.success("No high water cut alerts")
        
        st.subheader("🎯 Optimization Candidates")
        df_opt = df_optim[df_optim['year'] == latest_year]
        opt_wells = df_opt[df_opt['optimization_candidate'] == 'YES']
        
        if not opt_wells.empty:
            st.info(f"Found {len(opt_wells)} optimization candidates")
            st.dataframe(opt_wells[['wellbore_name', 'oil_to_fluid_ratio']], use_container_width=True)
        else:
            st.info("No optimization candidates")

except Exception as e:
    st.error(f"❌ Application Error: {str(e)}")
    st.info("Please try refreshing the page or restarting the application")
    logging.error(f"App error: {e}", exc_info=True)
