import os
import pandas as pd
import json

DATA_PATH = os.path.join(os.path.dirname(__file__), "tampa-resilience", "output", "master_fragility_with_explanations.csv")

# Simple static scenarios map just for frontend reliability
SCENARIOS = {
    "heavy rainfall": {"Elevation_Risk": 0.5, "Flood_Exposure": 2.0, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 0.5, "Social_Vulnerability": 1.0, "severity": 1.2},
    "storm surge": {"Elevation_Risk": 1.5, "Flood_Exposure": 2.5, "Road_Access_Risk": 1.5, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0, "severity": 1.4},
    "sea-level-rise increase": {"Elevation_Risk": 2.0, "Flood_Exposure": 1.5, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 0.5, "Social_Vulnerability": 1.0, "severity": 1.1},
    "repeated flooding days": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.5, "Road_Access_Risk": 1.5, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0, "severity": 1.1},
    "severe heatwave": {"Elevation_Risk": 0.1, "Flood_Exposure": 0.1, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 2.0, "Social_Vulnerability": 2.5, "severity": 1.0},
    "live conditions": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.2, "Road_Access_Risk": 1.2, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.5, "severity": 0.5},
    "category 5 hurricane": {"Elevation_Risk": 2.5, "Flood_Exposure": 3.0, "Road_Access_Risk": 2.5, "Shelter_Access_Risk": 3.0, "Social_Vulnerability": 2.0, "severity": 2.2},
    "baseline": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.0, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0, "severity": 1.0}
}

def get_all_scored_zones(scenario_key: str):
    df = pd.read_csv(DATA_PATH)
    weights = SCENARIOS.get(scenario_key, SCENARIOS["baseline"])
    
    zones = []
    severity = weights.get("severity", 1.0)
    # calculate total weight without severity
    total_weight = sum([v for k, v in weights.items() if k != "severity"]) or 1.0

    for _, row in df.iterrows():
        raw_score = (
            (row.get("Elevation_Risk", 0) * weights.get("Elevation_Risk", 1.0)) +
            (row.get("Flood_Exposure", 0) * weights.get("Flood_Exposure", 1.0)) +
            (row.get("Road_Access_Risk", 0) * weights.get("Road_Access_Risk", 1.0)) +
            (row.get("Shelter_Access_Risk", 0) * weights.get("Shelter_Access_Risk", 1.0)) +
            (row.get("Social_Vulnerability", 0) * weights.get("Social_Vulnerability", 1.0))
        ) / total_weight
        
        raw_score = raw_score * severity
        
        zones.append({
            "zoneId": str(row["Zone_ID"]),
            "zoneName": row["Zone_Name"],
            "score": min(100, max(0, int(raw_score))),
            "reasoning": f"Driven by Flood ({row.get('Flood_Exposure',0)}) and Social Vuln ({row.get('Social_Vulnerability',0)})"
        })
    return sorted(zones, key=lambda x: x["score"], reverse=True)
