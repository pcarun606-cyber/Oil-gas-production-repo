import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

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
    .metric-card {
        background-color: #2d3748;
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #00d4ff;
    }
    .metric-unit {
        font-size: 14px;
        color: #cbd5e0;
    }
    .sidebar-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data
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
if st.session_state.page == "Field Overview":
    st.title("Field Overview")
    st.write("Overview of all wells and field-level metrics")
    
    # Placeholder for field overview content
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Production", "2,450 Sm³/d")
    with col2:
        st.metric("Total Wells", "5")

elif st.session_state.page == "Well Performance":
    st.title("Well Performance")
    st.write("Detailed analysis for individual well")
    
    # Well selector
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_well = st.selectbox("Select Well", ["Well 1", "Well 2", "Well 3", "Well 4", "Well 5"])
    with col2:
        st.button("Export")
    
    # Metric cards
    st.subheader(f"{selected_well} - Key Metrics")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 12px; color: #a0aec0;">ACTUAL RATE</div>
            <div class="metric-value">29.3</div>
            <div class="metric-unit">Sm³/d</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="background-color: #d69e2e;">
            <div style="font-size: 12px; color: #eedae8;">FORECAST RATE</div>
            <div class="metric-value" style="color: #fff;">14.3</div>
            <div class="metric-unit">Sm³/d</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="background-color: #38a169;">
            <div style="font-size: 12px; color: #c6f6d5;">VARIANCE</div>
            <div class="metric-value" style="color: #fff;">104.6%</div>
            <div class="metric-unit" style="color: #fff;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 12px; color: #a0aec0;">CUM. ACTUAL</div>
            <div class="metric-value">520.2K</div>
            <div class="metric-unit">Sm³</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 12px; color: #a0aec0;">CUM. FORECAST</div>
            <div class="metric-value">561.6K</div>
            <div class="metric-unit">Sm³</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 12px; color: #a0aec0;">SINCE LAST HIST.</div>
            <div class="metric-value">121</div>
            <div class="metric-unit">months</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"{selected_well} - Oil Rate")
        well_data = generate_well_performance_data()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=well_data['date'], y=well_data['oil_rate'],
            mode='lines', name='Actual', line=dict(color='#0ea5e9', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=well_data['date'], y=well_data['forecast_rate'],
            mode='lines', name='Forecast', line=dict(color='#ea580c', dash='dash', width=2)
        ))
        fig.update_layout(
            hovermode='x unified', height=400, template='plotly_dark',
            xaxis_title="Date", yaxis_title="Sm³/d",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(f"{selected_well} - Cumulative Oil")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=well_data['date'], y=well_data['cumulative'],
            fill='tozeroy', name='Cumulative', line=dict(color='#0ea5e9', width=2),
            fillcolor='rgba(14, 165, 233, 0.2)'
        ))
        fig.add_trace(go.Scatter(
            x=well_data['date'], y=well_data['cumulative'] * 1.1,
            mode='lines', name='Forecast', line=dict(color='#ea580c', dash='dash', width=2)
        ))
        fig.update_layout(
            hovermode='x unified', height=400, template='plotly_dark',
            xaxis_title="Date", yaxis_title="Sm³",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Variance chart
    st.subheader(f"{selected_well} - Variance Over Time")
    variance_data = generate_variance_data()
    
    fig = go.Figure()
    colors = ['#22c55e' if x >= 0 else '#eab308' for x in variance_data['variance']]
    fig.add_trace(go.Bar(
        x=variance_data['date'], y=variance_data['variance'],
        marker=dict(color=colors), name='Variance'
    ))
    fig.update_layout(
        hovermode='x', height=400, template='plotly_dark',
        xaxis_title="Date", yaxis_title="Variance (%)",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly data table
    st.subheader(f"{selected_well} - Monthly Production Data")
    monthly_df = generate_monthly_data()
    st.dataframe(monthly_df, use_container_width=True, hide_index=True)

elif st.session_state.page == "Production Planning":
    st.title("Production Planning")
    st.write("Plan and forecast well & field level production")
    
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
            ["Overall Field", "Well 1", "Well 2", "Well 3", "Well 4", "Well 5"],
            label_visibility="collapsed"
        )
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Production Plan - Rate Trend")
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
        st.subheader("Cumulative Production Plan")
        
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

elif st.session_state.page == "Forecast & Reserves":
    st.title("Forecast & Reserves")
    st.write("Reserve estimates and production forecasts")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Remaining Reserves", "5,200 Sm³")
    with col2:
        st.metric("Forecast Horizon", "10 years")

elif st.session_state.page == "Actions & Alerts":
    st.title("Actions & Alerts")
    st.write("Critical actions and system alerts")
    
    st.info("📋 No active alerts at this moment")
    
    st.subheader("Recent Actions")
    actions_df = pd.DataFrame({
        'Date': ['2026-04-05', '2026-04-03', '2026-03-30'],
        'Action': ['Production forecast updated', 'Well 3 maintenance completed', 'New data uploaded'],
        'Status': ['Completed', 'Completed', 'Completed']
    })
    
    st.dataframe(actions_df, use_container_width=True, hide_index=True)
