import json
import random
import os
import pandas as pd

with open("frontend/public/data/tampa_data.json", "r") as f:
    geojson = json.load(f)

rows = []
for f in geojson.get("features", []):
    zId = f["properties"]["zoneId"]
    zName = f["properties"]["name"]
    # random baseline between 10 and 60
    e_risk = random.randint(10, 80)
    f_exp = random.randint(10, 80)
    r_acc = random.randint(10, 80)
    s_acc = random.randint(10, 80)
    s_vul = random.randint(10, 80)
    comp = (e_risk + f_exp + r_acc + s_acc + s_vul) // 5
    
    rows.append({
        "Zone_ID": zId,
        "Zone_Name": zName,
        "Elevation_Risk": e_risk,
        "Flood_Exposure": f_exp,
        "Road_Access_Risk": r_acc,
        "Shelter_Access_Risk": s_acc,
        "Social_Vulnerability": s_vul,
        "Composite_Fragility_Score": comp
    })

df = pd.DataFrame(rows)
out_path = "backend/tampa-resilience/output/master_fragility_with_explanations.csv"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
df.to_csv(out_path, index=False)
print(f"Generated {len(rows)} entries for backend scoring.")
