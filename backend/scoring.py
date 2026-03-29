import os
import pandas as pd
import json

DATA_PATH = os.path.join(os.path.dirname(__file__), "tampa-resilience", "output", "master_fragility_with_explanations.csv")

# Simple static scenarios map just for frontend reliability
SCENARIOS = {
    # distributions: [pct_green, pct_yellow, pct_orange, pct_red] mapping to visual thresholds 0..30..50..80..100
    "heavy rainfall": {"Elevation_Risk": 0.5, "Flood_Exposure": 2.0, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 0.5, "Social_Vulnerability": 1.0, "severity": 1.8, "distribution": [0.15, 0.40, 0.30, 0.15]},
    "storm surge": {"Elevation_Risk": 1.5, "Flood_Exposure": 2.5, "Road_Access_Risk": 1.5, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0, "severity": 2.4, "distribution": [0.05, 0.20, 0.40, 0.35]},
    "sea-level-rise increase": {"Elevation_Risk": 1.5, "Flood_Exposure": 1.5, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 0.5, "Social_Vulnerability": 1.0, "severity": 1.7, "distribution": [0.20, 0.30, 0.30, 0.20]},
    "repeated flooding days": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.5, "Road_Access_Risk": 1.5, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0, "severity": 1.6, "distribution": [0.15, 0.35, 0.35, 0.15]},
    "severe heatwave": {"Elevation_Risk": 0.1, "Flood_Exposure": 0.1, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 2.0, "Social_Vulnerability": 2.5, "severity": 1.6, "distribution": [0.10, 0.20, 0.40, 0.30]},
    "live conditions": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.2, "Road_Access_Risk": 1.2, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.5, "severity": 0.3, "distribution": None}, # Objective, use raw scores
    "category 5 hurricane": {"Elevation_Risk": 2.5, "Flood_Exposure": 3.0, "Road_Access_Risk": 2.5, "Shelter_Access_Risk": 3.0, "Social_Vulnerability": 2.0, "severity": 3.5, "distribution": [0.05, 0.10, 0.30, 0.55]},
    "baseline": {"Elevation_Risk": 1.0, "Flood_Exposure": 1.0, "Road_Access_Risk": 1.0, "Shelter_Access_Risk": 1.0, "Social_Vulnerability": 1.0, "severity": 1.0, "distribution": [0.20, 0.30, 0.30, 0.20]}
}

def get_all_scored_zones(scenario_key: str):
    df = pd.read_csv(DATA_PATH)
    weights = SCENARIOS.get(scenario_key, SCENARIOS["baseline"])
    
    zones = []
    severity = weights.get("severity", 1.0)
    
    # Calculate keys that are strictly metrics
    metric_keys = [k for k in weights.keys() if k not in ["severity", "distribution"]]
    total_weight = sum([weights[k] for k in metric_keys]) or 1.0

    for _, row in df.iterrows():
        raw_score = sum([row.get(k, 0) * weights[k] for k in metric_keys]) / total_weight
        raw_score = raw_score * severity
        
        zones.append({
            "zoneId": str(row["Zone_ID"]),
            "zoneName": row["Zone_Name"],
            "raw_score": raw_score,
            "score": min(100, max(0, int(raw_score))),
            "reasoning": f"Driven by Flood ({row.get('Flood_Exposure',0)}) and Social Vuln ({row.get('Social_Vulnerability',0)})"
        })

    # Sort to determine percentile/rank easily
    zones.sort(key=lambda x: x["raw_score"])
    
    dist = weights.get("distribution")
    
    if dist is not None and len(zones) > 0:
        # dist is [green_pct, yellow_pct, orange_pct, red_pct]
        # boundaries are visual thresholds: green(0-29), yellow(30-49), orange(50-79), red(80-100)
        n = len(zones)
        c0 = int(n * dist[0])
        c1 = c0 + int(n * dist[1])
        c2 = c1 + int(n * dist[2])
        
        for i, z in enumerate(zones):
            # assign mapped score depending on rank bucket
            if i < c0:
                # 0 to 29
                t = i / max(1, c0 - 1)
                z["score"] = int(0 + t * 29)
            elif i < c1:
                # 30 to 49
                t = (i - c0) / max(1, (c1 - c0) - 1)
                z["score"] = int(30 + t * 19)
            elif i < c2:
                # 50 to 79
                t = (i - c1) / max(1, (c2 - c1) - 1)
                z["score"] = int(50 + t * 29)
            else:
                # 80 to 100
                t = (i - c2) / max(1, (n - 1 - c2))
                z["score"] = int(80 + t * 20)
                
    # clean up and reverse sort order (highest first)
    zones.sort(key=lambda x: x["score"], reverse=True)
    for z in zones:
        if "raw_score" in z:
            del z["raw_score"]
            
    return zones