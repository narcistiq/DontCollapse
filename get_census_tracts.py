import requests
import json
import os

url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tracts_blkgrps_cb/MapServer/0/query?where=STATE='12'+AND+(COUNTY='057'+OR+COUNTY='103')&outFields=BASENAME&f=geojson"
print("Downloading...")
r = requests.get(url, timeout=30)
data = r.json()

features = []
for i, f in enumerate(data.get("features", [])):
    zone_id = f"Z{i+1:04d}"
    features.append({
        "type": "Feature",
        "properties": {
            "zoneId": zone_id,
            "name": f"Tract {f['properties'].get('BASENAME', i)}",
            "kind": "zone"
        },
        "geometry": f["geometry"]
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

print("Features:", len(features))
out_path = os.path.join(os.path.dirname(__file__), "frontend", "public", "data", "tampa_data.json")
with open(out_path, "w") as f:
    json.dump(geojson, f)

