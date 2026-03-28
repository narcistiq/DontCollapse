"""
STEP 4: Calculate Fragility Score & Generate Results
====================================================
This script combines all vulnerability features into a single
"Fragility Score" and generates insights.

Run AFTER 03_feature_engineering.py
"""

import pandas as pd
import numpy as np
import os

print("=" * 60)
print("STEP 4: FRAGILITY SCORE CALCULATION")
print("=" * 60)

# Load the feature-engineered data
print("\nLoading feature data...\n")
df = pd.read_csv('output/features_engineered.csv')

print(f"Dataset: {len(df)} zones")
print(f"Features available: {list(df.columns)}\n")

# ============================================================================
# PART 4A: Simple Fragility Score (Equal Weights)
# ============================================================================

print("--- PART 4A: Simple Fragility Score ---\n")

print("Method: Average of all 5 vulnerability features")
print("Assumption: All factors equally important\n")

features = [
    'Flood_Exposure_Norm',
    'Elevation_Risk',
    'Road_Access_Weakness',
    'Population_Vulnerability',
    'Facility_Access_Risk'
]

# Calculate simple average
df['Fragility_Score_Simple'] = df[features].mean(axis=1)

print("Simple Fragility Scores:")
print(df[['Zone_Name', 'Fragility_Score_Simple']])

# ============================================================================
# PART 4B: Weighted Fragility Score (Realistic Weights)
# ============================================================================

print("\n--- PART 4B: Weighted Fragility Score ---\n")

print("Method: Weighted sum of features")
print("Weights (based on flood-severity impact):\n")

# Define weights (must sum to 1.0)
weights = {
    'Flood_Exposure_Norm': 0.35,           # Flood exposure is PRIMARY factor (35%)
    'Elevation_Risk': 0.25,                # Elevation is second (25%)
    'Population_Vulnerability': 0.20,      # Who is at risk? (20%)
    'Facility_Access_Risk': 0.15,          # Can people evacuate? (15%)
    'Road_Access_Weakness': 0.05           # How good are roads? (5%)
}

for feature, weight in weights.items():
    print(f"  {feature}: {weight*100:.0f}%")

print(f"\n  Total: {sum(weights.values())*100:.0f}%")

# Calculate weighted score
df['Fragility_Score'] = 0.0
for feature, weight in weights.items():
    df['Fragility_Score'] += df[feature] * weight

# Round to 1 decimal
df['Fragility_Score'] = df['Fragility_Score'].round(1)

print("\n\nWeighted Fragility Scores:")
print(df[['Zone_Name', 'Fragility_Score']].sort_values('Fragility_Score', ascending=False))

# ============================================================================
# PART 4C: Risk Categorization
# ============================================================================

print("\n--- PART 4C: Categorize Risk Levels ---\n")

def categorize_risk(score):
    """Classify fragility score into risk categories"""
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

df['Risk_Category'] = df['Fragility_Score'].apply(categorize_risk)

print("Risk Categories:")
print("""
  CRITICAL (75-100): Immediate action needed
  HIGH     (60-75):  Urgent attention required
  MODERATE (40-60):  Planning needed
  LOW      (25-40):  Monitor situation
  MINIMAL  (0-25):   Currently safe
""")

print("\nZones by Risk Category:")
for category in ['CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
    zones = df[df['Risk_Category'] == category]['Zone_Name'].tolist()
    if zones:
        print(f"\n{category}:")
        for zone in zones:
            score = df[df['Zone_Name'] == zone]['Fragility_Score'].values[0]
            print(f"  - {zone}: {score}")

# ============================================================================
# PART 4D: Rankings
# ============================================================================

print("\n--- PART 4D: Ranking Zones by Fragility ---\n")

# Rank from most fragile to most resilient
df['Fragility_Rank'] = df['Fragility_Score'].rank(ascending=False, method='min').astype(int)

ranking_display = df[['Fragility_Rank', 'Zone_Name', 'Fragility_Score', 'Risk_Category']].sort_values('Fragility_Rank')

print("PRIORITY RANKING (Most Fragile → Most Resilient):")
print(ranking_display.to_string())

# ============================================================================
# PART 4E: Component Breakdown per Zone
# ============================================================================

print("\n--- PART 4E: What Makes Each Zone Fragile? ---\n")

print("For each zone, show which factors contribute to fragility:\n")

for idx, row in df.iterrows():
    zone_name = row['Zone_Name']
    rank = int(row['Fragility_Rank'])
    score = row['Fragility_Score']
    
    print(f"\n#{rank}: {zone_name} (Score: {score})")
    print("-" * 50)
    
    # Show component scores
    components = {
        'Flood Exposure': row['Flood_Exposure_Norm'] * weights['Flood_Exposure_Norm'],
        'Elevation Risk': row['Elevation_Risk'] * weights['Elevation_Risk'],
        'Population Vulnerability': row['Population_Vulnerability'] * weights['Population_Vulnerability'],
        'Facility Access Risk': row['Facility_Access_Risk'] * weights['Facility_Access_Risk'],
        'Road Access Weakness': row['Road_Access_Weakness'] * weights['Road_Access_Weakness']
    }
    
    # Sort by contribution (highest first)
    sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
    
    for component, contribution in sorted_components:
        bar = "█" * int(contribution / 5)  # Simple bar chart
        print(f"  {component:.<30} {contribution:.1f}  {bar}")

# ============================================================================
# PART 4F: Generate Insights
# ============================================================================

print("\n--- PART 4F: Key Insights ---\n")

# Find most critical issue
most_critical = df.nlargest(1, 'Fragility_Score')
print(f"Most Fragile Area: {most_critical['Zone_Name'].values[0]}")
print(f"  - Fragility Score: {most_critical['Fragility_Score'].values[0]}")
print(f"  - Risk Category: {most_critical['Risk_Category'].values[0]}")

# Count categories
print(f"\nZones by Risk Level:")
print(f"  CRITICAL: {len(df[df['Risk_Category']=='CRITICAL'])}")
print(f"  HIGH:     {len(df[df['Risk_Category']=='HIGH'])}")
print(f"  MODERATE: {len(df[df['Risk_Category']=='MODERATE'])}")

# Average scores
print(f"\nAverage Fragility Score: {df['Fragility_Score'].mean():.1f}")
print(f"Median Fragility Score:  {df['Fragility_Score'].median():.1f}")

# ============================================================================
# PART 4G: Save Results
# ============================================================================

print("\n--- PART 4G: Save Results ---\n")

os.makedirs('output', exist_ok=True)

# Save full results
df.to_csv('output/fragility_scores_full.csv', index=False)

# Save simplified results for mapping
simplified = df[['Zone_ID', 'Zone_Name', 'Fragility_Score', 'Risk_Category', 
                 'Fragility_Rank', 'Population', 'Elevation_ft']].copy()
simplified.to_csv('output/fragility_scores_summary.csv', index=False)

# Save just rankings
ranking_final = df[['Fragility_Rank', 'Zone_Name', 'Fragility_Score', 'Risk_Category']].sort_values('Fragility_Rank')
ranking_final.to_csv('output/zones_ranked_by_fragility.csv', index=False)

print("✓ Results saved:")
print("  - output/fragility_scores_full.csv (all data + scores)")
print("  - output/fragility_scores_summary.csv (for mapping)")
print("  - output/zones_ranked_by_fragility.csv (rankings only)")

# ============================================================================
# KEY CONCEPTS FOR BEGINNERS
# ============================================================================

print("\n" + "=" * 60)
print("KEY CONCEPTS FOR SCORING")
print("=" * 60)

print("""
1. SIMPLE SCORE (Equal Weights):
   - Average all features: (A + B + C + D + E) / 5
   - Use when you don't know relative importance
   - Easy to explain

2. WEIGHTED SCORE:
   - Multiply each feature by its importance weight
   - Sum the results: (A × 0.35) + (B × 0.25) + ...
   - Weights must sum to 1.0 (or 100%)
   - More realistic for your domain

3. SCORE INTERPRETATION:
   - 0-25: Minimal risk (safe)
   - 25-40: Low risk
   - 40-60: Moderate risk
   - 60-75: High risk
   - 75-100: Critical risk

4. RANKING:
   - Order zones by score (highest = most fragile)
   - Helps planners prioritize where to act first
   - Rank = position in this order

5. WEIGHTS ARE ASSUMPTIONS:
   - You can adjust weights based on local priorities
   - More flood exposure? Increase its weight
   - Facility access less critical? Lower its weight
   - Test different weights to see what makes sense
""")

print("\n✓ STEP 4 COMPLETE!")
print("\n🎉 PIPELINE FINISHED! You now have:")
print("   - Fragility scores for each zone")
print("   - Risk rankings")
print("   - Output files ready for visualization")
print("\nNext steps:")
print("  1. View output/gaps_ranked_by_fragility.csv")
print("  2. Visualize on map (requires mapping tool - see GUIDE.md)")
print("  3. Generate AI summaries (see 05_generate_insights.py)\n")
