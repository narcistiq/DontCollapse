"""
STEP 2: Combine Datasets by Location (Zone_ID)
================================================
This script shows how to merge different datasets using a common geographic key.

Run AFTER 01_load_data.py (it creates the sample data files).
"""

import pandas as pd
import os

print("=" * 60)
print("STEP 2: COMBINING DATASETS BY LOCATION")
print("=" * 60)

# Load the sample data created in Step 1
print("\nLoading data files...\n")

df_census = pd.read_csv('data/sample_census_data.csv')
df_flood = pd.read_csv('data/sample_flood_data.csv')
df_facilities = pd.read_csv('data/sample_facilities_data.csv')

print("Datasets loaded:")
print(f"  - Census data: {len(df_census)} zones")
print(f"  - Flood data: {len(df_flood)} zones")
print(f"  - Facilities data: {len(df_facilities)} records")

# ============================================================================
# PART 2A: Understanding Merge Operations
# ============================================================================

print("\n--- PART 2A: Understanding Merge (Join) ---\n")

print("""
MERGE (JOIN) combines two tables based on a common column (Zone_ID).

Merge Types:
1. INNER JOIN: Keep only zones present in BOTH tables
   → Lose data if one table doesn't have all zones
   
2. LEFT JOIN: Keep all zones from the LEFT table
   → Add NULL for missing values from right table
   
3. OUTER JOIN: Keep all zones from BOTH tables
   → Add NULL where data is missing
   
For our use case: Use LEFT JOIN
  - Start with census (our main zones)
  - Add flood, road, and facility data
  - If data is missing, we'll handle it later
""")

# ============================================================================
# PART 2B: Merge Census + Flood Data
# ============================================================================

print("\n--- PART 2B: Merge Census + Flood Data ---\n")

# First merge: Census (left) + Flood (right)
df_merged = df_census.merge(
    df_flood,
    on='Zone_ID',           # Column to match on
    how='left'              # Keep all zones from census
)

print("Result of merging Census + Flood:")
print(df_merged.head())
print(f"\nShape after first merge: {df_merged.shape}")

# ============================================================================
# PART 2C: Handle Missing Values After Merge
# ============================================================================

print("\n--- PART 2C: Handling Missing Values ---\n")

print("Missing values after first merge:")
print(df_merged.isnull().sum())

# For numeric columns, fill with median
numeric_cols = df_merged.select_dtypes(include=['float64', 'int64']).columns

for col in numeric_cols:
    if df_merged[col].isnull().sum() > 0:
        median_val = df_merged[col].median()
        df_merged[col].fillna(median_val, inplace=True)
        print(f"  Filled {col} with median: {median_val}")

# For categorical columns, fill with 'Unknown'
categorical_cols = df_merged.select_dtypes(include=['object']).columns

for col in categorical_cols:
    if df_merged[col].isnull().sum() > 0:
        df_merged[col].fillna('Unknown', inplace=True)
        print(f"  Filled {col} with 'Unknown'")

print("\nMissing values after filling:")
print(df_merged.isnull().sum())

# ============================================================================
# PART 2D: Aggregate Facility Data (Multiple Facilities per Zone)
# ============================================================================

print("\n--- PART 2D: Aggregate Multi-Record Data ---\n")

print("Challenge: Some zones have multiple facilities/roads")
print("Solution: Aggregate them into single values per zone\n")

# Group by Zone_ID and aggregate
df_facilities_agg = df_facilities.groupby('Zone_ID').agg({
    'Facility_ID': 'count',                    # How many facilities?
    'Accessibility_Score': 'mean',             # Average accessibility
    'Elevation_ft': 'min'                      # Minimum elevation (most vulnerable)
}).reset_index()

# Rename columns for clarity
df_facilities_agg.rename(columns={
    'Facility_ID': 'Num_Facilities',
    'Accessibility_Score': 'Avg_Facility_Accessibility',
    'Elevation_ft': 'Min_Facility_Elevation'
}, inplace=True)

print("Aggregated facility data (by zone):")
print(df_facilities_agg)

# ============================================================================
# PART 2E: Final Merge - Combine Everything
# ============================================================================

print("\n--- PART 2E: Final Complete Merge ---\n")

# Merge facilities into main dataset
df_merged = df_merged.merge(
    df_facilities_agg,
    on='Zone_ID',
    how='left'
)

print("Final merged dataset (all data combined by Zone_ID):")
print(df_merged.head())

print(f"\nFinal shape: {df_merged.shape}")
print(f"Columns: {list(df_merged.columns)}")

# ============================================================================
# PART 2F: Verify and Save Combined Data
# ============================================================================

print("\n--- PART 2F: Data Quality Check ---\n")

# Check for remaining missing values
print("Remaining missing values:")
print(df_merged.isnull().sum())

# Handle any remaining NaNs
df_merged = df_merged.fillna(0)

print("\nAfter filling remaining NaNs:")
print(df_merged.isnull().sum())

# Show basic statistics
print("\nBasic statistics of combined dataset:")
print(df_merged.describe())

# Save combined dataset
os.makedirs('output', exist_ok=True)
df_merged.to_csv('output/combined_data.csv', index=False)

print("\n✓ Combined dataset saved to: output/combined_data.csv")

# ============================================================================
# KEY CONCEPTS FOR BEGINNERS
# ============================================================================

print("\n" + "=" * 60)
print("KEY CONCEPTS FOR MERGING")
print("=" * 60)

print("""
1. MERGE ON ZONE_ID:
   - Zone_ID is the "key" that connects all datasets
   - Both tables must have Zone_ID column
   - Values must match exactly (case-sensitive!)

2. JOIN TYPES:
   - LEFT: Keep all zones from first (left) table
   - INNER: Keep only zones in both tables
   - OUTER: Keep all zones from both tables

3. AGGREGATION:
   - When multiple records per zone (like many roads in one zone)
   - Aggregate them: count, mean, min, max, sum
   - Creates one row per zone for merging

4. MISSING VALUES (NaN):
   - Appear after merge if one table lacks data for a zone
   - Fill with: median (numeric), 'Unknown' (text), or 0 (counts)

5. COLUMN NAMING:
   - Use clear names: 'Avg_Facility_Accessibility' not 'Acc_Fac_Avg'
   - Makes later steps easier to understand
""")

print("\n✓ STEP 2 COMPLETE!")
print("Next: Run '03_feature_engineering.py' to create fragility features\n")
