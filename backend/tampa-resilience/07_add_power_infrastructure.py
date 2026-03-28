"""
STEP 7: Add Power Infrastructure Data
======================================
This script shows how to get power infrastructure data and merge it
with your existing zone data.

Power infrastructure is critical during floods - if substations flood,
entire neighborhoods lose power, affecting hospitals, pumps, etc.
"""

import pandas as pd
import requests
import json
import os
from io import StringIO

print("=" * 70)
print("STEP 7: ADDING POWER INFRASTRUCTURE DATA")
print("=" * 70)

# ============================================================================
# PART 1: Download Power Infrastructure from OpenStreetMap
# ============================================================================

print("\n--- PART 1: DOWNLOADING POWER DATA FROM OPENSTREETMAP ---\n")

print("""
OpenStreetMap (OSM) has extensive power infrastructure data.
We'll use Overpass Turbo to query it.

HOW TO DOWNLOAD POWER INFRASTRUCTURE DATA:

1. Go to: https://overpass-turbo.eu/
2. Copy-paste this query (for Tampa Bay area):

[out:json][timeout:25];
(
  // Power substations
  node["power"="substation"](27.5,-83.0,28.5,-82.0);
  way["power"="substation"](27.5,-83.0,28.5,-82.0);
  relation["power"="substation"](27.5,-83.0,28.5,-82.0);

  // Power plants
  node["power"="plant"](27.5,-83.0,28.5,-82.0);
  way["power"="plant"](27.5,-83.0,28.5,-82.0);
  relation["power"="plant"](27.5,-83.0,28.5,-82.0);

  // Power lines (major transmission)
  way["power"="line"]["voltage">="115000"](27.5,-83.0,28.5,-82.0);
  relation["power"="line"]["voltage">="115000"](27.5,-83.0,28.5,-82.0);
);
out body;
>;
out skel qt;

3. Click "Run" (green arrow)
4. Click "Export" → "download/copy as GeoJSON"
5. Save as: data/power_infrastructure.geojson

The coordinates (27.5,-83.0,28.5,-82.0) cover Tampa Bay area.
""")

# ============================================================================
# PART 2: Alternative - Download from Public Sources
# ============================================================================

print("\n--- PART 2: ALTERNATIVE PUBLIC DATA SOURCES ---\n")

print("""
If OSM data is insufficient, try these alternatives:

A. FLORIDA GEOGRAPHIC DATA LIBRARY (FGDL)
   URL: https://www.fgdl.org/
   Search for: "power" or "electric"
   Download: Electric transmission lines, substations

B. HOMELAND INFRASTRUCTURE FOUNDATION-LEVEL DATA (HIFLD)
   URL: https://hifld-geoplatform.opendata.arcgis.com/
   Search: "Power Plants" or "Electric Substations"
   Format: Shapefile or GeoJSON

C. ENERGY INFORMATION ADMINISTRATION (EIA)
   URL: https://www.eia.gov/maps/layer_info-m.php
   Search: Power plants, transmission lines
   Format: KML or Shapefile

D. LOCAL UTILITIES
   - Tampa Electric: https://www.tampaelectric.com/
   - Duke Energy Florida: https://www.duke-energy.com/
   - Florida Power & Light: https://www.fpl.com/
   (May require contacting them for GIS data)
""")

# ============================================================================
# PART 3: Create Sample Power Data (For Demonstration)
# ============================================================================

print("\n--- PART 3: CREATING SAMPLE POWER DATA ---\n")

print("Since we can't download live data here, let's create realistic sample data")
print("based on actual Tampa Bay power infrastructure.\n")

# Create sample power infrastructure data
power_data = [
    # Substations
    {"id": "SUB001", "type": "substation", "name": "Downtown Tampa Substation", "lat": 27.9475, "lon": -82.4584, "voltage": "115kV", "operator": "Tampa Electric"},
    {"id": "SUB002", "type": "substation", "name": "Ybor City Substation", "lat": 27.9556, "lon": -82.4451, "voltage": "69kV", "operator": "Tampa Electric"},
    {"id": "SUB003", "type": "substation", "name": "South Tampa Substation", "lat": 27.9200, "lon": -82.4800, "voltage": "115kV", "operator": "Tampa Electric"},
    {"id": "SUB004", "type": "substation", "name": "North Tampa Substation", "lat": 28.0500, "lon": -82.4200, "voltage": "69kV", "operator": "Tampa Electric"},
    {"id": "SUB005", "type": "substation", "name": "East Tampa Substation", "lat": 27.9800, "lon": -82.4200, "voltage": "115kV", "operator": "Tampa Electric"},

    # Power Plants
    {"id": "PLANT001", "type": "plant", "name": "H.L. Culbreath Bayside Power Station", "lat": 27.9333, "lon": -82.4333, "capacity_mw": 780, "fuel": "Natural Gas", "operator": "Tampa Electric"},
    {"id": "PLANT002", "type": "plant", "name": "Gannon Power Plant", "lat": 27.9500, "lon": -82.4167, "capacity_mw": 435, "fuel": "Coal", "operator": "Tampa Electric"},

    # Transmission Lines (simplified as points for demo)
    {"id": "LINE001", "type": "line", "name": "115kV Transmission Line A", "lat": 27.9400, "lon": -82.4500, "voltage": "115kV", "operator": "Tampa Electric"},
    {"id": "LINE002", "type": "line", "name": "230kV Transmission Line B", "lat": 27.9600, "lon": -82.4300, "voltage": "230kV", "operator": "Tampa Electric"},
]

df_power = pd.DataFrame(power_data)

# Add elevation data (simulated - in real data you'd get this from DEM)
# Tampa Bay elevations are generally low
df_power['elevation_ft'] = [5.2, 4.8, 6.1, 8.5, 7.2, 3.1, 4.5, 6.8, 5.9]

# Add flood risk (simulated)
df_power['flood_risk'] = ['High', 'High', 'Medium', 'Low', 'Medium', 'Critical', 'High', 'Medium', 'Medium']

print("Sample Power Infrastructure Data:")
print(df_power.to_string())

# Save sample data
os.makedirs('data', exist_ok=True)
df_power.to_csv('data/sample_power_infrastructure.csv', index=False)
print("\n✓ Saved sample power data to: data/sample_power_infrastructure.csv")

# ============================================================================
# PART 4: Load and Process Power Data
# ============================================================================

print("\n--- PART 4: LOADING AND PROCESSING POWER DATA ---\n")

# Load the power data
df_power = pd.read_csv('data/sample_power_infrastructure.csv')

print("Power infrastructure loaded:")
print(f"  - {len(df_power)} total facilities")
print(f"  - {len(df_power[df_power['type']=='substation'])} substations")
print(f"  - {len(df_power[df_power['type']=='plant'])} power plants")
print(f"  - {len(df_power[df_power['type']=='line'])} transmission lines")

# ============================================================================
# PART 5: Calculate Power Infrastructure Fragility
# ============================================================================

print("\n--- PART 5: CALCULATING POWER INFRASTRUCTURE FRAGILITY ---\n")

# Calculate fragility score for each power facility
df_power['fragility_score'] = 0.0

# Elevation risk (low elevation = high risk)
df_power['elevation_risk'] = 100 - (df_power['elevation_ft'] * 10)
df_power['elevation_risk'] = df_power['elevation_risk'].clip(0, 100)

# Flood risk mapping
flood_risk_map = {'Critical': 95, 'High': 75, 'Medium': 50, 'Low': 25}
df_power['flood_risk_score'] = df_power['flood_risk'].map(flood_risk_map)

# Importance weight (power plants > substations > lines)
importance_weights = {'plant': 1.0, 'substation': 0.8, 'line': 0.6}
df_power['importance_weight'] = df_power['type'].map(importance_weights)

# Combined fragility score
df_power['fragility_score'] = (
    df_power['elevation_risk'] * 0.6 +
    df_power['flood_risk_score'] * 0.4
) * df_power['importance_weight']

# Cap at 100
df_power['fragility_score'] = df_power['fragility_score'].clip(0, 100)

print("Power Infrastructure Fragility Scores:")
fragility_cols = ['id', 'name', 'type', 'elevation_ft', 'flood_risk', 'fragility_score']
print(df_power[fragility_cols].sort_values('fragility_score', ascending=False).to_string())

# ============================================================================
# PART 6: Assign Power Facilities to Zones
# ============================================================================

print("\n--- PART 6: ASSIGNING POWER FACILITIES TO ZONES ---\n")

# Load existing zone data
df_zones = pd.read_csv('output/combined_data.csv')

print("Assigning power facilities to zones based on proximity...")
print("(In real implementation, you'd use geospatial distance calculations)")

# Simple zone assignment based on facility names/locations
# (In real data, you'd use lat/lon coordinates and spatial joins)

zone_assignments = {
    'SUB001': 'Z001',  # Downtown Tampa Substation → Downtown Tampa
    'SUB002': 'Z002',  # Ybor City Substation → Ybor City
    'SUB003': 'Z003',  # South Tampa Substation → South Tampa
    'SUB004': 'Z004',  # North Tampa Substation → North Tampa
    'SUB005': 'Z005',  # East Tampa Substation → East Tampa
    'PLANT001': 'Z001', # Bayside Power Station → Downtown Tampa
    'PLANT002': 'Z001', # Gannon Power Plant → Downtown Tampa
    'LINE001': 'Z001',  # Transmission Line A → Downtown Tampa
    'LINE002': 'Z002',  # Transmission Line B → Ybor City
}

df_power['Zone_ID'] = df_power['id'].map(zone_assignments)

print("Power facilities assigned to zones:")
for zone_id in df_zones['Zone_ID']:
    facilities_in_zone = df_power[df_power['Zone_ID'] == zone_id]
    if len(facilities_in_zone) > 0:
        print(f"\n  {zone_id} ({df_zones[df_zones['Zone_ID']==zone_id]['Zone_Name'].values[0]}):")
        for idx, fac in facilities_in_zone.iterrows():
            print(f"    - {fac['name']} ({fac['type']}) - Fragility: {fac['fragility_score']:.0f}/100")

# ============================================================================
# PART 7: Aggregate Power Data by Zone
# ============================================================================

print("\n--- PART 7: AGGREGATING POWER DATA BY ZONE ---\n")

# Group by zone and aggregate power infrastructure
power_by_zone = df_power.groupby('Zone_ID').agg({
    'id': 'count',                           # Number of power facilities
    'fragility_score': ['mean', 'max'],      # Average and max fragility
    'elevation_ft': 'min',                   # Lowest elevation (most vulnerable)
    'type': lambda x: ', '.join(x.unique())  # Types present
}).reset_index()

# Flatten column names
power_by_zone.columns = ['Zone_ID', 'num_power_facilities', 'avg_power_fragility',
                        'max_power_fragility', 'min_power_elevation', 'power_types']

print("Power infrastructure summary by zone:")
print(power_by_zone.to_string())

# ============================================================================
# PART 8: Merge Power Data with Main Dataset
# ============================================================================

print("\n--- PART 8: MERGING POWER DATA WITH MAIN DATASET ---\n")

# Merge power data into main dataset
df_merged = df_zones.merge(power_by_zone, on='Zone_ID', how='left')

# Fill missing values (zones with no power facilities)
df_merged['num_power_facilities'] = df_merged['num_power_facilities'].fillna(0)
df_merged['avg_power_fragility'] = df_merged['avg_power_fragility'].fillna(0)
df_merged['max_power_fragility'] = df_merged['max_power_fragility'].fillna(0)
df_merged['min_power_elevation'] = df_merged['min_power_elevation'].fillna(999)  # High number = no facility
df_merged['power_types'] = df_merged['power_types'].fillna('None')

print("Merged dataset with power infrastructure:")
print(df_merged[['Zone_ID', 'Zone_Name', 'num_power_facilities', 'avg_power_fragility',
                 'max_power_fragility']].to_string())

# ============================================================================
# PART 9: Update Fragility Score with Power Risk
# ============================================================================

print("\n--- PART 9: UPDATING FRAGILITY SCORES WITH POWER RISK ---\n")

# Calculate power vulnerability factor
df_merged['power_vulnerability'] = 0.0

# If zone has power facilities, add their fragility
df_merged['power_vulnerability'] = df_merged['avg_power_fragility'] * (df_merged['num_power_facilities'] > 0).astype(int)

# If zone has critical power facilities (fragility > 70), increase vulnerability
df_merged['power_vulnerability'] += (df_merged['max_power_fragility'] > 70).astype(int) * 20

# If power facilities are at very low elevation (< 5ft), critical risk
df_merged['power_vulnerability'] += (df_merged['min_power_elevation'] < 5).astype(int) * 30

# Normalize to 0-100
df_merged['power_vulnerability'] = df_merged['power_vulnerability'].clip(0, 100)

print("Power vulnerability by zone:")
print(df_merged[['Zone_ID', 'Zone_Name', 'power_vulnerability']].to_string())

# ============================================================================
# PART 10: Recalculate Overall Fragility Score
# ============================================================================

print("\n--- PART 10: RECALCULATING OVERALL FRAGILITY SCORES ---\n")

# Original weights (from Step 4)
original_weights = {
    'Flood_Exposure_Norm': 0.35,
    'Elevation_Risk': 0.25,
    'Population_Vulnerability': 0.20,
    'Facility_Access_Risk': 0.15,
    'Road_Access_Weakness': 0.05
}

# New weights including power (reduce others proportionally)
total_original = sum(original_weights.values())  # 1.0
power_weight = 0.10  # Add 10% weight for power infrastructure
scale_factor = (1.0 - power_weight) / total_original

new_weights = {k: v * scale_factor for k, v in original_weights.items()}
new_weights['power_vulnerability'] = power_weight

print("Updated weights (including power infrastructure):")
for factor, weight in new_weights.items():
    print(f"  {factor}: {weight:.2f} ({weight*100:.0f}%)")

# Calculate new fragility score
df_merged['Fragility_Score_Updated'] = (
    df_merged['Flood_Exposure_Norm'] * new_weights['Flood_Exposure_Norm'] +
    df_merged['Elevation_Risk'] * new_weights['Elevation_Risk'] +
    df_merged['Population_Vulnerability'] * new_weights['Population_Vulnerability'] +
    df_merged['Facility_Access_Risk'] * new_weights['Facility_Access_Risk'] +
    df_merged['Road_Access_Weakness'] * new_weights['Road_Access_Weakness'] +
    df_merged['power_vulnerability'] * new_weights['power_vulnerability']
)

# Round and cap
df_merged['Fragility_Score_Updated'] = df_merged['Fragility_Score_Updated'].round(1).clip(0, 100)

print("\nUpdated fragility scores (including power risk):")
comparison_cols = ['Zone_ID', 'Zone_Name', 'Fragility_Score', 'Fragility_Score_Updated', 'power_vulnerability']
print(df_merged[comparison_cols].sort_values('Fragility_Score_Updated', ascending=False).to_string())

# ============================================================================
# PART 11: Save Updated Dataset
# ============================================================================

print("\n--- PART 11: SAVING UPDATED DATASET ---\n")

os.makedirs('output', exist_ok=True)

# Save updated dataset
df_merged.to_csv('output/combined_data_with_power.csv', index=False)
print("✓ Updated dataset saved to: output/combined_data_with_power.csv")

# Save power infrastructure details
df_power.to_csv('output/power_infrastructure_detailed.csv', index=False)
print("✓ Power infrastructure details saved to: output/power_infrastructure_detailed.csv")

# Save power summary by zone
power_by_zone.to_csv('output/power_infrastructure_by_zone.csv', index=False)
print("✓ Power summary by zone saved to: output/power_infrastructure_by_zone.csv")

# ============================================================================
# KEY CONCEPTS FOR BEGINNERS
# ============================================================================

print("\n" + "=" * 70)
print("KEY CONCEPTS FOR POWER INFRASTRUCTURE")
print("=" * 70)

print("""
1. POWER INFRASTRUCTURE TYPES:
   - Substations: Transform voltage, distribute power locally
   - Power Plants: Generate electricity (coal, gas, nuclear)
   - Transmission Lines: Carry power over long distances

2. WHY POWER MATTERS IN FLOODS:
   - Hospitals need power for life support
   - Water pumps need power to remove floodwater
   - Communication systems fail without power
   - People can't cook, refrigerate food, or charge devices

3. FRAGILITY FACTORS:
   - Elevation: Power equipment can't be underwater
   - Flood Risk: Water damages transformers, generators
   - Importance: Power plants > substations > transmission lines

4. IMPACT ON ZONES:
   - Zone with fragile power = higher overall fragility
   - Power failure affects entire zone's resilience
   - Critical facilities (hospitals) especially vulnerable

5. DATA SOURCES:
   - OpenStreetMap: Free, community-maintained
   - Government: EIA, HIFLD, state agencies
   - Utilities: Local power companies (may share data)
""")

print("\n✓ STEP 7 COMPLETE!")
print("Next: Run '04_calculate_fragility_score.py' again to see updated rankings")
print("      (or use the new combined_data_with_power.csv)")
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
You now have power infrastructure integrated into your analysis:

1. POWER FACILITIES IDENTIFIED:
   - Substations, power plants, transmission lines
   - Each with fragility score based on elevation + flood risk

2. ZONES UPDATED:
   - Each zone now knows its power infrastructure
   - Fragility scores updated to include power risk

3. CRITICAL INSIGHTS:
   - Which zones have vulnerable power infrastructure?
   - How does power failure affect overall resilience?
   - Where to prioritize power hardening projects?

4. OUTPUT FILES:
   - combined_data_with_power.csv (main dataset)
   - power_infrastructure_detailed.csv (all facilities)
   - power_infrastructure_by_zone.csv (summary by zone)

Next steps:
- Re-run fragility scoring with power data included
- Identify zones where power failure would be catastrophic
- Plan power infrastructure hardening (elevation, waterproofing)
""")
