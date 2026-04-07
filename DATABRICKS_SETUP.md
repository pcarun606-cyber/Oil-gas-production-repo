# Databricks GOLD Layer Integration Setup Guide

## Overview
Your Oil & Gas Production Dashboard is now configured to connect to Databricks and display data from the **GOLD Layer** tables. These are refined analytical tables containing production analysis, efficiency metrics, water cut analysis, and optimization candidates.

## Prerequisites
- Databricks workspace with SQL capabilities
- Personal Access Token (PAT) from Databricks
- GOLD layer tables created in your Databricks workspace

## Environment Configuration

The following environment variables are configured in `app.yaml`:

```yaml
- name: DATABRICKS_HOST
  value: "your_workspace_url"
- name: DATABRICKS_TOKEN
  value: "your_token"
- name: DATABRICKS_CATALOG
  value: "oilgasproduction"
- name: DATABRICKS_SCHEMA
  value: "oilgasproductionschema"
- name: DATABRICKS_CLUSTER_ID
  value: "oilgascluster"
```

## GOLD Layer Tables

The application works with the following GOLD layer tables:

### 1. gold_well_annual_production
**Base annual production truth for each well**

```sql
CREATE TABLE IF NOT EXISTS {catalog}.{schema}.gold_well_annual_production (
    wellbore_name STRING,
    year INT,
    oil DOUBLE,              -- Sm³
    gas DOUBLE,              -- Sm³
    water DOUBLE,            -- Sm³
    gas_injection DOUBLE,    -- Sm³
    water_injection DOUBLE,  -- Sm³
    total_fluids DOUBLE,     -- oil + water (Sm³)
    created_at TIMESTAMP,
    CONSTRAINT pk_annual PRIMARY KEY (wellbore_name, year)
) USING DELTA;
```

**Usage:** Base annual production data for well and field overview

### 2. gold_well_production_efficiency
**Oil & Gas production efficiency vs injection efforts - Measure production efficiency**

```sql
CREATE TABLE IF NOT EXISTS {catalog}.{schema}.gold_well_production_efficiency (
    wellbore_name STRING,
    year INT,
    oil DOUBLE,              -- Sm³
    gas DOUBLE,              -- Sm³
    gas_injection DOUBLE,    -- Sm³
    water_injection DOUBLE,  -- Sm³
    oil_per_injection DOUBLE,      -- oil / (gas_injection + water_injection)
    gas_per_injection DOUBLE,      -- gas / (gas_injection + water_injection)
    efficiency_flag STRING,        -- 'LOW' if oil_per_injection < 0.5, else 'NORMAL'
    created_at TIMESTAMP,
    CONSTRAINT pk_efficiency PRIMARY KEY (wellbore_name, year)
) USING DELTA;
```

**Usage:** Analyze production efficiency, identify low-performing wells

### 3. gold_well_water_cut_analysis
**Water cut %, dominance flag - Supports recovery maximization**

```sql
CREATE TABLE IF NOT EXISTS {catalog}.{schema}.gold_well_water_cut_analysis (
    wellbore_name STRING,
    year INT,
    oil DOUBLE,              -- Sm³
    water DOUBLE,            -- Sm³
    water_cut_pct DOUBLE,    -- water / (oil + water) * 100
    water_issue_flag STRING, -- 'HIGH_WATER' if water > oil, else 'NORMAL'
    created_at TIMESTAMP,
    CONSTRAINT pk_watercut PRIMARY KEY (wellbore_name, year)
) USING DELTA;
```

**Usage:** Monitor water production, identify high water cut wells for intervention

### 4. gold_well_optimization_candidates
**Oil-to-fluid ratio, injection stress - Identify optimization opportunities**

```sql
CREATE TABLE IF NOT EXISTS {catalog}.{schema}.gold_well_optimization_candidates (
    wellbore_name STRING,
    year INT,
    oil DOUBLE,              -- Sm³
    water DOUBLE,            -- Sm³
    gas_injection DOUBLE,    -- Sm³
    water_injection DOUBLE,  -- Sm³
    oil_to_fluid_ratio DOUBLE,  -- oil / (oil + water)
    injection_intensity DOUBLE, -- gas_injection + water_injection
    optimization_candidate STRING, -- 'YES' if oil_to_fluid_ratio < 0.4 & injection_intensity > 1000, else 'NO'
    created_at TIMESTAMP,
    CONSTRAINT pk_optimization PRIMARY KEY (wellbore_name, year)
) USING DELTA;
```

**Usage:** Identify wells suitable for optimization actions (injection modifications, workover, etc)

## Application Pages and GOLD Table Usage

### 1. Field Overview
- **Data Source:** GOLD TABLE 1 (gold_well_annual_production) + GOLD TABLE 2 (gold_well_production_efficiency)
- **Displays:** Total field production (Oil, Gas, Water), number of active wells, production efficiency metrics
- **Key Metrics:** Total Oil/Gas/Water (Sm³), Average oil/gas per injection

### 2. Well Performance
- **Data Source:** All 4 GOLD tables
- **Displays:** Individual well analysis with production trends, efficiency, water cut
- **Key Metrics:** Well-specific oil/gas/water production, efficiency flags, water issue alerts

### 3. Production Planning
- **Data Source:** GOLD TABLE 1 + GOLD TABLE 4
- **Displays:** Optimization candidates, production planning metrics
- **Key Metrics:** Wells identified for optimization, average production across field

### 4. Forecast & Reserves
- **Data Source:** GOLD TABLE 1
- **Displays:** Cumulative reserves, historical production trends
- **Key Metrics:** Total reserves, yearly production summary

### 5. Actions & Alerts
- **Data Source:** GOLD TABLE 3 + GOLD TABLE 4
- **Displays:** High water cut alerts, optimization candidates, system actions
- **Key Metrics:** Number of wells flagged, priority wells for intervention

## Database Module Methods

The `src/database.py` module provides these methods:

```python
# Load annual production data
df_annual = db.get_annual_production_data()

# Load production efficiency
df_efficiency = db.get_production_efficiency_data()

# Load water cut analysis
df_water_cut = db.get_water_cut_analysis_data()

# Load optimization candidates
df_optimization = db.get_optimization_candidates_data()

# Custom query execution
df_custom = db.fetch_dataframe(sql_query)
```

## Sample Data Creation

Here's SQL to create sample GOLD table data:

```sql
-- Sample data for gold_well_annual_production
INSERT INTO {catalog}.{schema}.gold_well_annual_production
SELECT 'Well-001' as wellbore_name, 2024 as year, 15000 as oil, 25000 as gas, 5000 as water, 
       30000 as gas_injection, 8000 as water_injection, 20000 as total_fluids, current_timestamp()
UNION ALL
SELECT 'Well-002', 2024, 12000, 20000, 8000, 25000, 6000, 20000, current_timestamp()
UNION ALL
SELECT 'Well-001', 2025, 14500, 24000, 5500, 32000, 8500, 20000, current_timestamp()
UNION ALL
SELECT 'Well-002', 2025, 11500, 19500, 8500, 26000, 6500, 20000, current_timestamp();
```

## Troubleshooting

### Connection Issues
1. Verify Databricks credentials in app.yaml are correct
2. Check token is not expired (regenerate if needed)
3. Ensure cluster is running and accessible
4. Validate host URL doesn't have trailing slashes

### Missing Data
1. Verify GOLD tables exist: `SHOW TABLES IN {catalog}.{schema};`
2. Check table schemas: `DESCRIBE TABLE {catalog}.{schema}.gold_well_annual_production;`
3. View sample data: `SELECT * FROM {catalog}.{schema}.gold_well_annual_production LIMIT 10;`

### Application Errors
1. Check app.yaml format (YAML syntax)
2. Verify environment variables are properly set
3. Look at Streamlit console for detailed error messages
4. Restart the Streamlit app after making changes

## Performance Tips

1. **Use caching** - App uses `@st.cache_data` for automatic result caching
2. **Partition by year** - GOLD tables are organized by year for faster queries
3. **Create indexes** on wellbore_name and year columns
4. **Use DBU autoscaling** for variable workloads

## Security Best Practices

1. **Never commit tokens** to git - use environment variables
2. **Rotate tokens regularly** - regenerate PAT every 90 days
3. **Use Unity Catalog** for fine-grained access control
4. **Enable audit logging** in Databricks workspace
5. **Use IP whitelisting** if available in your organization

## Next Steps

1. Create GOLD tables in Databricks with schemas provided above
2. Populate tables with production data (see Sample Data Creation)
3. Update app.yaml with your actual Databricks credentials
4. Run the app: `streamlit run app.py`
5. Navigate through dashboard pages to view GOLD layer analytics
6. Set up scheduled refreshes for GOLD tables from your source data
