"""
STEP 3: Feature Engineering - Create Vulnerability Factors
===========================================================
This script creates the individual factors that measure fragility:
- Flood Exposure
- Elevation Risk
- Road Access Weakness
- Population Vulnerability
- Facility Access

Run AFTER 02_merge_data.py
"""

import pandas as pd
import numpy as np
import os

print("=" * 60)
print("STEP 3: FEATURE ENGINEERING")
print("=" * 60)

# Load the combined data
print("\nLoading combined data...\n")
df = pd.read_csv('output/combined_data.csv')

print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}\n")

# ============================================================================
# PART 3A: Normalize Values to 0-100 Scale
# ============================================================================

print("--- PART 3A: Normalize Values to 0-100 Scale ---\n")

def normalize_feature(series, reverse=False):
    """
    Convert a column to 0-100 scale.
    
    Args:
        series: Pandas Series (column) to normalize
        reverse: If True, flip the scale (high values → low scores)
                 Use for "bad" metrics like elevation (low is bad)
    
    Returns:
        Normalized series with values 0-100
    """
    min_val = series.min()
    max_val = series.max()
    
    # Avoid division by zero
    if min_val == max_val:
        return pd.Series([50] * len(series), index=series.index)
    
    # Normalize to 0-1, then scale to 0-100
    normalized = (series - min_val) / (max_val - min_val) * 100
    
    if reverse:
        normalized = 100 - normalized
    
    return normalized

print("Normalization formula:")
print("  normalized = (value - min) / (max - min) * 100")
print("  If reverse=True: normalized = 100 - normalized")
print("  (Use reverse=True for 'bad' metrics like low elevation)\n")

# ============================================================================
# PART 3B: Feature 1 - Flood Exposure Score
# ============================================================================

print("--- PART 3B: Feature 1 - Flood Exposure ---\n")

print("Calculation:")
print("  - Start with existing Flood_Exposure_Score")
print("  - Add penalty for repeat flooding events")
print("  - Normalize to 0-100\n")

# Normalize the flood exposure score
df['Flood_Exposure_Norm'] = normalize_feature(df['Flood_Exposure_Score'])

# Add penalty for repeat flooding
# Each flooding event in 10 years adds 5 points
repeat_flood_penalty = df['Repeat_Flood_Events_10y'] * 5
df['Flood_Exposure_Norm'] = df['Flood_Exposure_Norm'] + repeat_flood_penalty

# Cap at 100
df['Flood_Exposure_Norm'] = df['Flood_Exposure_Norm'].clip(0, 100)

print("Flood Exposure Scores:")
print(df[['Zone_Name', 'Flood_Exposure_Score', 'Repeat_Flood_Events_10y', 'Flood_Exposure_Norm']])

# ============================================================================
# PART 3C: Feature 2 - Elevation Risk Score
# ============================================================================

print("\n--- PART 3C: Feature 2 - Elevation Risk ---\n")

print("Calculation:")
print("  - Higher elevation = safer (reverse=True)")
print("  - Areas below 5 feet are at critical risk\n")

# Normalize elevation (low elevation = high risk)
df['Elevation_Risk'] = normalize_feature(df['Elevation_ft'], reverse=True)

# Add critical penalty for very low elevations
df['Elevation_Risk'] = df['Elevation_Risk'].apply(
    lambda x: x if x < 90 else 100  # If below 5ft, score as 100
)

print("Elevation Risk Scores:")
print(df[['Zone_Name', 'Elevation_ft', 'Elevation_Risk']])

# ============================================================================
# PART 3D: Feature 3 - Road Access Weakness Score
# ============================================================================

print("\n--- PART 3D: Feature 3 - Road Access Weakness ---\n")

print("Calculation:")
print("  - Low accessibility = high risk")
print("  - Road elevation matters (low elevation roads can be cut off)\n")

# Assume we have road-related data (if not, we'll create a proxy)
if 'Avg_Facility_Accessibility' in df.columns:
    # Reverse: low accessibility = high weakness
    df['Road_Access_Weakness'] = normalize_feature(
        df['Avg_Facility_Accessibility'],
        reverse=True
    )
else:
    # If no facility data, create a proxy based on population + elevation
    df['Road_Access_Weakness'] = 50  # Default moderate risk

print("Road Access Weakness Scores:")
print(df[['Zone_Name', 'Avg_Facility_Accessibility', 'Road_Access_Weakness']])

# ============================================================================
# PART 3E: Feature 4 - Population Vulnerability Score
# ============================================================================

print("\n--- PART 3E: Feature 4 - Population Vulnerability ---\n")

print("Calculation:")
print("  - Vulnerable groups: elderly, children, poor")
print("  - Score = weighted sum of percentages\n")

# Vulnerability factors
age_vulnerability = df['Pct_Elderly'] + df['Pct_Children']  # Young & old need more help
poverty_vulnerability = df['Pct_Poverty'] * 1.5              # Poverty makes disasters worse

# Combine into population vulnerability score
df['Population_Vulnerability'] = (age_vulnerability + poverty_vulnerability) / 2

# Normalize to 0-100
df['Population_Vulnerability'] = normalize_feature(df['Population_Vulnerability'])

print("Population Vulnerability Scores:")
print(df[['Zone_Name', 'Pct_Elderly', 'Pct_Children', 'Pct_Poverty', 'Population_Vulnerability']])

# ============================================================================
# PART 3F: Feature 5 - Critical Facility Distance/Accessibility Score
# ============================================================================

print("\n--- PART 3F: Feature 5 - Facility Access Risk ---\n")

print("Calculation:")
print("  - Number of facilities (hospitals, shelters, schools)")
print("  - How accessible are they?\n")

if 'Num_Facilities' in df.columns and 'Avg_Facility_Accessibility' in df.columns:
    # Create facility access score
    # More facilities = better
    facility_count_norm = normalize_feature(df['Num_Facilities'])
    
    # Better accessibility = better
    facility_access_norm = df['Avg_Facility_Accessibility']
    
    # Low facility accessibility = high risk
    df['Facility_Access_Risk'] = 100 - (facility_count_norm + facility_access_norm) / 2
else:
    df['Facility_Access_Risk'] = 50  # Default moderate risk

print("Facility Access Risk Scores:")
print(df[['Zone_Name', 'Num_Facilities', 'Avg_Facility_Accessibility', 'Facility_Access_Risk']])

# ============================================================================
# PART 3G: Create Summary of All Features
# ============================================================================

print("\n--- PART 3G: Summary of All Features ---\n")

features_to_show = [
    'Zone_Name',
    'Flood_Exposure_Norm',
    'Elevation_Risk',
    'Road_Access_Weakness',
    'Population_Vulnerability',
    'Facility_Access_Risk'
]

print("All vulnerability features (0-100 scale, higher = more fragile):")
print(df[features_to_show].to_string())

# ============================================================================
# KEY STATISTICS FOR EACH FEATURE
# ============================================================================

print("\n--- Feature Statistics ---\n")

for feature in ['Flood_Exposure_Norm', 'Elevation_Risk', 'Road_Access_Weakness', 
                'Population_Vulnerability', 'Facility_Access_Risk']:
    print(f"\n{feature}:")
    print(f"  Mean: {df[feature].mean():.1f}")
    print(f"  Min:  {df[feature].min():.1f}")
    print(f"  Max:  {df[feature].max():.1f}")

# Save feature data
os.makedirs('output', exist_ok=True)
df.to_csv('output/features_engineered.csv', index=False)

print("\n✓ Feature-engineered data saved to: output/features_engineered.csv")

# ============================================================================
# KEY CONCEPTS FOR BEGINNERS
# ============================================================================

print("\n" + "=" * 60)
print("KEY CONCEPTS FOR FEATURE ENGINEERING")
print("=" * 60)

print("""
1. NORMALIZATION:
   - Scale different measurements to same 0-100 range
   - Allows fair comparison (e.g., elevation vs population %)
   - Formula: (value - min) / (max - min) * 100

2. REVERSE NORMALIZATION:
   - For "bad" metrics: low elevation = high risk
   - Solution: flip the scale (100 - normalized)

3. FEATURE COMBINATIONS:
   - Combine related metrics (age% + poverty% = vulnerability)
   - Weight them if some are more important
   - Average, sum, or multiply based on logic

4. DOMAIN KNOWLEDGE:
   - Why include each feature? (elevation matters for floods!)
   - How do factors interact? (poor areas need more help)
   - What's the range? (elevation 0-20ft, population %: 0-100%)

5. FEATURES ARE RAW INPUTS:
   - Next step: combine them into ONE fragility score
   - Weights determine relative importance
""")

print("\n✓ STEP 3 COMPLETE!")
print("Next: Run '04_calculate_fragility_score.py' to combine features\n")
