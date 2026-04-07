import streamlit as st

# CRITICAL: set_page_config MUST be first streamlit command
st.set_page_config(
    page_title="Production Dashboard",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# NOW import everything else
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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

# Apply minimal CSS at module level (only styling, no other st. commands)
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #1a202c; }
[data-testid="stSidebar"] { background-color: #0f1419; }
* { color: #ffffff !important; }
body, div, p, span, label, h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
.stMetric { background-color: #2d3748; padding: 12px; border-radius: 8px; margin: 8px 0; }
.stDataFrame { background-color: #2d3748; }
.stButton > button { background-color: #2d3748; color: #00d4ff; border: 1px solid #00d4ff; }
.stSelectbox > div > div { background-color: #0f1419 !important; border: 1px solid #2d3748 !important; }
[role="option"] { background-color: #0f1419 !important; color: #ffffff !important; }
[role="option"]:hover { background-color: #2d3748 !important; }
</style>
""", unsafe_allow_html=True)

# Get database connection
@st.cache_resource
def get_db_connection():
    """Get cached Databricks connection"""
    try:
        if get_databricks_connection is None:
            return None
        db = get_databricks_connection()
        if db and hasattr(db, 'connect') and db.connect():
            return db
        return None
    except Exception as e:
        logging.error(f"DB Connection error: {e}")
        return None

# Sample data generators
def generate_sample_annual_production_data():
    """Generate sample GOLD TABLE 1"""
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
                'total_fluids': np.random.uniform(11000, 28000)
            })
    return pd.DataFrame(data)

def generate_sample_production_efficiency_data():
    """Generate sample GOLD TABLE 2"""
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
            
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': oil,
                'gas': gas,
                'gas_injection': gas_inj,
                'water_injection': water_inj,
                'oil_per_injection': oil / (gas_inj + water_inj),
                'gas_per_injection': gas / (gas_inj + water_inj),
                'efficiency_flag': 'LOW' if oil / (gas_inj + water_inj) < 0.5 else 'NORMAL'
            })
    return pd.DataFrame(data)

def generate_sample_water_cut_analysis_data():
    """Generate sample GOLD TABLE 3"""
    np.random.seed(42)
    wells = ['Well-001', 'Well-002', 'Well-003', 'Well-004', 'Well-005']
    years = [2023, 2024, 2025, 2026]
    
    data = []
    for well in wells:
        for year in years:
            oil = np.random.uniform(8000, 18000)
            water = np.random.uniform(3000, 10000)
            
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': oil,
                'water': water,
                'water_cut_pct': (water / (oil + water)) * 100,
                'water_issue_flag': 'HIGH_WATER' if water > oil else 'NORMAL'
            })
    return pd.DataFrame(data)

def generate_sample_optimization_candidates_data():
    """Generate sample GOLD TABLE 4"""
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
            
            ratio = oil / (oil + water)
            intensity = gas_inj + water_inj
            
            data.append({
                'wellbore_name': well,
                'year': year,
                'oil': oil,
                'water': water,
                'gas_injection': gas_inj,
                'water_injection': water_inj,
                'oil_to_fluid_ratio': ratio,
                'injection_intensity': intensity,
                'optimization_candidate': 'YES' if (ratio < 0.4 and intensity > 20000) else 'NO'
            })
    return pd.DataFrame(data)

def generate_production_plan_data():
    """Generate production plan data"""
    dates = pd.date_range(start='2026-05-01', end='2026-06-30', freq='D')
    np.random.seed(42)
    
    actual = np.random.normal(loc=500, scale=50, size=len(dates))
    forecast = 450 + np.arange(len(dates)) * 0.5
    
    return pd.DataFrame({
        'date': dates,
        'actual': np.maximum(actual, 0),
        'forecast': forecast,
        'sm3d': np.cumsum(forecast)
    })

# Cache data loaders with fallback
@st.cache_data
def load_annual_production_data(db):
    """Load GOLD TABLE 1 with fallback"""
    try:
        if db and hasattr(db, 'get_annual_production_data'):
            return db.get_annual_production_data()
    except Exception as e:
        logging.warning(f"Could not load from Databricks: {e}")
    return generate_sample_annual_production_data()

@st.cache_data
def load_production_efficiency_data(db):
    """Load GOLD TABLE 2 with fallback"""
    try:
        if db and hasattr(db, 'get_production_efficiency_data'):
            return db.get_production_efficiency_data()
    except Exception as e:
        logging.warning(f"Could not load efficiency data: {e}")
    return generate_sample_production_efficiency_data()

@st.cache_data
def load_water_cut_analysis_data(db):
    """Load GOLD TABLE 3 with fallback"""
    try:
        if db and hasattr(db, 'get_water_cut_analysis_data'):
            return db.get_water_cut_analysis_data()
    except Exception as e:
        logging.warning(f"Could not load water cut data: {e}")
    return generate_sample_water_cut_analysis_data()

@st.cache_data
def load_optimization_candidates_data(db):
    """Load GOLD TABLE 4 with fallback"""
    try:
        if db and hasattr(db, 'get_optimization_candidates_data'):
            return db.get_optimization_candidates_data()
    except Exception as e:
        logging.warning(f"Could not load optimization data: {e}")
    return generate_sample_optimization_candidates_data()

# MAIN APP FUNCTION - All Streamlit logic wrapped here
def main():
    """Main application logic"""
    
    # Get database connection
    db = get_db_connection()
    
    # Show connection status
    if db is None:
        st.info("📊 Operating in sample data mode (Databricks unavailable)")
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Field Overview"
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### Production Dashboard")
        st.markdown("Oil & Gas Surveillance")
        st.divider()
        
        pages = ["Field Overview", "Well Performance", "Production Planning", "Forecast & Reserves", "Actions & Alerts"]
        selected_page = st.selectbox("Select Page", pages)
        st.session_state.page = selected_page
        
        st.divider()
        st.button("📤 Upload New File", use_container_width=True)
    
    # PAGE: FIELD OVERVIEW
    if st.session_state.page == "Field Overview":
        st.title("Field Overview")
        st.write("Overview of all wells and field-level metrics")
        
        df_annual = load_annual_production_data(db)
        
        if df_annual is not None and not df_annual.empty:
            latest_year = df_annual['year'].max() if 'year' in df_annual.columns else 2026
            df_latest = df_annual[df_annual['year'] == latest_year]
            
            # Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Oil (Sm³)", f"{df_latest['oil'].sum():,.0f}")
            with col2:
                st.metric("Total Gas (Sm³)", f"{df_latest['gas'].sum():,.0f}")
            with col3:
                st.metric("Total Water (Sm³)", f"{df_latest['water'].sum():,.0f}")
            with col4:
                st.metric("Total Fluids (Sm³)", f"{(df_latest['oil'].sum() + df_latest['water'].sum()):,.0f}")
            with col5:
                st.metric("Active Wells", len(df_latest))
            
            # Data table
            st.subheader(f"Annual Production - Year {latest_year}")
            st.dataframe(df_latest, use_container_width=True)
            
            # Efficiency analysis
            df_efficiency = load_production_efficiency_data(db)
            if df_efficiency is not None and not df_efficiency.empty:
                st.subheader("Production Efficiency Analysis")
                df_eff_latest = df_efficiency[df_efficiency['year'] == latest_year]
                
                col1, col2 = st.columns(2)
                with col1:
                    if 'oil_per_injection' in df_eff_latest.columns:
                        st.metric("Avg Oil per Injection", f"{df_eff_latest['oil_per_injection'].mean():.2f}")
                with col2:
                    if 'gas_per_injection' in df_eff_latest.columns:
                        st.metric("Avg Gas per Injection", f"{df_eff_latest['gas_per_injection'].mean():.2f}")
                
                st.dataframe(df_eff_latest, use_container_width=True)
    
    # PAGE: WELL PERFORMANCE
    elif st.session_state.page == "Well Performance":
        st.title("Well Performance")
        st.write("Detailed analysis for individual wells")
        
        df_annual = load_annual_production_data(db)
        df_water_cut = load_water_cut_analysis_data(db)
        df_efficiency = load_production_efficiency_data(db)
        
        if df_annual is not None and not df_annual.empty:
            wells = sorted(df_annual['wellbore_name'].unique().astype(str).tolist()) if 'wellbore_name' in df_annual.columns else []
            
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_well = st.selectbox("Select Well", wells if wells else ["No data"])
            with col2:
                st.button("Export")
            
            if selected_well and selected_well != "No data" and wells:
                well_data = df_annual[df_annual['wellbore_name'] == selected_well]
                
                if not well_data.empty:
                    latest = well_data[well_data['year'] == well_data['year'].max()].iloc[0]
                    
                    # Metrics
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    with col1:
                        st.metric("Oil (Sm³)", f"{latest.get('oil', 0):,.0f}")
                    with col2:
                        st.metric("Gas (Sm³)", f"{latest.get('gas', 0):,.0f}")
                    with col3:
                        st.metric("Water (Sm³)", f"{latest.get('water', 0):,.0f}")
                    with col4:
                        st.metric("Gas Inj", f"{latest.get('gas_injection', 0):,.0f}")
                    with col5:
                        st.metric("Water Inj", f"{latest.get('water_injection', 0):,.0f}")
                    with col6:
                        st.metric("Year", int(latest['year']))
                    
                    # Charts
                    well_data_sorted = well_data.sort_values('year').copy()
                    well_data_sorted['cumulative_oil'] = well_data_sorted['oil'].cumsum()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.line(well_data_sorted, x='year', y='oil',
                                     title=f"{selected_well} - Oil Rate",
                                     markers=True, labels={'oil': 'Oil (Sm³)', 'year': 'Year'})
                        fig.update_layout(
                            plot_bgcolor='#2d3748', paper_bgcolor='#1a202c',
                            font=dict(color='#ffffff'),
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.line(well_data_sorted, x='year', y='cumulative_oil',
                                     title=f"{selected_well} - Cumulative Oil",
                                     markers=True, labels={'cumulative_oil': 'Cumulative Oil (Sm³)', 'year': 'Year'})
                        fig.update_traces(fill='tozeroy')
                        fig.update_layout(
                            plot_bgcolor='#2d3748', paper_bgcolor='#1a202c',
                            font=dict(color='#ffffff'),
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Production trend
                    st.subheader("Production Trend")
                    fig = px.line(well_data_sorted, x='year', y=['oil', 'gas', 'water'],
                                 title=f"{selected_well} - Production Over Time",
                                 markers=True)
                    fig.update_layout(plot_bgcolor='#2d3748', paper_bgcolor='#1a202c', font=dict(color='#ffffff'))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Water cut and efficiency
                    if df_water_cut is not None and not df_water_cut.empty:
                        st.subheader("Water Cut Analysis")
                        well_wc = df_water_cut[df_water_cut['wellbore_name'] == selected_well]
                        if not well_wc.empty:
                            st.dataframe(well_wc, use_container_width=True)
                    
                    if df_efficiency is not None and not df_efficiency.empty:
                        st.subheader("Production Efficiency")
                        well_eff = df_efficiency[df_efficiency['wellbore_name'] == selected_well]
                        if not well_eff.empty:
                            st.dataframe(well_eff, use_container_width=True)
    
    # PAGE: PRODUCTION PLANNING
    elif st.session_state.page == "Production Planning":
        st.title("Production Planning")
        st.write("Plan and forecast production")
        
        df_annual = load_annual_production_data(db)
        df_optimization = load_optimization_candidates_data(db)
        
        if df_annual is not None and not df_annual.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Plan Schedule", ["3 months", "6 months", "1 year", "2 years"])
            with col2:
                wells = sorted(df_annual['wellbore_name'].unique().astype(str).tolist()) if 'wellbore_name' in df_annual.columns else []
                st.selectbox("Scope", ["Overall Field"] + wells)
            
            st.divider()
            
            # Production plan charts
            plan_data = generate_production_plan_data()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plan_data['date'], y=plan_data['actual'],
                                        mode='lines', name='Actual', line=dict(color='#0ea5e9')))
                fig.add_trace(go.Scatter(x=plan_data['date'], y=plan_data['forecast'],
                                        mode='lines', name='Forecast', line=dict(color='#ea580c', dash='dash')))
                fig.update_layout(title="Production Plan - Rate Trend", height=400,
                                 plot_bgcolor='#2d3748', paper_bgcolor='#1a202c',
                                 font=dict(color='#ffffff'), hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plan_data['date'], y=plan_data['sm3d'],
                                        fill='tozeroy', name='Cumulative', line=dict(color='#ea580c'),
                                        fillcolor='rgba(234, 88, 12, 0.2)'))
                fig.update_layout(title="Cumulative Production Plan", height=400,
                                 plot_bgcolor='#2d3748', paper_bgcolor='#1a202c',
                                 font=dict(color='#ffffff'), hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            
            # Optimization candidates
            st.subheader("Well Optimization Candidates")
            if df_optimization is not None and not df_optimization.empty:
                latest_year = df_annual['year'].max()
                opt_wells = df_optimization[(df_optimization['year'] == latest_year) & 
                                           (df_optimization['optimization_candidate'] == 'YES')]
                if not opt_wells.empty:
                    st.info(f"Found {len(opt_wells)} optimization candidates")
                    st.dataframe(opt_wells, use_container_width=True)
                else:
                    st.info("No optimization candidates at this time")
    
    # PAGE: FORECAST & RESERVES
    elif st.session_state.page == "Forecast & Reserves":
        st.title("Forecast & Reserves")
        st.write("Reserve estimates and production forecasts")
        
        df_annual = load_annual_production_data(db)
        
        if df_annual is not None and not df_annual.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cumulative Oil Reserves", f"{df_annual['oil'].sum():,.0f} Sm³")
            with col2:
                st.metric("Cumulative Gas Reserves", f"{df_annual['gas'].sum():,.0f} Sm³")
            with col3:
                st.metric("Cumulative Water", f"{df_annual['water'].sum():,.0f} Sm³")
            
            st.subheader("Historical Production Data")
            st.dataframe(df_annual, use_container_width=True)
            
            # Production trend
            if 'year' in df_annual.columns:
                yearly = df_annual.groupby('year')[['oil', 'gas', 'water']].sum().reset_index()
                fig = px.bar(yearly, x='year', y=['oil', 'gas', 'water'],
                            title="Yearly Production Summary",
                            labels={'value': 'Production (Sm³)', 'year': 'Year'})
                fig.update_layout(plot_bgcolor='#2d3748', paper_bgcolor='#1a202c', font=dict(color='#ffffff'))
                st.plotly_chart(fig, use_container_width=True)
    
    # PAGE: ACTIONS & ALERTS
    elif st.session_state.page == "Actions & Alerts":
        st.title("Actions & Alerts")
        st.write("Critical actions and alerts")
        
        df_water_cut = load_water_cut_analysis_data(db)
        df_optimization = load_optimization_candidates_data(db)
        
        # Water cut alerts
        st.subheader("⚠️ Water Cut Alerts")
        if df_water_cut is not None and not df_water_cut.empty:
            high_water = df_water_cut[df_water_cut['water_cut_pct'] > 50]
            if not high_water.empty:
                st.warning(f"Found {len(high_water)} wells with high water cut")
                st.dataframe(high_water, use_container_width=True)
            else:
                st.success("No high water cut alerts")
        
        # Optimization candidates
        st.subheader("🎯 Optimization Candidates")
        if df_optimization is not None and not df_optimization.empty:
            opt_wells = df_optimization[df_optimization['optimization_candidate'] == 'YES']
            if not opt_wells.empty:
                st.info(f"Found {len(opt_wells)} optimization candidates")
                st.dataframe(opt_wells, use_container_width=True)
            else:
                st.info("No optimization candidates")
        
        # Recent actions
        st.subheader("📋 Recent System Actions")
        actions = pd.DataFrame({
            'Date': ['2026-04-07', '2026-04-06', '2026-04-05'],
            'Action': ['GOLD tables updated', 'Water cut analysis completed', 'Optimization analysis completed'],
            'Status': ['Completed', 'Completed', 'Completed']
        })
        st.dataframe(actions, use_container_width=True, hide_index=True)

# RUN APP WITH ERROR HANDLING
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.info("Please try refreshing the page or restarting the application")
        logging.error(f"Critical app error: {e}", exc_info=True)
