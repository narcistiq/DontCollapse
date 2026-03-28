"""
MASTER TABLE BUILDER - Flood Fragility Project
==============================================
This script creates a complete master table with all vulnerability factors
and a final fragility score. Starts simple and builds up step by step.
"""

import pandas as pd
import numpy as np
import os

print("=" * 80)
print("BUILDING MASTER FLOOD FRAGILITY TABLE")
print("=" * 80)

# ============================================================================
# STEP 1: Start with Basic Zone Data
# ============================================================================

print("\n--- STEP 1: START WITH BASIC ZONE DATA ---\n")

# Create or load basic zone information
zones_data = {
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Zone_Name': ['Downtown Tampa', 'Ybor City', 'South Tampa', 'North Tampa', 'East Tampa'],
    'Population': [15000, 8500, 12000, 20000, 18000],
    'Area_sq_miles': [2.1, 1.8, 3.2, 4.5, 2.9]
}

df_master = pd.DataFrame(zones_data)

print("Starting master table:")
print(df_master.to_string())
print(f"\nShape: {df_master.shape} (rows × columns)")

# ============================================================================
# STEP 2: Add Flood Exposure Factor
# ============================================================================

print("\n--- STEP 2: ADD FLOOD EXPOSURE FACTOR ---\n")

# Flood exposure data (0-100 scale, higher = more exposed)
flood_data = {
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Flood_Exposure': [85, 25, 92, 65, 95],  # Based on FEMA flood maps
    'Flood_Events_Last_10y': [3, 0, 8, 1, 12]  # Historical flood frequency
}

df_flood = pd.DataFrame(flood_data)

# Merge flood data into master table
df_master = df_master.merge(df_flood, on='Zone_ID', how='left')

print("Added flood exposure:")
print(df_master[['Zone_ID', 'Zone_Name', 'Flood_Exposure', 'Flood_Events_Last_10y']].to_string())

# ============================================================================
# STEP 3: Add Elevation Risk Factor
# ============================================================================

print("\n--- STEP 3: ADD ELEVATION RISK FACTOR ---\n")

# Elevation data (feet above sea level)
elevation_data = {
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Avg_Elevation_ft': [4.2, 7.1, 2.1, 5.5, 1.8],
    'Min_Elevation_ft': [2.1, 5.8, 0.8, 3.2, 0.5]  # Lowest point in zone
}

df_elevation = pd.DataFrame(elevation_data)

# Merge elevation data
df_master = df_master.merge(df_elevation, on='Zone_ID', how='left')

# Calculate elevation risk (lower elevation = higher risk)
# Risk = 100 - (elevation * 10), so 5ft = 50 risk, 0ft = 100 risk
df_master['Elevation_Risk'] = 100 - (df_master['Avg_Elevation_ft'] * 10)
df_master['Elevation_Risk'] = df_master['Elevation_Risk'].clip(0, 100)

print("Added elevation risk:")
print(df_master[['Zone_ID', 'Zone_Name', 'Avg_Elevation_ft', 'Min_Elevation_ft', 'Elevation_Risk']].to_string())

# ============================================================================
# STEP 4: Add Road Access Risk Factor
# ============================================================================

print("\n--- STEP 4: ADD ROAD ACCESS RISK FACTOR ---\n")

# Road network data
road_data = {
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Total_Road_Miles': [45, 38, 52, 67, 41],
    'Flooded_Road_Miles': [12, 2, 18, 8, 22],  # Roads that flood
    'Major_Evacuation_Routes': [2, 3, 1, 4, 1]  # Number of safe evacuation routes
}

df_roads = pd.DataFrame(road_data)

# Merge road data
df_master = df_master.merge(df_roads, on='Zone_ID', how='left')

# Calculate road access risk
# Higher risk if many roads flood or few evacuation routes
df_master['Road_Flood_Percent'] = (df_master['Flooded_Road_Miles'] / df_master['Total_Road_Miles'] * 100)
df_master['Road_Access_Risk'] = df_master['Road_Flood_Percent'] + (5 - df_master['Major_Evacuation_Routes']) * 10
df_master['Road_Access_Risk'] = df_master['Road_Access_Risk'].clip(0, 100)

print("Added road access risk:")
print(df_master[['Zone_ID', 'Zone_Name', 'Road_Flood_Percent', 'Major_Evacuation_Routes', 'Road_Access_Risk']].to_string())

# ============================================================================
# STEP 5: Add Shelter Distance Factor
# ============================================================================

print("\n--- STEP 5: ADD SHELTER DISTANCE FACTOR ---\n")

# Shelter access data
shelter_data = {
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Nearest_Shelter_Distance_miles': [0.8, 1.2, 2.1, 1.5, 3.2],
    'Shelter_Capacity_People': [2500, 1800, 3200, 4100, 2800],
    'Shelters_Within_5miles': [3, 2, 1, 4, 1]
}

df_shelters = pd.DataFrame(shelter_data)

# Merge shelter data
df_master = df_master.merge(df_shelters, on='Zone_ID', how='left')

# Calculate shelter access risk
# Higher risk if far from shelter or insufficient capacity
df_master['Shelter_Distance_Risk'] = df_master['Nearest_Shelter_Distance_miles'] * 15  # 1 mile = 15 risk points
df_master['Shelter_Capacity_Risk'] = 100 - (df_master['Shelter_Capacity_People'] / df_master['Population'] * 100)
df_master['Shelter_Capacity_Risk'] = df_master['Shelter_Capacity_Risk'].clip(0, 100)

# Combined shelter risk
df_master['Shelter_Access_Risk'] = (df_master['Shelter_Distance_Risk'] + df_master['Shelter_Capacity_Risk']) / 2
df_master['Shelter_Access_Risk'] = df_master['Shelter_Access_Risk'].clip(0, 100)

print("Added shelter access risk:")
print(df_master[['Zone_ID', 'Zone_Name', 'Nearest_Shelter_Distance_miles', 'Shelter_Capacity_People', 'Shelter_Access_Risk']].to_string())

# ============================================================================
# STEP 6: Add Social Vulnerability Factor
# ============================================================================

print("\n--- STEP 6: ADD SOCIAL VULNERABILITY FACTOR ---\n")

# Social vulnerability data
social_data = {
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Pct_Elderly_65plus': [12, 8, 18, 10, 9],
    'Pct_Children_Under5': [8, 6, 4, 9, 11],
    'Pct_Below_Poverty': [18, 32, 8, 22, 35],
    'Pct_No_Vehicle': [15, 28, 6, 19, 31],
    'Pct_Limited_English': [8, 12, 3, 6, 14]
}

df_social = pd.DataFrame(social_data)

# Merge social data
df_master = df_master.merge(df_social, on='Zone_ID', how='left')

# Calculate social vulnerability score
# Combine multiple social factors
df_master['Social_Vulnerability'] = (
    df_master['Pct_Elderly_65plus'] * 1.5 +      # Elderly need more help
    df_master['Pct_Children_Under5'] * 1.5 +     # Children need more help
    df_master['Pct_Below_Poverty'] * 1.2 +       # Poverty reduces resilience
    df_master['Pct_No_Vehicle'] * 1.0 +          # No car = harder to evacuate
    df_master['Pct_Limited_English'] * 0.8       # Language barriers
)

# Normalize to 0-100 scale
max_social = df_master['Social_Vulnerability'].max()
min_social = df_master['Social_Vulnerability'].min()
if max_social > min_social:
    df_master['Social_Vulnerability'] = (
        (df_master['Social_Vulnerability'] - min_social) /
        (max_social - min_social) * 100
    )

print("Added social vulnerability:")
print(df_master[['Zone_ID', 'Zone_Name', 'Pct_Elderly_65plus', 'Pct_Below_Poverty', 'Pct_No_Vehicle', 'Social_Vulnerability']].to_string())

# ============================================================================
# STEP 7: Add Power Infrastructure Risk Factor
# ============================================================================

print("\n--- STEP 7: ADD POWER INFRASTRUCTURE RISK FACTOR ---\n")

# Power infrastructure data
power_data = {
    'Zone_ID': ['Z001', 'Z002', 'Z003', 'Z004', 'Z005'],
    'Power_Substations': [2, 1, 0, 1, 0],
    'Power_Plants': [2, 0, 0, 0, 0],  # Number of power plants in zone
    'Critical_Power_Elevation_ft': [3.1, 4.5, 999, 8.5, 999],  # Elevation of critical power facilities (999 = none)
    'Backup_Power_Capacity': [25, 15, 5, 35, 10]  # Percent of critical facilities with backup power
}

df_power = pd.DataFrame(power_data)

# Merge power data
df_master = df_master.merge(df_power, on='Zone_ID', how='left')

# Calculate power risk
# Higher risk if critical power facilities are low elevation or lack backup
df_master['Power_Elevation_Risk'] = df_master['Critical_Power_Elevation_ft'].apply(
    lambda x: 100 - (x * 10) if x < 100 else 0  # 999 becomes 0 risk
)
df_master['Power_Elevation_Risk'] = df_master['Power_Elevation_Risk'].clip(0, 100)

df_master['Power_Backup_Risk'] = 100 - df_master['Backup_Power_Capacity']

# Combined power risk
df_master['Power_Infrastructure_Risk'] = (
    df_master['Power_Elevation_Risk'] * 0.7 +    # Elevation more important
    df_master['Power_Backup_Risk'] * 0.3
)

print("Added power infrastructure risk:")
print(df_master[['Zone_ID', 'Zone_Name', 'Power_Substations', 'Power_Plants', 'Critical_Power_Elevation_ft', 'Power_Infrastructure_Risk']].to_string())

# ============================================================================
# STEP 8: Calculate Final Fragility Score
# ============================================================================

print("\n--- STEP 8: CALCULATE FINAL FRAGILITY SCORE ---\n")

# Define weights for each factor (must sum to 1.0)
fragility_weights = {
    'Flood_Exposure': 0.30,          # Most important - direct flood impact
    'Elevation_Risk': 0.20,          # Fundamental vulnerability
    'Road_Access_Risk': 0.15,        # Can people evacuate?
    'Shelter_Access_Risk': 0.15,     # Can people find safety?
    'Social_Vulnerability': 0.10,    # Who is most affected?
    'Power_Infrastructure_Risk': 0.10 # Critical services availability
}

print("Fragility Score Weights:")
for factor, weight in fragility_weights.items():
    print(f"  {factor}: {weight*100:.0f}%")
print(f"  Total: {sum(fragility_weights.values())*100:.0f}%")

# Calculate weighted fragility score
df_master['Fragility_Score'] = (
    df_master['Flood_Exposure'] * fragility_weights['Flood_Exposure'] +
    df_master['Elevation_Risk'] * fragility_weights['Elevation_Risk'] +
    df_master['Road_Access_Risk'] * fragility_weights['Road_Access_Risk'] +
    df_master['Shelter_Access_Risk'] * fragility_weights['Shelter_Access_Risk'] +
    df_master['Social_Vulnerability'] * fragility_weights['Social_Vulnerability'] +
    df_master['Power_Infrastructure_Risk'] * fragility_weights['Power_Infrastructure_Risk']
)

# Round to 1 decimal place
df_master['Fragility_Score'] = df_master['Fragility_Score'].round(1)

# Add risk category
def get_risk_category(score):
    if score >= 75:
        return 'CRITICAL'
    elif score >= 60:
        return 'HIGH'
    elif score >= 40:
        return 'MODERATE'
    elif score >= 25:
        return 'LOW'
    else:
        return 'MINIMAL'

df_master['Risk_Category'] = df_master['Fragility_Score'].apply(get_risk_category)

# Add ranking
df_master['Fragility_Rank'] = df_master['Fragility_Score'].rank(ascending=False, method='min').astype(int)

print("Final fragility scores:")
ranking_cols = ['Fragility_Rank', 'Zone_ID', 'Zone_Name', 'Fragility_Score', 'Risk_Category']
print(df_master[ranking_cols].sort_values('Fragility_Rank').to_string())

# ============================================================================
# STEP 9: Create Final Master Table
# ============================================================================

print("\n--- STEP 9: CREATE FINAL MASTER TABLE ---\n")

# Select columns for the final master table
master_columns = [
    'Zone_ID', 'Zone_Name', 'Population', 'Area_sq_miles',
    'Flood_Exposure', 'Elevation_Risk', 'Road_Access_Risk',
    'Shelter_Access_Risk', 'Social_Vulnerability', 'Power_Infrastructure_Risk',
    'Fragility_Score', 'Risk_Category', 'Fragility_Rank'
]

df_final_master = df_master[master_columns].copy()

print("FINAL MASTER TABLE:")
print("=" * 120)
print(df_final_master.to_string())
print("=" * 120)

# ============================================================================
# STEP 10: Save Master Table
# ============================================================================

print("\n--- STEP 10: SAVE MASTER TABLE ---\n")

os.makedirs('output', exist_ok=True)
df_final_master.to_csv('output/master_fragility_table.csv', index=False)

print("✓ Master table saved to: output/master_fragility_table.csv")

# Also save the full detailed table
df_master.to_csv('output/master_fragility_table_detailed.csv', index=False)
print("✓ Detailed master table saved to: output/master_fragility_table_detailed.csv")

# ============================================================================
# STEP 11: Summary Statistics
# ============================================================================

print("\n--- STEP 11: SUMMARY STATISTICS ---\n")

print("Fragility Score Distribution:")
print(f"  Average: {df_final_master['Fragility_Score'].mean():.1f}")
print(f"  Highest: {df_final_master['Fragility_Score'].max():.1f} ({df_final_master.loc[df_final_master['Fragility_Score'].idxmax(), 'Zone_Name']})")
print(f"  Lowest:  {df_final_master['Fragility_Score'].min():.1f} ({df_final_master.loc[df_final_master['Fragility_Score'].idxmin(), 'Zone_Name']})")

print(f"\nRisk Category Breakdown:")
for category in ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
    count = len(df_final_master[df_final_master['Risk_Category'] == category])
    if count > 0:
        print(f"  {category}: {count} zones")

print(f"\nFactor Correlations with Fragility Score:")
factors = ['Flood_Exposure', 'Elevation_Risk', 'Road_Access_Risk',
           'Shelter_Access_Risk', 'Social_Vulnerability', 'Power_Infrastructure_Risk']
for factor in factors:
    correlation = df_final_master[factor].corr(df_final_master['Fragility_Score'])
    print(f"  {factor}: {correlation:.2f}")

# ============================================================================
# KEY CONCEPTS FOR BEGINNERS
# ============================================================================

print("\n" + "=" * 80)
print("HOW TO BUILD YOUR OWN MASTER TABLE")
print("=" * 80)

print("""
1. START SIMPLE:
   - Create DataFrame with zone names and IDs
   - Add one factor at a time

2. MERGE PATTERN:
   df_master = df_master.merge(new_data, on='Zone_ID', how='left')

3. CALCULATE RISK SCORES:
   - Convert raw data to 0-100 risk scale
   - Higher number = higher risk
   - Use formulas like: risk = 100 - (good_thing * multiplier)

4. WEIGHTED SCORE:
   - fragility = (factor1 * weight1) + (factor2 * weight2) + ...
   - Weights must sum to 1.0 (or 100%)
   - Adjust weights based on what matters most

5. YOUR DATA SOURCES:
   - FEMA: Flood exposure maps
   - USGS: Elevation data
   - Census: Social vulnerability
   - Local GIS: Roads, shelters, power infrastructure

6. CUSTOMIZE WEIGHTS:
   - If floods are your biggest concern: increase Flood_Exposure weight
   - If evacuation is critical: increase Road_Access_Risk weight
   - If vulnerable populations matter most: increase Social_Vulnerability weight
""")

print("\n✓ MASTER TABLE COMPLETE!")
print("Use 'output/master_fragility_table.csv' for your analysis and maps!")
print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)

print("""
1. Open master_fragility_table.csv in Excel/Google Sheets
2. Sort by Fragility_Score to see most vulnerable zones first
3. Create charts showing factor contributions
4. Use for mapping (Fragility_Score as color intensity)
5. Share with stakeholders for decision-making

The table has everything you need:
- One row per zone
- All vulnerability factors
- Final fragility score
- Risk categories and rankings
""")
