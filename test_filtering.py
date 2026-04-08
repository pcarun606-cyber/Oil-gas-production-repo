"""Test the NULL string filtering logic"""
import pandas as pd
import numpy as np

# Simulate data from Databricks - mix of real nulls and string 'nan'
test_data = {
    'wellbore_name': ['Well-1', 'nan', 'Well-3', None, 'Well-5'],
    'year': [2020, 'nan', 2022, 2023, 2024],
    'oil': [100.5, np.nan, 150.2, np.nan, 200.0],
    'gas': [50.2, np.nan, 75.1, 80.0, np.nan],
}

df = pd.DataFrame(test_data)
df_original = df.copy()

print("=" * 80)
print("ORIGINAL DATA:")
print("=" * 80)
print(df)
print(f"\nOriginal shape: {df.shape}")
print()

# Apply the filtering logic from database.py
print("=" * 80)
print("APPLYING FILTERING LOGIC:")
print("=" * 80)

# First, replace string 'nan' with actual NaN for all columns
df = df.replace({'nan': None})
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].apply(lambda x: None if isinstance(x, str) and x.lower() == 'nan' else x)

print("After replacing string 'nan' with None:")
print(df)
print()

# Identify key columns
key_columns = []
for col in df.columns:
    if col.lower() in ['wellbore_name', 'well_name', 'well_id', 'name', 'id', 'wellbore']:
        key_columns.append(col)

print(f"Key columns identified: {key_columns}")
print()

if key_columns:
    df_before = len(df)
    df = df.dropna(subset=key_columns)
    df_after = len(df)
    removed = df_before - df_after
    print(f"Filtered from {df_before} rows to {df_after} valid rows (removed {removed} rows)")
else:
    print("No key columns found!")

print()
print("=" * 80)
print("FILTERED DATA:")
print("=" * 80)
print(df)
print(f"\nFinal shape: {df.shape}")

print()
print("=" * 80)
print("RESULT:")
print("=" * 80)
print(f"✅ Successfully filtered out {df_original.shape[0] - df.shape[0]} rows with NULL/missing wellbore_name")
print(f"📊 Kept {df.shape[0]} rows with valid data")
