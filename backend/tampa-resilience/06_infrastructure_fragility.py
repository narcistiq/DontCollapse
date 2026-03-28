"""
BONUS: Identify Most Fragile Infrastructure
===========================================
This script analyzes which specific roads, drainage zones, and facilities
are at highest risk - not just which zones overall.

Run AFTER Steps 1-4 are complete.
"""

import pandas as pd
import numpy as np
import os

print("=" * 70)
print("INFRASTRUCTURE FRAGILITY ANALYSIS")
print("=" * 70)

# Load original datasets
print("\nLoading individual infrastructure data...\n")

df_roads = pd.read_csv('data/sample_roads_data.csv')
df_facilities = pd.read_csv('data/sample_facilities_data.csv')
df_flood = pd.read_csv('data/sample_flood_data.csv')
df_fragility = pd.read_csv('output/fragility_scores_summary.csv')

# ============================================================================
# PART 1: Most Fragile ROADS
# ============================================================================

print("=" * 70)
print("PART 1: MOST FRAGILE ROADS (Critical for Evacuation)")
print("=" * 70)

# Calculate road fragility score
df_roads['Road_Fragility'] = 0.0

# If flood-prone, add risk
if 'Flood_Risk_Level' in df_roads.columns:
    flood_risk_map = {'Critical': 90, 'High': 70, 'Medium': 40, 'Low': 20}
    df_roads['Flood_Risk_Score'] = df_roads['Flood_Risk_Level'].map(
        lambda x: flood_risk_map.get(x, 50)
    )
else:
    df_roads['Flood_Risk_Score'] = 50

# If low elevation, add risk (< 5ft is critical)
df_roads['Elevation_Risk_Score'] = 100 - (df_roads['Elevation_ft'] * 10)
df_roads['Elevation_Risk_Score'] = df_roads['Elevation_Risk_Score'].clip(0, 100)

# Combine: flood risk (60%) + elevation risk (40%)
df_roads['Road_Fragility'] = (
    df_roads['Flood_Risk_Score'] * 0.6 +
    df_roads['Elevation_Risk_Score'] * 0.4
)

# Sort by fragility
df_roads_ranked = df_roads.sort_values('Road_Fragility', ascending=False)

print("\n🚨 MOST FRAGILE ROADS (needs immediate action):\n")
print(df_roads_ranked[['Road_ID', 'Zone_ID', 'Road_Type', 'Elevation_ft', 
                        'Flood_Risk_Level', 'Road_Fragility']].head(10).to_string())

print("\n\nWhat this means:")
print("  Roads with fragility > 80 = Will likely flood, blocking evacuation")
print("  Roads with fragility > 60 = High risk if major storm")
print("  Roads with fragility < 40 = Generally safe\n")

# Recommendations
critical_roads = df_roads[df_roads['Road_Fragility'] > 75]
if len(critical_roads) > 0:
    print(f"\n⚠️ ACTION NEEDED: {len(critical_roads)} roads have critical fragility")
    print("\nRecommendations for fragile roads:")
    print("  1. Elevate road surface (raise by 2-3 feet)")
    print("  2. Improve drainage (better storm drains, permeable pavement)")
    print("  3. Install barriers (temporary or permanent)")
    print("  4. Mark as 'no evacuation route' - find alternate")
    print("  5. Pre-position pumps nearby")

# ============================================================================
# PART 2: Most Fragile CRITICAL FACILITIES
# ============================================================================

print("\n" + "=" * 70)
print("PART 2: MOST FRAGILE CRITICAL FACILITIES")
print("=" * 70)

# Calculate facility fragility
df_facilities['Facility_Fragility'] = 0.0

# Low elevation is bad for facilities (they'll flood)
df_facilities['Elevation_Risk'] = 100 - (df_facilities['Elevation_ft'] * 15)
df_facilities['Elevation_Risk'] = df_facilities['Elevation_Risk'].clip(0, 100)

# If hard to reach (low accessibility), that's bad
df_facilities['Access_Risk'] = 100 - df_facilities['Accessibility_Score']

# Combine: elevation (60%) + access (40%)
df_facilities['Facility_Fragility'] = (
    df_facilities['Elevation_Risk'] * 0.6 +
    df_facilities['Access_Risk'] * 0.4
)

df_facilities_ranked = df_facilities.sort_values('Facility_Fragility', ascending=False)

print("\n🏥 MOST FRAGILE FACILITIES (Hospitals, Shelters, Schools):\n")
print(df_facilities_ranked[['Facility_ID', 'Facility_Type', 'Zone_ID', 
                             'Elevation_ft', 'Accessibility_Score', 
                             'Facility_Fragility']].to_string())

print("\n\nWhat this means:")
print("  Hospitals at risk = No place for injured during floods")
print("  Shelters at risk = Nowhere safe for evacuees to go")
print("  Schools at risk = Can't use as emergency centers\n")

# Recommendations
critical_facilities = df_facilities[df_facilities['Facility_Fragility'] > 60]
if len(critical_facilities) > 0:
    print(f"\n⚠️ CRITICAL: {len(critical_facilities)} essential facilities are fragile")
    print("\nRecommendations:")
    print("  1. Relocate to higher ground (if possible)")
    print("  2. Harden facility: waterproof, backup power, supplies")
    print("  3. Create redundancy: backup hospital/shelter elsewhere")
    print("  4. Improve access routes: elevate roads to facility")
    print("  5. Pre-position emergency supplies: not dependent on roads")

# ============================================================================
# PART 3: Most Fragile ZONES + Infrastructure Breakdown
# ============================================================================

print("\n" + "=" * 70)
print("PART 3: ZONES WITH MOST FRAGILE INFRASTRUCTURE")
print("=" * 70)

print("\nFor each zone, what's at risk?\n")

for zone_id in df_fragility['Zone_ID'].head(3).values:
    zone_name = df_fragility[df_fragility['Zone_ID'] == zone_id]['Zone_Name'].values[0]
    zone_score = df_fragility[df_fragility['Zone_ID'] == zone_id]['Fragility_Score'].values[0]
    
    print(f"\n{'='*60}")
    print(f"Zone: {zone_name} (Fragility: {zone_score:.1f})")
    print(f"{'='*60}")
    
    # Roads in this zone
    roads_in_zone = df_roads[df_roads['Zone_ID'] == zone_id]
    if len(roads_in_zone) > 0:
        worst_road = roads_in_zone.nlargest(1, 'Road_Fragility').iloc[0]
        print(f"\n  ROADS: {len(roads_in_zone)} roads")
        print(f"    → Most fragile: {worst_road['Road_ID']} ({worst_road['Road_Fragility']:.0f}/100)")
        print(f"      Type: {worst_road['Road_Type']}, Elevation: {worst_road['Elevation_ft']:.1f}ft")
    
    # Facilities in this zone
    facilities_in_zone = df_facilities[df_facilities['Zone_ID'] == zone_id]
    if len(facilities_in_zone) > 0:
        worst_facility = facilities_in_zone.nlargest(1, 'Facility_Fragility').iloc[0]
        print(f"\n  FACILITIES: {len(facilities_in_zone)} facilities")
        print(f"    → Most fragile: {worst_facility['Facility_ID']} ({worst_facility['Facility_Fragility']:.0f}/100)")
        print(f"      Type: {worst_facility['Facility_Type']}, Elevation: {worst_facility['Elevation_ft']:.1f}ft")
    
    # Flood exposure
    flood_info = df_flood[df_flood['Zone_ID'] == zone_id]
    if len(flood_info) > 0:
        floods = flood_info['Repeat_Flood_Events_10y'].values[0]
        elevation = flood_info['Elevation_ft'].values[0]
        exposure = flood_info['Flood_Exposure_Score'].values[0]
        print(f"\n  FLOOD RISK:")
        print(f"    → Elevation: {elevation:.1f}ft (critical if <5ft)")
        print(f"    → Flood events (10 years): {floods}")
        print(f"    → Exposure score: {exposure:.0f}/100")

# ============================================================================
# PART 4: Critical Bottlenecks & Chokepoints
# ============================================================================

print("\n" + "=" * 70)
print("PART 4: CRITICAL BOTTLENECKS")
print("=" * 70)

print("""
In disasters, cities get paralyzed by BOTTLENECKS - places where:
  • Only 1-2 roads lead in/out
  • Those roads flood
  • People are trapped

Example:
  "Downtown Tampa is surrounded by water. Main evacuation route
   (Bay Shore Blvd) is at sea level and floods immediately. People
   can't leave."

To find bottlenecks in YOUR data:
  1. Group roads by zone (which roads exit this zone?)
  2. Count how many escape routes each zone has
  3. Check if those routes are fragile
  4. If routes are few + fragile = BOTTLENECK

Simple calculation:
""")

escape_routes = df_roads.groupby('Zone_ID').size()
fragile_routes = df_roads[df_roads['Road_Fragility'] > 60].groupby('Zone_ID').size()

bottleneck_analysis = pd.DataFrame({
    'Total_Routes': escape_routes,
    'Fragile_Routes': fragile_routes
}).fillna(0)

bottleneck_analysis['Safe_Routes'] = (
    bottleneck_analysis['Total_Routes'] - bottleneck_analysis['Fragile_Routes']
)
bottleneck_analysis['Bottleneck_Risk'] = (
    bottleneck_analysis['Fragile_Routes'] / 
    bottleneck_analysis['Total_Routes'].replace(0, 1) * 100
)

print("\nBottleneck Analysis by Zone:\n")
print(bottleneck_analysis.to_string())

print("\n\nInterpretation:")
print("  Bottleneck_Risk > 50% = Most routes flood → TRAPPED")
print("  Bottleneck_Risk 25-50% = Half routes flooded → DIFFICULT")
print("  Bottleneck_Risk < 25% = Safe routes available → OKAY")

# ============================================================================
# PART 5: Priority Infrastructure Projects
# ============================================================================

print("\n" + "=" * 70)
print("PART 5: PRIORITY INFRASTRUCTURE IMPROVEMENT PROJECTS")
print("=" * 70)

projects = []

# High-risk roads
for idx, road in df_roads_ranked.head(3).iterrows():
    projects.append({
        'Priority': 'CRITICAL',
        'Type': 'Road Elevation',
        'Location': f"{road['Road_ID']} in {road['Zone_ID']}",
        'Problem': f"Elevation {road['Elevation_ft']:.1f}ft, Flood Risk: {road['Flood_Risk_Level']}",
        'Cost': 'High',
        'Benefit': 'Enable evacuation + normal traffic'
    })

# High-risk facilities
for idx, fac in df_facilities_ranked.head(2).iterrows():
    projects.append({
        'Priority': 'CRITICAL',
        'Type': 'Facility Hardening',
        'Location': f"{fac['Facility_ID']} ({fac['Facility_Type']}) in {fac['Zone_ID']}",
        'Problem': f"Elevation {fac['Elevation_ft']:.1f}ft, Access: {fac['Accessibility_Score']:.0f}",
        'Cost': 'Very High',
        'Benefit': 'Keep critical services operating during floods'
    })

# Drainage improvements
projects.append({
    'Priority': 'HIGH',
    'Type': 'Drainage System',
    'Location': 'Zones with repeated flooding',
    'Problem': 'Stormwater overwhelms drainage capacity',
    'Cost': 'Very High',
    'Benefit': 'Reduce flooding frequency + severity'
})

df_projects = pd.DataFrame(projects)

print("\nRecommended Infrastructure Projects (Priority Order):\n")
for idx, proj in df_projects.iterrows():
    print(f"\n{idx+1}. {proj['Type']} - {proj['Location']}")
    print(f"   Problem: {proj['Problem']}")
    print(f"   Cost: {proj['Cost']}")
    print(f"   Benefit: {proj['Benefit']}")

# ============================================================================
# PART 6: Save Reports
# ============================================================================

print("\n" + "=" * 70)
print("SAVING REPORTS")
print("=" * 70 + "\n")

os.makedirs('output', exist_ok=True)

# Save ranked roads
df_roads_ranked.to_csv('output/fragile_roads_ranked.csv', index=False)
print("✓ output/fragile_roads_ranked.csv")

# Save ranked facilities
df_facilities_ranked.to_csv('output/fragile_facilities_ranked.csv', index=False)
print("✓ output/fragile_facilities_ranked.csv")

# Save bottleneck analysis
bottleneck_analysis.to_csv('output/bottleneck_analysis.csv')
print("✓ output/bottleneck_analysis.csv")

# Save projects
df_projects.to_csv('output/priority_infrastructure_projects.csv', index=False)
print("✓ output/priority_infrastructure_projects.csv")

# Create summary report
with open('output/infrastructure_fragility_summary.txt', 'w') as f:
    f.write("INFRASTRUCTURE FRAGILITY ANALYSIS SUMMARY\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("MOST FRAGILE ROADS:\n")
    f.write("-" * 70 + "\n")
    for idx, road in df_roads_ranked.head(5).iterrows():
        f.write(f"  {road['Road_ID']}: {road['Road_Fragility']:.0f}/100 ")
        f.write(f"(Elevation: {road['Elevation_ft']:.1f}ft, Risk: {road['Flood_Risk_Level']})\n")
    
    f.write("\n\nMOST FRAGILE FACILITIES:\n")
    f.write("-" * 70 + "\n")
    for idx, fac in df_facilities_ranked.head(5).iterrows():
        f.write(f"  {fac['Facility_ID']} ({fac['Facility_Type']}): {fac['Facility_Fragility']:.0f}/100 ")
        f.write(f"(Elevation: {fac['Elevation_ft']:.1f}ft)\n")
    
    f.write("\n\nBOTTLENECK ZONES:\n")
    f.write("-" * 70 + "\n")
    bottlenecks = bottleneck_analysis[bottleneck_analysis['Bottleneck_Risk'] > 50]
    if len(bottlenecks) > 0:
        for zone_id, row in bottlenecks.iterrows():
            f.write(f"  {zone_id}: {row['Bottleneck_Risk']:.0f}% of routes fragile ")
            f.write(f"({int(row['Fragile_Routes'])}/{int(row['Total_Routes'])} routes)\n")
    else:
        f.write("  None identified\n")

print("✓ output/infrastructure_fragility_summary.txt")

print("\n" + "=" * 70)
print("✓ INFRASTRUCTURE ANALYSIS COMPLETE!")
print("=" * 70)

print("""

KEY TAKEAWAYS:

1. MOST FRAGILE ROADS: Identify specific roads that will flood
   → Need elevation, drainage, or marking as impassable

2. MOST FRAGILE FACILITIES: Hospitals, shelters at risk
   → Need hardening, relocation, or redundancy

3. BOTTLENECKS: Zones with few safe escape routes
   → People could be trapped - need alternate routes

4. PRIORITY PROJECTS: Fix highest-risk infrastructure first
   → Order by impact + feasibility

Next Steps:
  - Share priority projects with city planners
  - Get cost estimates for elevation/drainage improvements
  - Identify funding sources (grants, bonds, partnerships)
  - Test evacuation plans with identified safe routes
""")
