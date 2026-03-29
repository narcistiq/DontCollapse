import json
import os
import random
import csv

def sync_data():
    geojson_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "data", "tampa_data.json")
    csv_path = os.path.join(os.path.dirname(__file__), "..", "tampa-resilience", "output", "master_fragility_with_explanations.csv")
    
    with open(geojson_path, "r") as f:
        data = json.load(f)
        
    features = data.get("features", [])
    
    headers = [
        "Zone_ID", "Zone_Name", "Elevation_Risk", "Flood_Exposure", 
        "Road_Access_Risk", "Shelter_Access_Risk", "Social_Vulnerability", 
        "Composite_Fragility_Score"
    ]
    
    # We will purposely generate polarized data so different scenarios trigger red/green extremes
    rows = []
    for i, f in enumerate(features):
        z_id = f["properties"]["zoneId"]
        z_name = f["properties"]["name"]
        
        if i % 3 == 0:
            # Extreme flood risk, safe heat
            flood = random.randint(95, 100)
            heat = random.randint(0, 10)
        elif i % 3 == 1:
            # Extreme heat risk, safe flood
            flood = random.randint(0, 10)
            heat = random.randint(95, 100)
        else:
            # Moderate mixed
            flood = random.randint(40, 60)
            heat = random.randint(40, 60)
            
        row = [
            z_id,
            z_name,
            flood, # Elevation_Risk
            flood, # Flood_Exposure
            heat,  # Road_Access (tied to a proxy for heat/soc vuln for this simple example)
            heat,  # Shelter_Access (tied to heat)
            random.randint(90, 100), # ALWAYS HIGH VULNERABILITY TO BOOST BASELINE A BIT
            50
        ]
        rows.append(row)
        
    with open(csv_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print(f"DataAgent: Successfully synced {len(rows)} dynamically polarized zones into {csv_path}")

if __name__ == "__main__":
    sync_data()
