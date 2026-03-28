"""
STEP 1: Load and Explore Data
=============================
This script shows how to load different data types and explore them.

Run this FIRST to understand your data structure.
"""

import pandas as pd
import numpy as np
import os

print("=" * 60)
print("STEP 1: LOADING & EXPLORING DATA")
print("=" * 60)

# ============================================================================
# PART 1A: Loading CSV Files (Census Data, etc.)
# ============================================================================

print("\n--- PART 1A: Loading CSV Files ---\n")

# Example 1: Load a CSV file with population data
# (We'll create sample data if file doesn't exist)

csv_file = "data/sample_census_data.csv"

if os.path.exists(csv_file):
    print(f"Loading {csv_file}...")
    df_census = pd.read_csv(csv_file)
else:
    print(f"File {csv_file} not found. Creating sample data...")
    # Create sample census data for demonstration
    df_census = pd.DataFrame({
        'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
        'Zone_Name': ['Downtown Tampa', 'Ybor City', 'South Tampa', 'North Tampa', 'East Tampa'],
        'Population': [15000, 8500, 12000, 20000, 18000],
        'Median_Income': [65000, 45000, 75000, 55000, 42000],
        'Pct_Elderly': [12, 8, 18, 10, 9],
        'Pct_Children': [14, 12, 8, 16, 15],
        'Pct_Poverty': [18, 32, 8, 22, 35]
    })
    print("✓ Sample census data created\n")

print("First few rows of census data:")
print(df_census.head())

print("\nData shape (rows, columns):", df_census.shape)
print("\nColumn names and types:")
print(df_census.info())

print("\nBasic statistics:")
print(df_census.describe())

# ============================================================================
# PART 1B: Handling Missing Data
# ============================================================================

print("\n--- PART 1B: Handling Missing Data ---\n")

# Check for missing values
print("Missing values in each column:")
print(df_census.isnull().sum())

# Drop rows with missing critical columns
df_census_clean = df_census.dropna(subset=['Zone_ID', 'Population'])

# Fill missing values with median (for numeric columns)
df_census_clean['Pct_Elderly'] = df_census_clean['Pct_Elderly'].fillna(
    df_census_clean['Pct_Elderly'].median()
)

print("\nAfter cleaning - missing values:")
print(df_census_clean.isnull().sum())

# ============================================================================
# PART 1C: Loading Multiple Data Types
# ============================================================================

print("\n--- PART 1C: Creating & Loading Multiple Datasets ---\n")

# Create flood zone data
df_flood = pd.DataFrame({
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Flood_Zone': ['AE', 'X', 'AE', 'A', 'AE'],
    'Elevation_ft': [4.2, 7.1, 2.1, 5.5, 1.8],
    'Flood_Exposure_Score': [85, 25, 92, 65, 95],
    'Repeat_Flood_Events_10y': [3, 0, 8, 1, 12]
})

print("Flood Zone Data:")
print(df_flood.head())

# Create road/infrastructure data
df_roads = pd.DataFrame({
    'Zone_ID': ['Z001', 'Z001', 'Z002', 'Z003', 'Z004', 'Z005', 'Z005'],
    'Road_ID': ['R101', 'R102', 'R103', 'R104', 'R105', 'R106', 'R107'],
    'Road_Type': ['Highway', 'Primary', 'Primary', 'Secondary', 'Highway', 'Secondary', 'Secondary'],
    'Elevation_ft': [6.0, 3.5, 8.2, 2.1, 7.0, 1.5, 2.0],
    'Flood_Risk_Level': ['High', 'Medium', 'Low', 'High', 'Low', 'Critical', 'High']
})

print("\nRoad/Infrastructure Data:")
print(df_roads.head())

# Create facility access data (hospitals, shelters, schools)
df_facilities = pd.DataFrame({
    'Facility_ID': ['F001', 'F002', 'F003', 'F004', 'F005'],
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Facility_Type': ['Hospital', 'School', 'Shelter', 'Hospital', 'School'],
    'Accessibility_Score': [95, 70, 85, 90, 60],  # 0-100, higher = easier to reach
    'Elevation_ft': [8.5, 4.2, 5.0, 7.5, 3.1]
})

print("\nFacility Data:")
print(df_facilities.head())

# ============================================================================
# PART 1D: Save Sample Data for Later Use
# ============================================================================

print("\n--- PART 1D: Saving Sample Data ---\n")

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Save all datasets
df_census_clean.to_csv('data/sample_census_data.csv', index=False)
df_flood.to_csv('data/sample_flood_data.csv', index=False)
df_roads.to_csv('data/sample_roads_data.csv', index=False)
df_facilities.to_csv('data/sample_facilities_data.csv', index=False)

print("✓ Sample data saved to 'data/' folder:")
print("  - sample_census_data.csv")
print("  - sample_flood_data.csv")
print("  - sample_roads_data.csv")
print("  - sample_facilities_data.csv")

# ============================================================================
# KEY CONCEPTS FOR BEGINNERS
# ============================================================================

print("\n" + "=" * 60)
print("KEY CONCEPTS")
print("=" * 60)

print("""
1. DATAFRAME: A table with rows and columns (like Excel)
   - Each row = one geographic unit (zone)
   - Each column = one attribute (population, elevation, etc.)

2. ZONE_ID: The "glue" that connects all datasets
   - Use it to merge different datasets together
   - Must be consistent across all files

3. MISSING VALUES (NaN):
   - Drop rows if critical data is missing
   - Fill missing values with median or mean for numeric data

4. NUMERIC vs CATEGORICAL:
   - Numeric: numbers (Population, Elevation)
   - Categorical: text/categories (Zone_Name, Flood_Zone, Road_Type)

5. DESCRIBE():
   - Shows mean, median, min, max for numeric columns
   - Helps you understand data distribution
""")

print("\n✓ STEP 1 COMPLETE!")
print("Next: Run '02_merge_data.py' to combine datasets by Zone_ID\n")
