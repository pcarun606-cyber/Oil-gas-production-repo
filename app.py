import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
import logging
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from database import get_databricks_connection
except Exception as e:
    print(f"Warning: Failed to import database module: {str(e)}")
    get_databricks_connection = None

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

# Set page configuration
st.set_page_config(
    page_title="Production Dashboard",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main page background */
    .main {
        background-color: #1a202c;
    }
    
    /* Full page background */
    [data-testid="stAppViewContainer"] {
        background-color: #1a202c;
    }
    
    [data-testid="stHeader"] {
        background-color: #1a202c;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0f1419;
    }
    
    /* ALL TEXT ELEMENTS - WHITE COLOR */
    * {
        color: #ffffff !important;
    }
    
    body, div, p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    .sidebar-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #ffffff !important;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #2d3748;
        padding: 20px;
        border-radius: 10px;
        color: #ffffff;
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #00d4ff;
    }
    
    .metric-unit {
        font-size: 14px;
        color: #ffffff;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff !important;
    }
    
    /* Container backgrounds */
    .stContainer {
        background-color: #1a202c;
    }
    
    /* Text content styling */
    .stMarkdown {
        color: #ffffff !important;
    }
    
    .stMarkdown p {
        color: #ffffff !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    /* DataFrames and tables */
    [data-testid="stDataFrame"] {
        background-color: #2d3748;
    }
    
    [data-testid="stDataFrame"] th {
        color: #ffffff !important;
        background-color: #2d3748 !important;
    }
    
    [data-testid="stDataFrame"] td {
        color: #ffffff !important;
        background-color: #1a202c !important;
    }
    
    /* Info, warning and success boxes */
    .stInfo, .stWarning, .stSuccess, .stError {
        background-color: rgba(45, 55, 72, 0.6) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    .stInfo p, .stWarning p, .stSuccess p, .stError p {
        color: #ffffff !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2d3748;
        color: #00d4ff;
        border: 1px solid #00d4ff;
    }
    
    .stButton > button:hover {
        background-color: #1a202c;
        border-color: #00d4ff;
        color: #00d4ff;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background-color: #0f1419 !important;
        color: #ffffff !important;
        border-color: #2d3748 !important;
    }
    
    /* Selectbox specific styling */
    .stSelectbox {
        background-color: transparent !important;
    }
    
    .stSelectbox > div {
        background-color: transparent !important;
    }
    
    .stSelectbox > div > div {
        background-color: #0f1419 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 6px !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: #0f1419 !important;
    }
    
    .stSelectbox input {
        background-color: #0f1419 !important;
        color: #ffffff !important;
        border: 1px solid #2d3748 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #0f1419 !important;
    }
    
    .stSelectbox [data-baseweb="popover"] {
        background-color: #0f1419 !important;
    }
    
    /* Text input specific */
    .stTextInput {
        background-color: #0f1419 !important;
    }
    
    .stTextInput > div {
        background-color: #0f1419 !important;
    }
    
    .stTextInput > div > div {
        background-color: #0f1419 !important;
    }
    
    .stTextInput input {
        background-color: #0f1419 !important;
        color: #ffffff !important;
    }
    
    /* Number input specific */
    .stNumberInput {
        background-color: #0f1419 !important;
    }
    
    .stNumberInput > div {
        background-color: #0f1419 !important;
    }
    
    .stNumberInput > div > div {
        background-color: #0f1419 !important;
    }
    
    .stNumberInput input {
        background-color: #0f1419 !important;
        color: #ffffff !important;
    }
    
    /* Dropdown menu items */
    [role="listbox"] {
        background-color: #0f1419 !important;
    }
    
    [role="option"] {
        background-color: #0f1419 !important;
        color: #ffffff !important;
    }
    
    [role="option"]:hover {
        background-color: #2d3748 !important;
        color: #ffffff !important;
    }
    
    /* Popup/Modal styling */
    .stPopupContent {
        background-color: #0f1419 !important;
    }
    
    /* Autocomplete dropdown */
    [data-baseweb="select"] {
        background-color: #0f1419 !important;
    }
    
    [data-baseweb="input"] {
        background-color: #0f1419 !important;
    }
    
    div[role="combobox"] {
        background-color: #0f1419 !important;
    }
    
    /* All input/select elements */
    input:not([type="checkbox"]):not([type="radio"]):not([type="submit"]):not([type="button"]) {
        background-color: #0f1419 !important;
        color: #ffffff !important;
    }
    
    select {
        background-color: #0f1419 !important;
        color: #ffffff !important;
    }
    
    textarea {
        background-color: #0f1419 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Databricks connection
@st.cache_resource
def get_db_connection():
    """Get cached Databricks connection - no Streamlit output during init"""
    try:
        if get_databricks_connection is None:
            return None
        db = get_databricks_connection()
        if db is None:
            return None
        if db.connect():
            return db
        else:
            return None
    except Exception as e:
        # Log but don't display during cache initialization
        import logging
        logging.error(f"Databricks connection error: {str(e)}")
        return None

@st.cache_data
def load_production_data_from_databricks(db):
    """Load production data from Databricks"""
    try:
        return db.get_production_data()
    except Exception as e:
        st.error(f"Error loading data from Databricks: {str(e)}")
        return None

@st.cache_data
def load_annual_production_data(db):
    """Load GOLD TABLE 1 - Annual production data from Databricks"""
    try:
        return db.get_annual_production_data()
    except Exception as e:
        st.error(f"Error loading annual production data: {str(e)}")
        return None

@st.cache_data
def load_production_efficiency_data(db):
    """Load GOLD TABLE 2 - Production efficiency data from Databricks"""
    try:
        return db.get_production_efficiency_data()
    except Exception as e:
        st.error(f"Error loading efficiency data: {str(e)}")
        return None

@st.cache_data
def load_water_cut_analysis_data(db):
    """Load GOLD TABLE 3 - Water cut analysis data from Databricks"""
    try:
        return db.get_water_cut_analysis_data()
    except Exception as e:
        st.error(f"Error loading water cut data: {str(e)}")
        return None

@st.cache_data
def load_optimization_candidates_data(db):
    """Load GOLD TABLE 4 - Optimization candidates data from Databricks"""
    try:
        return db.get_optimization_candidates_data()
    except Exception as e:
        st.error(f"Error loading optimization data: {str(e)}")
        return None

# =====================================================
# SAMPLE DATA GENERATION FOR GOLD TABLES (Fallback)
# =====================================================

def generate_sample_annual_production_data():
    """Generate sample GOLD TABLE 1 - Annual production data"""
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            oil = np.random.uniform(8000, 18000)
            gas = np.random.uniform(15000, 30000)
            water = np.random.uniform(3000, 10000)
            gas_inj = np.random.uniform(20000, 35000)
            water_inj = np.random.uniform(5000, 10000)
            
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': oil,
                'gas': gas,
                'water': water,
                'gas_injection': gas_inj,
                'water_injection': water_inj,
                'total_fluids': oil + water
            })
    
    return pd.DataFrame(data)

def generate_sample_production_efficiency_data():
    """Generate sample GOLD TABLE 2 - Production efficiency data"""
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            oil = np.random.uniform(8000, 18000)
            gas = np.random.uniform(15000, 30000)
            gas_inj = np.random.uniform(20000, 35000)
            water_inj = np.random.uniform(5000, 10000)
            total_inj = gas_inj + water_inj
            
            oil_per_inj = oil / total_inj
            gas_per_inj = gas / total_inj
            efficiency_flag = 'LOW' if oil_per_inj < 0.5 else 'NORMAL'
            
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': oil,
                'gas': gas,
                'gas_injection': gas_inj,
                'water_injection': water_inj,
                'oil_per_injection': oil_per_inj,
                'gas_per_injection': gas_per_inj,
                'efficiency_flag': efficiency_flag
            })
    
    return pd.DataFrame(data)

def generate_sample_water_cut_analysis_data():
    """Generate sample GOLD TABLE 3 - Water cut analysis data"""
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            oil = np.random.uniform(8000, 18000)
            water = np.random.uniform(3000, 10000)
            water_cut_pct = (water / (oil + water)) * 100
            water_issue_flag = 'HIGH_WATER' if water > oil else 'NORMAL'
            
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': oil,
                'water': water,
                'water_cut_pct': water_cut_pct,
                'water_issue_flag': water_issue_flag
            })
    
    return pd.DataFrame(data)

def generate_sample_optimization_candidates_data():
    """Generate sample GOLD TABLE 4 - Optimization candidates data"""
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            oil = np.random.uniform(8000, 18000)
            water = np.random.uniform(3000, 10000)
            gas_inj = np.random.uniform(20000, 35000)
            water_inj = np.random.uniform(5000, 10000)
            
            oil_to_fluid_ratio = oil / (oil + water)
            injection_intensity = gas_inj + water_inj
            optimization_candidate = 'YES' if (oil_to_fluid_ratio < 0.4 and injection_intensity > 20000) else 'NO'
            
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': oil,
                'water': water,
                'gas_injection': gas_inj,
                'water_injection': water_inj,
                'oil_to_fluid_ratio': oil_to_fluid_ratio,
                'injection_intensity': injection_intensity,
                'optimization_candidate': optimization_candidate
            })
    
    return pd.DataFrame(data)

# =====================================================
# LEGACY DATA GENERATION FUNCTIONS (For Dashboard Support)
# =====================================================

def generate_production_plan_data():
    """Generate sample production plan data"""
    dates = pd.date_range(start='2026-05-01', end='2026-06-30', freq='D')
    np.random.seed(42)
    
    actual = np.random.normal(loc=500, scale=50, size=len(dates))
    forecast = 450 + np.arange(len(dates)) * 0.5
    
    df = pd.DataFrame({
        'date': dates,
        'actual': np.maximum(actual, 0),
        'forecast': forecast,
        'sm3d': np.cumsum(forecast)
    })
    
    return df

def generate_well_performance_data():
    """Generate sample well performance data"""
    dates = pd.date_range(start='2014-03-01', end='2026-04-30', freq='D')
    np.random.seed(42)
    
    # Decline curve simulation
    months = np.arange(len(dates)) / 30
    decline_curve = 1200 * np.exp(-0.15 * months)
    noise = np.random.normal(0, 30, len(dates))
    oil_rate = np.maximum(decline_curve + noise, 0)
    
    df = pd.DataFrame({
        'date': dates,
        'oil_rate': oil_rate,
        'forecast_rate': decline_curve,
        'cumulative': np.cumsum(oil_rate)
    })
    
    return df

def generate_monthly_data():
    """Generate monthly production data"""
    months = ['Mar 2014', 'Apr 2014', 'May 2014', 'Jun 2014', 'Jul 2014']
    actual = [1175.5, 814.4, 667.0, 487.7, 386.4]
    forecast = ['-', '-', '5', '-', '-']
    variance = ['-', '-', '-', '-', '-']
    cum_actual = [11142.47, 36044.42, 55362.18, 70747.86, 77718.29]
    cum_forecast = ['-', '-', '-', '-', '-']
    
    return pd.DataFrame({
        'Month': months,
        'Actual (Sm³/d)': actual,
        'Forecast (Sm³/d)': forecast,
        'Variance (%)': variance,
        'Cum. Actual (Sm³)': cum_actual,
        'Cum. Forecast (Sm³)': cum_forecast
    })

def generate_variance_data():
    """Generate variance over time data"""
    dates = pd.date_range(start='2016-10-01', end='2025-11-30', freq='D')
    np.random.seed(42)
    variance = np.random.normal(0, 0.05, len(dates))
    
    return pd.DataFrame({
        'date': dates,
        'variance': variance
    })

# Updated load functions with fallback to sample data
@st.cache_data
def load_annual_production_data_with_fallback(db):
    """Load GOLD TABLE 1 with fallback to sample data"""
    try:
        if db:
            try:
                return db.get_annual_production_data()
            except Exception as e:
                logging.warning(f"Could not load annual production from Databricks: {str(e)}")
        return generate_sample_annual_production_data()
    except Exception as e:
        logging.error(f"Error in load_annual_production_data_with_fallback: {str(e)}")
        return pd.DataFrame({'wellbore_name': ['Well 1'], 'year': [2026], 'oil': [1000]})

@st.cache_data
def load_production_efficiency_data_with_fallback(db):
    """Load GOLD TABLE 2 with fallback to sample data"""
    try:
        if db:
            try:
                return db.get_production_efficiency_data()
            except Exception as e:
                logging.warning(f"Could not load efficiency data from Databricks: {str(e)}")
        return generate_sample_production_efficiency_data()
    except Exception as e:
        logging.error(f"Error in load_production_efficiency_data_with_fallback: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_water_cut_analysis_data_with_fallback(db):
    """Load GOLD TABLE 3 with fallback to sample data"""
    try:
        if db:
            try:
                return db.get_water_cut_analysis_data()
            except Exception as e:
                logging.warning(f"Could not load water cut data from Databricks: {str(e)}")
        return generate_sample_water_cut_analysis_data()
    except Exception as e:
        logging.error(f"Error in load_water_cut_analysis_data_with_fallback: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_optimization_candidates_data_with_fallback(db):
    """Load GOLD TABLE 4 with fallback to sample data"""
    try:
        if db:
            try:
                return db.get_optimization_candidates_data()
            except Exception as e:
                logging.warning(f"Could not load optimization data from Databricks: {str(e)}")
        return generate_sample_optimization_candidates_data()
    except Exception as e:
        logging.error(f"Error in load_optimization_candidates_data_with_fallback: {str(e)}")
        return pd.DataFrame()

# Generate sample data
    """Generate sample production plan data"""
    dates = pd.date_range(start='2026-05-01', end='2026-06-30', freq='D')
    np.random.seed(42)
    
    actual = np.random.normal(loc=500, scale=50, size=len(dates))
    forecast = 450 + np.arange(len(dates)) * 0.5
    
    df = pd.DataFrame({
        'date': dates,
        'actual': np.maximum(actual, 0),
        'forecast': forecast,
        'sm3d': np.cumsum(forecast)
    })
    
    return df

def generate_well_performance_data():
    """Generate sample well performance data"""
    dates = pd.date_range(start='2014-03-01', end='2026-04-30', freq='D')
    np.random.seed(42)
    
    # Decline curve simulation
    months = np.arange(len(dates)) / 30
    decline_curve = 1200 * np.exp(-0.15 * months)
    noise = np.random.normal(0, 30, len(dates))
    oil_rate = np.maximum(decline_curve + noise, 0)
    
    df = pd.DataFrame({
        'date': dates,
        'oil_rate': oil_rate,
        'forecast_rate': decline_curve,
        'cumulative': np.cumsum(oil_rate)
    })
    
    return df

def generate_monthly_data():
    """Generate monthly production data"""
    months = ['Mar 2014', 'Apr 2014', 'May 2014', 'Jun 2014', 'Jul 2014']
    actual = [1175.5, 814.4, 667.0, 487.7, 386.4]
    forecast = ['-', '-', '5', '-', '-']
    variance = ['-', '-', '-', '-', '-']
    cum_actual = [11142.47, 36044.42, 55362.18, 70747.86, 77718.29]
    cum_forecast = ['-', '-', '-', '-', '-']
    
    return pd.DataFrame({
        'Month': months,
        'Actual (Sm³/d)': actual,
        'Forecast (Sm³/d)': forecast,
        'Variance (%)': variance,
        'Cum. Actual (Sm³)': cum_actual,
        'Cum. Forecast (Sm³)': cum_forecast
    })

def generate_variance_data():
    """Generate variance over time data"""
    dates = pd.date_range(start='2016-10-01', end='2025-11-30', freq='D')
    np.random.seed(42)
    variance = np.random.normal(0, 0.05, len(dates))
    
    return pd.DataFrame({
        'date': dates,
        'variance': variance
    })

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Field Overview"

# Sidebar navigation
with st.sidebar:
    st.markdown('<div class="sidebar-title">Production Dashboard</div>', unsafe_allow_html=True)
    st.markdown("**Oil & Gas Surveillance**")
    st.divider()
    
    # Navigation buttons
    pages = {
        "Field Overview": "🏭",
        "Well Performance": "⚙️",
        "Production Planning": "📊",
        "Forecast & Reserves": "📈",
        "Actions & Alerts": "⚠️"
    }
    
    for page_name, icon in pages.items():
        if st.button(f"{icon} {page_name}", use_container_width=True):
            st.session_state.page = page_name
    
    st.divider()
    
    # Filters
    st.subheader("Filters & Settings")
    
    # Wells filter
    st.write("**WELLS**")
    col1, col2 = st.columns(2)
    with col1:
        st.button("All", use_container_width=True)
    with col2:
        st.button("None", use_container_width=True)
    
    # File upload
    st.divider()
    st.button("📤 Upload New File", use_container_width=True)

# Main content area
# Get Databricks connection
db = get_db_connection()

# Display connection status (after cache initialization)
if db is None:
    st.info("📊 Displaying sample data (Databricks connection unavailable)")

if st.session_state.page == "Field Overview":
    st.title("Field Overview")
    st.write("Overview of all wells and field-level metrics from Databricks GOLD layer")
    
    # Load GOLD TABLE 1 - Annual Production (with fallback)
    df_annual = load_annual_production_data_with_fallback(db)
    
    if db is None:
        st.info("📊 Displaying sample data (Databricks connection unavailable)")
    
    if df_annual is not None and not df_annual.empty:
        # Get latest year data
        latest_year = df_annual['year'].max() if 'year' in df_annual.columns else None
        
        # Filter for latest year
        if latest_year:
            df_latest = df_annual[df_annual['year'] == latest_year]
            
            # Calculate metrics
            total_oil = df_latest['oil'].sum() if 'oil' in df_latest.columns else 0
            total_gas = df_latest['gas'].sum() if 'gas' in df_latest.columns else 0
            total_water = df_latest['water'].sum() if 'water' in df_latest.columns else 0
            total_fluids = df_latest['total_fluids'].sum() if 'total_fluids' in df_latest.columns else total_oil + total_water
            num_wells = len(df_latest)
            
            # Display metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Oil (Sm³)", f"{total_oil:,.0f}")
            with col2:
                st.metric("Total Gas (Sm³)", f"{total_gas:,.0f}")
            with col3:
                st.metric("Total Water (Sm³)", f"{total_water:,.0f}")
            with col4:
                st.metric("Total Fluids (Sm³)", f"{total_fluids:,.0f}")
            with col5:
                st.metric("Active Wells", num_wells)
            
            # Display annual production table
            st.subheader(f"Annual Production - Year {latest_year}")
            st.dataframe(df_latest, use_container_width=True)
            
            # Load and display efficiency data
            df_efficiency = load_production_efficiency_data_with_fallback(db)
            if df_efficiency is not None and not df_efficiency.empty:
                st.subheader("Production Efficiency Analysis")
                
                # Filter efficiency data for latest year
                df_eff_latest = df_efficiency[df_efficiency['year'] == latest_year]
                
                # Display efficiency metrics
                col1, col2 = st.columns(2)
                with col1:
                    if 'oil_per_injection' in df_eff_latest.columns:
                        avg_oil_per_inj = df_eff_latest['oil_per_injection'].mean()
                        st.metric("Avg Oil per Injection", f"{avg_oil_per_inj:.2f}")
                with col2:
                    if 'gas_per_injection' in df_eff_latest.columns:
                        avg_gas_per_inj = df_eff_latest['gas_per_injection'].mean()
                        st.metric("Avg Gas per Injection", f"{avg_gas_per_inj:.2f}")
                
                st.dataframe(df_eff_latest, use_container_width=True)
    else:
        st.warning("No annual production data available.")

elif st.session_state.page == "Well Performance":
    st.title("Well Performance")
    st.write("Detailed analysis for individual wells from Databricks GOLD layer")
    
    if db is None:
        st.info("📊 Displaying sample data (Databricks connection unavailable)")
    
    # Load GOLD data (with fallback)
    df_annual = load_annual_production_data_with_fallback(db)
    df_water_cut = load_water_cut_analysis_data_with_fallback(db)
    df_efficiency = load_production_efficiency_data_with_fallback(db)
    
    if df_annual is not None and not df_annual.empty:
        # Get available wells
        wells = sorted(df_annual['wellbore_name'].unique().tolist()) if 'wellbore_name' in df_annual.columns else []
        
        # Well selector
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_well = st.selectbox("Select Well", wells if wells else ["No wells available"])
        with col2:
            st.button("Export")
        
        if selected_well and selected_well != "No wells available":
            # Filter data for selected well
            well_annual = df_annual[df_annual['wellbore_name'] == selected_well]
            
            if not well_annual.empty:
                # Get latest year data for this well
                latest_well_data = well_annual[well_annual['year'] == well_annual['year'].max()].iloc[0]
                
                # Calculate actual rate (daily), forecast rate, and cumulative values
                oil_actual = latest_well_data.get('oil', 0)
                actual_rate = oil_actual / 365  # Convert annual to daily
                forecast_rate = actual_rate * 0.48  # Forecast at 48% of actual
                variance = ((actual_rate - forecast_rate) / forecast_rate * 100) if forecast_rate > 0 else 0
                
                # Calculate cumulative values
                total_production = well_annual['oil'].sum()
                cum_actual = total_production
                cum_forecast = cum_actual * 1.08  # Forecast slightly higher
                
                # Calculate months since last history (using year data as proxy)
                years_in_data = len(well_annual)
                months_since = years_in_data * 12
                
                # Display top metrics
                st.markdown("---")
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    st.metric("ACTUAL RATE", f"{actual_rate:.1f}", "Sm³/d")
                
                with col2:
                    st.metric("FORECAST RATE", f"{forecast_rate:.1f}", "Sm³/d")
                
                with col3:
                    st.metric("VARIANCE", f"{variance:.1f}%")
                
                with col4:
                    st.metric("CUM. ACTUAL", f"{cum_actual/1000:.1f}K", "Sm³")
                
                with col5:
                    st.metric("CUM. FORECAST", f"{cum_forecast/1000:.1f}K", "Sm³")
                
                with col6:
                    st.metric("SINCE LAST HIST.", months_since, "months")
                
                st.markdown("---")
                
                # Display well metrics
                st.subheader(f"{selected_well} - Key Metrics (Year {latest_well_data['year']})")
                
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    oil_val = latest_well_data.get('oil', 0)
                    st.metric("Oil (Sm³)", f"{oil_val:,.0f}")
                
                with col2:
                    gas_val = latest_well_data.get('gas', 0)
                    st.metric("Gas (Sm³)", f"{gas_val:,.0f}")
                
                with col3:
                    water_val = latest_well_data.get('water', 0)
                    st.metric("Water (Sm³)", f"{water_val:,.0f}")
                
                with col4:
                    gas_inj = latest_well_data.get('gas_injection', 0)
                    st.metric("Gas Injection", f"{gas_inj:,.0f}")
                
                with col5:
                    water_inj = latest_well_data.get('water_injection', 0)
                    st.metric("Water Injection", f"{water_inj:,.0f}")
                
                with col6:
                    total_fluids = latest_well_data.get('total_fluids', 0)
                    st.metric("Total Fluids", f"{total_fluids:,.0f}")
                
                # Oil Rate and Cumulative Oil Charts
                st.markdown("---")
                chart_col1, chart_col2 = st.columns(2)
                
                if len(well_annual) > 0:
                    well_annual_sorted = well_annual.sort_values('year')
                    
                    # Calculate cumulative oil
                    well_annual_sorted = well_annual_sorted.copy()
                    well_annual_sorted['cumulative_oil'] = well_annual_sorted['oil'].cumsum()
                    
                    with chart_col1:
                        # Oil Rate chart
                        fig_rate = px.line(well_annual_sorted, 
                                         x='year', 
                                         y='oil',
                                         title=f"{selected_well} - Oil Rate",
                                         markers=True,
                                         labels={'oil': 'Oil (Sm³)', 'year': 'Year'})
                        fig_rate.update_layout(
                            hovermode='x unified',
                            plot_bgcolor='#2d3748',
                            paper_bgcolor='#1a202c',
                            font=dict(color='#ffffff'),
                            xaxis=dict(showgrid=True, gridcolor='#404854'),
                            yaxis=dict(showgrid=True, gridcolor='#404854')
                        )
                        st.plotly_chart(fig_rate, use_container_width=True)
                    
                    with chart_col2:
                        # Cumulative Oil chart
                        fig_cumul = px.line(well_annual_sorted, 
                                          x='year', 
                                          y='cumulative_oil',
                                          title=f"{selected_well} - Cumulative Oil",
                                          labels={'cumulative_oil': 'Cumulative Oil (Sm³)', 'year': 'Year'},
                                          markers=True)
                        fig_cumul.update_traces(fill='tozeroy')
                        fig_cumul.update_layout(
                            hovermode='x unified',
                            plot_bgcolor='#2d3748',
                            paper_bgcolor='#1a202c',
                            font=dict(color='#ffffff'),
                            xaxis=dict(showgrid=True, gridcolor='#404854'),
                            yaxis=dict(showgrid=True, gridcolor='#404854')
                        )
                        st.plotly_chart(fig_cumul, use_container_width=True)
                
                # Annual production trend
                st.subheader("Production Trend")
                if len(well_annual) > 0:
                    fig = px.line(well_annual.sort_values('year'), 
                                 x='year', 
                                 y=['oil', 'gas', 'water'],
                                 title=f"{selected_well} - Production Trend Over Years",
                                 markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Water cut analysis
                if df_water_cut is not None and not df_water_cut.empty:
                    st.subheader("Water Cut Analysis")
                    well_watercut = df_water_cut[df_water_cut['wellbore_name'] == selected_well]
                    if not well_watercut.empty:
                        st.dataframe(well_watercut, use_container_width=True)
                
                # Production efficiency
                if df_efficiency is not None and not df_efficiency.empty:
                    st.subheader("Production Efficiency")
                    well_efficiency = df_efficiency[df_efficiency['wellbore_name'] == selected_well]
                    if not well_efficiency.empty:
                        st.dataframe(well_efficiency, use_container_width=True)
    else:
        st.warning("No production data available for well performance analysis.")

elif st.session_state.page == "Production Planning":
    st.title("Production Planning")
    st.write("Plan and forecast well & field level production based on GOLD data")
    
    if db is None:
        st.info("📊 Displaying sample data (Databricks connection unavailable)")
    
    # Load GOLD data (with fallback)
    df_annual = load_annual_production_data_with_fallback(db)
    df_optimization = load_optimization_candidates_data_with_fallback(db)
    
    if df_annual is not None and not df_annual.empty:
        # Plan Configuration
        st.subheader("Plan Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Production Plan Schedule**")
            plan_schedule = st.selectbox(
                "Select Schedule",
                ["Short Term (3 months)", "Short Term (6 months)", "Long Term (1 year)", "Long Term (2 years)", "Long Term (3 years)"],
                label_visibility="collapsed"
            )
        
        with col2:
            st.write("**Scope (Field / Well)**")
            scope = st.selectbox(
                "Select Scope",
                ["Overall Field"] + sorted(df_annual['wellbore_name'].unique().tolist()) if 'wellbore_name' in df_annual.columns else ["Overall Field"],
                label_visibility="collapsed"
            )
        
        st.divider()
        
        # Production Charts
        st.subheader("Production Plan Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Production Plan - Rate Trend**")
            plan_data = generate_production_plan_data()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=plan_data['date'], y=plan_data['actual'],
                mode='lines', name='Actual', line=dict(color='#0ea5e9', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=plan_data['date'], y=plan_data['forecast'],
                mode='lines', name='Forecast', line=dict(color='#ea580c', dash='dash', width=2)
            ))
            fig.update_layout(
                hovermode='x unified', height=400, template='plotly_dark',
                xaxis_title="Date", yaxis_title="Sm³/d",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Cumulative Production Plan**")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=plan_data['date'], y=plan_data['sm3d'],
                fill='tozeroy', name='Cumulative', line=dict(color='#ea580c', width=2),
                fillcolor='rgba(234, 88, 12, 0.2)'
            ))
            fig.add_trace(go.Scatter(
                x=plan_data['date'], y=plan_data['sm3d'] * 0.95,
                mode='lines', name='Actual', line=dict(color='#0ea5e9', width=2)
            ))
            fig.update_layout(
                hovermode='x unified', height=400, template='plotly_dark',
                xaxis_title="Date", yaxis_title="Sm³",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Production Plan Data Table
        st.subheader("Production Plan Data")
        table_data = pd.DataFrame({
            'Month': ['May 2026', 'Jun 2026'],
            'Forecast Rate (Sm³/d)': [664.99, 659.42],
            'Cum. Forecast (Sm³)': ['20.0K', '40.4K']
        })
        
        st.dataframe(table_data, use_container_width=True, hide_index=True)
        
        # Display optimization candidates
        st.divider()
        st.subheader("Well Optimization Candidates")
        if df_optimization is not None and not df_optimization.empty:
            latest_year = df_annual['year'].max()
            df_opt_latest = df_optimization[df_optimization['year'] == latest_year]
            
            # Filter optimization candidates
            optimization_wells = df_opt_latest[
                (df_opt_latest.get('optimization_candidate', 'NO') == 'YES') |
                (df_opt_latest.get('optimization_candidate', 'NO') == True)
            ] if 'optimization_candidate' in df_opt_latest.columns else df_opt_latest
            
            if not optimization_wells.empty:
                st.markdown("**Wells suitable for optimization actions:**")
                st.dataframe(optimization_wells, use_container_width=True)
            else:
                st.info("No optimization candidates identified for this period.")
        
        # Production planning metrics
        st.divider()
        st.subheader("Planning Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        latest_year = df_annual['year'].max()
        df_latest = df_annual[df_annual['year'] == latest_year]
        
        with col1:
            avg_oil = df_latest['oil'].mean() if 'oil' in df_latest.columns else 0
            st.metric("Avg Oil Production", f"{avg_oil:,.0f} Sm³")
        
        with col2:
            avg_gas = df_latest['gas'].mean() if 'gas' in df_latest.columns else 0
            st.metric("Avg Gas Production", f"{avg_gas:,.0f} Sm³")
        
        with col3:
            avg_water = df_latest['water'].mean() if 'water' in df_latest.columns else 0
            st.metric("Avg Water Production", f"{avg_water:,.0f} Sm³")
        
        with col4:
            num_wells = len(df_latest)
            st.metric("Active Wells", num_wells)
    else:
        st.warning("No production planning data available.")

elif st.session_state.page == "Forecast & Reserves":
    st.title("Forecast & Reserves")
    st.write("Reserve estimates and production forecasts from GOLD analysis")
    
    if db is None:
        st.info("📊 Displaying sample data (Databricks connection unavailable)")
    
    df_annual = load_annual_production_data_with_fallback(db)
    
    if df_annual is not None and not df_annual.empty:
        # Calculate cumulative reserves
        total_reserves = df_annual['oil'].sum() if 'oil' in df_annual.columns else 0
        total_reserves_gas = df_annual['gas'].sum() if 'gas' in df_annual.columns else 0
        total_reserves_water = df_annual['water'].sum() if 'water' in df_annual.columns else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cumulative Oil Reserves", f"{total_reserves:,.0f} Sm³")
        with col2:
            st.metric("Cumulative Gas Reserves", f"{total_reserves_gas:,.0f} Sm³")
        with col3:
            st.metric("Cumulative Water", f"{total_reserves_water:,.0f} Sm³")
        
        st.subheader("Historical Production Data")
        st.dataframe(df_annual, use_container_width=True)
        
        # Production trend chart
        st.subheader("Production Trend Over Years")
        if 'year' in df_annual.columns:
            yearly_sum = df_annual.groupby('year')[['oil', 'gas', 'water']].sum().reset_index()
            fig = px.bar(yearly_sum, x='year', y=['oil', 'gas', 'water'],
                        title="Yearly Production Summary",
                        labels={'value': 'Production (Sm³)', 'year': 'Year'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No forecast data available.")

elif st.session_state.page == "Actions & Alerts":
    st.title("Actions & Alerts")
    st.write("Critical actions and optimization candidates from GOLD analysis")
    
    if db is None:
        st.info("📊 Displaying sample data (Databricks connection unavailable)")
    
    df_water_cut = load_water_cut_analysis_data_with_fallback(db)
    df_optimization = load_optimization_candidates_data_with_fallback(db)
    
    # Water cut alerts
    if df_water_cut is not None and not df_water_cut.empty:
        st.subheader("⚠️ Water Cut Alerts")
        
        # Find wells with HIGH_WATER flag
        high_water_wells = df_water_cut[
            (df_water_cut.get('water_issue_flag', '') == 'HIGH_WATER') |
            (df_water_cut.get('water_issue_flag', '') == 'HIGH')
        ] if 'water_issue_flag' in df_water_cut.columns else df_water_cut[df_water_cut['water_cut_pct'] > 50]
        
        if not high_water_wells.empty:
            st.warning(f"🔴 {len(high_water_wells)} wells flagged with high water cut")
            st.dataframe(high_water_wells[['wellbore_name', 'year', 'water_cut_pct', 'water_issue_flag']], 
                       use_container_width=True)
        else:
            st.success("✅ No high water cut alerts")
    
    # Optimization candidates
    if df_optimization is not None and not df_optimization.empty:
        st.subheader("🎯 Optimization Candidates")
        
        opt_candidates = df_optimization[
            (df_optimization.get('optimization_candidate', 'NO') == 'YES') |
            (df_optimization.get('optimization_candidate', 'NO') == True)
        ] if 'optimization_candidate' in df_optimization.columns else df_optimization
        
        if not opt_candidates.empty:
            st.info(f"💡 {len(opt_candidates)} wells identified for optimization")
            display_cols = ['wellbore_name', 'year', 'oil_to_fluid_ratio', 'injection_intensity', 'optimization_candidate']
            display_cols = [c for c in display_cols if c in opt_candidates.columns]
            st.dataframe(opt_candidates[display_cols], use_container_width=True)
        else:
            st.info("No optimization candidates at this time")
    
    # Recent actions
    st.subheader("📋 Recent System Actions")
    actions_df = pd.DataFrame({
        'Date': ['2026-04-07', '2026-04-06', '2026-04-05'],
        'Action': ['GOLD tables updated with production data', 'Water cut analysis completed', 'Optimization analysis completed'],
        'Status': ['Completed', 'Completed', 'Completed']
    })
    st.dataframe(actions_df, use_container_width=True, hide_index=True)
