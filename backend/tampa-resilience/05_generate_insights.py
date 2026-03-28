"""
STEP 5: Generate AI-Style Insights & Recommendations
====================================================
This script creates human-readable explanations and actionable
recommendations for each zone based on fragility scores.

Run AFTER 04_calculate_fragility_score.py
"""

import pandas as pd
import os

print("=" * 60)
print("STEP 5: GENERATE INSIGHTS & RECOMMENDATIONS")
print("=" * 60)

# Load results
print("\nLoading fragility scores...\n")
df = pd.read_csv('output/fragility_scores_full.csv')

# ============================================================================
# PART 5A: Generate Individual Zone Insights
# ============================================================================

print("--- PART 5A: Zone-Specific Insights ---\n")

def generate_zone_insight(row):
    """
    Generate a human-readable explanation of why a zone is fragile.
    
    Mimics AI summarization by analyzing factor scores.
    """
    
    zone_name = row['Zone_Name']
    score = row['Fragility_Score']
    
    # Identify top 3 risk factors
    factors = {
        'Flood Exposure': row['Flood_Exposure_Norm'],
        'Low Elevation': row['Elevation_Risk'],
        'Poor Road Access': row['Road_Access_Weakness'],
        'Vulnerable Population': row['Population_Vulnerability'],
        'Limited Facility Access': row['Facility_Access_Risk']
    }
    
    top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Build insight statement
    if score >= 75:
        risk_level = "CRITICAL RISK"
        urgency = "IMMEDIATE ACTION REQUIRED"
    elif score >= 60:
        risk_level = "HIGH RISK"
        urgency = "URGENT ATTENTION NEEDED"
    elif score >= 40:
        risk_level = "MODERATE RISK"
        urgency = "PLANNING NEEDED"
    else:
        risk_level = "LOW RISK"
        urgency = "ROUTINE MONITORING"
    
    # Create explanation
    explanation = f"""\
{zone_name.upper()}
{'='*60}
Risk Level: {risk_level} (Score: {score}/100)
Status: {urgency}

Primary Concerns:
  1. {top_factors[0][0]} (Score: {top_factors[0][1]:.1f}/100)
  2. {top_factors[1][0]} (Score: {top_factors[1][1]:.1f}/100)
  3. {top_factors[2][0]} (Score: {top_factors[2][1]:.1f}/100)

Why This Area is Fragile:
"""
    
    # Build reason statement
    reasons = []
    
    if row['Flood_Exposure_Norm'] > 70:
        reasons.append(f"  • High flood exposure: {row['Repeat_Flood_Events_10y']:.0f} flood events in past 10 years")
    
    if row['Elevation_Risk'] > 70:
        reasons.append(f"  • Low elevation ({row['Elevation_ft']:.1f} ft): Areas below 5ft are at critical flood risk")
    
    if row['Population_Vulnerability'] > 70:
        vuln_pct = row['Pct_Elderly'] + row['Pct_Children']
        reasons.append(f"  • Vulnerable population: {vuln_pct:.0f}% elderly & children, {row['Pct_Poverty']:.0f}% in poverty")
    
    if row['Facility_Access_Risk'] > 70:
        reasons.append(f"  • Limited access to hospitals/shelters: {int(row['Num_Facilities'])} facilities nearby")
    
    if row['Road_Access_Weakness'] > 70:
        reasons.append(f"  • Poor road connectivity: Low accessibility score ({row['Avg_Facility_Accessibility']:.1f}%)")
    
    if not reasons:
        reasons.append("  • Combination of moderate risk factors across multiple categories")
    
    explanation += "\n".join(reasons)
    
    return explanation


# Generate insights for all zones
print("Generating detailed insights for each zone...\n")

for idx, zone_row in df.iterrows():
    insight = generate_zone_insight(zone_row)
    print(insight)
    print("\n")

# ============================================================================
# PART 5B: Generate Recommendations
# ============================================================================

print("\n--- PART 5B: Actionable Recommendations ---\n")

def generate_recommendations(row):
    """
    Generate specific, actionable recommendations for each zone.
    """
    
    zone_name = row['Zone_Name']
    recommendations = [zone_name]
    recommendations.append("RECOMMENDED ACTIONS:\n")
    
    # Flood Exposure
    if row['Flood_Exposure_Norm'] > 70:
        recommendations.append("🌊 FLOODING:")
        if row['Repeat_Flood_Events_10y'] > 5:
            recommendations.append("  - Install permanent pumping station for stormwater management")
            recommendations.append("  - Create elevated flood barriers along critical corridors")
        else:
            recommendations.append("  - Improve stormwater drainage infrastructure")
            recommendations.append("  - Create/restore wetlands for natural flood absorption")
        recommendations.append("  - Update flood emergency plans with frequent flooding scenario")
        recommendations.append("")
    
    # Elevation Risk
    if row['Elevation_Risk'] > 70:
        recommendations.append("📍 ELEVATION/TOPOGRAPHY:")
        recommendations.append("  - Map exact low-elevation areas prone to chronic flooding")
        recommendations.append("  - Consider elevated walkways or infrastructure in lowest zones")
        recommendations.append("  - Implement 'living shorelines' (marsh restoration) instead of hard barriers")
        recommendations.append("")
    
    # Road Access
    if row['Road_Access_Weakness'] > 60:
        recommendations.append("🛣️ ROAD CONNECTIVITY:")
        recommendations.append("  - Identify alternate evacuation routes not prone to flooding")
        recommendations.append("  - Raise elevation of main evacuation corridors")
        recommendations.append("  - Pre-position mobile barriers/sandbags along critical roads")
        recommendations.append("")
    
    # Population Vulnerability
    if row['Population_Vulnerability'] > 60:
        recommendations.append("👥 POPULATION PROTECTION:")
        recommendations.append(f"  - Establish community shelters (high-elevation, accessible)")
        recommendations.append(f"  - Create evacuation assistance program for elderly & disabled")
        recommendations.append(f"  - Distribute emergency kits to low-income households")
        recommendations.append("")
    
    # Facility Access
    if row['Facility_Access_Risk'] > 60:
        recommendations.append("🏥 CRITICAL FACILITIES:")
        recommendations.append("  - Ensure hospitals/shelters are on high ground (>10 ft elevation)")
        recommendations.append("  - Create redundant access routes to emergency facilities")
        recommendations.append("  - Pre-plan medical evacuation for flood scenarios")
        recommendations.append("")
    
    # General
    recommendations.append("✅ GENERAL:")
    recommendations.append("  - Conduct detailed vulnerability assessment (this is a first pass)")
    recommendations.append("  - Engage community in planning (residents know local conditions)")
    recommendations.append("  - Coordinate with neighboring areas on shared infrastructure")
    
    return "\n".join(recommendations)

print("Sample Recommendations for Highest-Risk Zone:\n")
highest_risk = df.nlargest(1, 'Fragility_Score').iloc[0]
print(generate_recommendations(highest_risk))

# ============================================================================
# PART 5C: Save All Insights
# ============================================================================

print("\n\n--- PART 5C: Save Insights to Files ---\n")

os.makedirs('output', exist_ok=True)

# Save all insights to a text file
with open('output/zone_insights_and_recommendations.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("TAMPA BAY WATER RESILIENCE ASSESSMENT\n")
    f.write("Zone-Specific Insights & Recommendations\n")
    f.write("=" * 80 + "\n\n")
    
    for idx, row in df.iterrows():
        f.write(generate_zone_insight(row))
        f.write("\n\n")
        f.write(generate_recommendations(row))
        f.write("\n\n")
        f.write("=" * 80 + "\n\n")

print("✓ Detailed insights saved to: output/zone_insights_and_recommendations.txt")

# ============================================================================
# PART 5D: Create a Summary Report
# ============================================================================

print("\n--- PART 5D: Executive Summary ---\n")

summary = f"""
TAMPA BAY WATER RESILIENCE ASSESSMENT - EXECUTIVE SUMMARY
{'='*70}

Total Zones Analyzed: {len(df)}

Risk Distribution:
  CRITICAL (75-100): {len(df[df['Risk_Category']=='CRITICAL'])} zones
  HIGH (60-75):      {len(df[df['Risk_Category']=='HIGH'])} zones
  MODERATE (40-60):  {len(df[df['Risk_Category']=='MODERATE'])} zones
  LOW (25-40):       {len(df[df['Risk_Category']=='LOW'])} zones
  MINIMAL (0-25):    {len(df[df['Risk_Category']=='MINIMAL'])} zones

Most Critical Area: {df.nlargest(1, 'Fragility_Score')['Zone_Name'].values[0]} (Score: {df['Fragility_Score'].max():.1f})

Key Statistics:
  Average Fragility Score: {df['Fragility_Score'].mean():.1f}
  Median Fragility Score:  {df['Fragility_Score'].median():.1f}
  Range: {df['Fragility_Score'].min():.1f} - {df['Fragility_Score'].max():.1f}

Priority Action Areas (Top 3):
"""

top_3 = df.nlargest(3, 'Fragility_Score')[['Fragility_Rank', 'Zone_Name', 'Fragility_Score', 'Risk_Category']]
for idx, row in top_3.iterrows():
    summary += f"  #{int(row['Fragility_Rank'])}: {row['Zone_Name']} (Score: {row['Fragility_Score']:.1f}, {row['Risk_Category']})\n"

summary += f"""

Next Steps:
  1. Review detailed zone insights (output/zone_insights_and_recommendations.txt)
  2. Prioritize top 3 critical areas for immediate action
  3. Engage stakeholders in vulnerable communities
  4. Develop detailed infrastructure improvement plans
  5. Implement monitoring & early warning systems
  6. Coordinate regional response (flooding doesn't follow zone boundaries)
"""

print(summary)

# Save summary
with open('output/executive_summary.txt', 'w') as f:
    f.write(summary)

print("\n✓ Executive summary saved to: output/executive_summary.txt")

# ============================================================================
# PART 5E: Create CSV with Insights (for database/app)
# ============================================================================

print("\n--- PART 5E: Save Insights to CSV (for web app) ---\n")

# Create a dataframe with insights
insights_list = []

for idx, row in df.iterrows():
    insight_text = generate_zone_insight(row)
    recommend_text = generate_recommendations(row)
    
    insights_list.append({
        'Zone_ID': row['Zone_ID'],
        'Zone_Name': row['Zone_Name'],
        'Fragility_Score': row['Fragility_Score'],
        'Risk_Category': row['Risk_Category'],
        'Fragility_Rank': int(row['Fragility_Rank']),
        'Insight_Summary': insight_text.split('\n\n')[1] if '\n\n' in insight_text else insight_text,
        'Key_Recommendations': recommend_text
    })

df_insights = pd.DataFrame(insights_list)
df_insights.to_csv('output/insights_for_webapp.csv', index=False)

print("✓ Web app-ready insights saved to: output/insights_for_webapp.csv")

# ============================================================================
# KEY CONCEPTS FOR BEGINNERS
# ============================================================================

print("\n" + "=" * 60)
print("KEY CONCEPTS FOR INSIGHTS")
print("=" * 60)

print("""
1. INSIGHTS:
   - Human-readable explanations based on data
   - Answers: "Why is this area fragile?"
   - Built from factor scores + thresholds

2. RECOMMENDATIONS:
   - Actionable next steps for each zone
   - Different actions based on what's causing the problem
   - Practical (pumps, elevation, shelters, etc.)

3. CUSTOMIZATION:
   - Change thresholds (currently >70 for "high risk")
   - Add domain-specific recommendations
   - Include local conditions & resources

4. FOR WEB APP:
   - Store insights/recommendations in database
   - Show when user clicks on a zone
   - Update recommendations as conditions change

5. LIMITATIONS:
   - This is a FIRST PASS analysis
   - Use as starting point for deeper study
   - Engage experts & community for final decisions
""")

print("\n" + "=" * 60)
print("✓ ENTIRE PIPELINE COMPLETE!")
print("=" * 60)

print("""
You now have:
  ✓ Fragility scores for each zone (0-100 scale)
  ✓ Risk categories (CRITICAL, HIGH, MODERATE, LOW, MINIMAL)
  ✓ Zone rankings by vulnerability
  ✓ Detailed insights explaining why each area is fragile
  ✓ Actionable recommendations for improvement
  ✓ CSV files ready for web app/mapping
  ✓ Executive summary report

Output Files:
  • fragility_scores_summary.csv - Use for mapping
  • zones_ranked_by_fragility.csv - For priority planning
  • zone_insights_and_recommendations.txt - Detailed explanations
  • insights_for_webapp.csv - Ready to display in web app
  • executive_summary.txt - For stakeholders

Next Steps:
  1. Review the insights and verify they make sense
  2. Adjust weights if needed (see 04_calculate_fragility_score.py)
  3. Build web app/dashboard (see GUIDE.md section "Building the Dashboard")
  4. Add map visualization (interactive mapping library like Folium, Mapbox, or Leaflet)
  5. Add flood scenario selector (rainfall, surge, sea-level rise)
  6. Deploy to show to stakeholders
""")
