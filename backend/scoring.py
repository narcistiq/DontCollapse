import os
import pandas as pd
import json

DATA_PATH = os.path.join(os.path.dirname(__file__), "tampa-resilience", "output", "master_fragility_with_explanations.csv")

# Simple static scenarios map just for frontend reliability
SCENARIOS = {
    "heavy rainfall": {"Elevation_Risk": 0.5, "Flood_Exposure": 2.0, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 0.5, "Social_Vulnerability": 1.0},
    "storm surge": {"Elevation_Risk": 1.5, "Flood_Exposure": 2.5, "Road_Access_Risk": 1.5, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0},
    "sea-level-rise increase": {"Elevation_Risk": 2.0, "Flood_Exposure": 1.5, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 0.5, "Social_Vulnerability": 1.0},
    "repeated flooding days": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.5, "Road_Access_Risk": 1.5, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0},
    "severe heatwave": {"Elevation_Risk": 0.1, "Flood_Exposure": 0.1, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 2.0, "Social_Vulnerability": 2.5},
    "baseline": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.0, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0}
}

def get_all_scored_zones(scenario_key: str):
    df = pd.read_csv(DATA_PATH)
    weights = SCENARIOS.get(scenario_key, SCENARIOS["baseline"])
    
    zones = []
    total_weight = sum(weights.values()) or 1.0

    for _, row in df.iterrows():
        raw_score = (
            (row.get("Elevation_Risk", 0) * weights["Elevation_Risk"]) +
            (row.get("Flood_Exposure", 0) * weights["Flood_Exposure"]) +
            (row.get("Road_Access_Risk", 0) * weights["Road_Access_Risk"]) +
            (row.get("Shelter_Access_Risk", 0) * weights["Shelter_Access_Risk"]) +
            (row.get("Social_Vulnerability", 0) * weights["Social_Vulnerability"])
        ) / total_weight
        
        zones.append({
            "zoneId": str(row["Zone_ID"]),
            "zoneName": row["Zone_Name"],
            "score": min(100, max(0, int(raw_score))),
            "reasoning": f"Driven by Flood ({row.get('Flood_Exposure',0)}) and Social Vuln ({row.get('Social_Vulnerability',0)})"
        })
    return sorted(zones, key=lambda x: x["score"], reverse=True)
