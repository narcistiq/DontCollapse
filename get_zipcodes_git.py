import requests
import json
import os

url = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/fl_florida_zip_codes_geo.min.json"
print("Downloading FL zip codes...")
r = requests.get(url, timeout=30)
data = r.json()

features = []
counter = 1
for f in data.get("features", []):
    props = f.get("properties", {})
    zip_code = props.get("ZCTA5CE10", "")
    if zip_code.startswith("336") or zip_code.startswith("337"):
        zone_id = f"Z_{zip_code}"
        features.append({
            "type": "Feature",
            "id": counter,
            "properties": {
                "zoneId": zone_id,
                "name": f"ZIP {zip_code}",
                "kind": "zone",
                "fragility": 20
            },
            "geometry": f.get("geometry")
        })
        counter += 1

geojson = {
    "type": "FeatureCollection",
    "features": features
}

print(f"Kept {len(features)} zip codes for Tampa Bay area.")
out_path = os.path.join(os.path.dirname(__file__), "frontend", "public", "data", "tampa_data.json")
with open(out_path, "w") as f:
    json.dump(geojson, f)

