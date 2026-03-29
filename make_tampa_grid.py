import json
import os

center_lon = -82.46
center_lat = 27.95

# Let's make a 8x5 grid
lon_step = 0.015
lat_step = 0.015

features = []
zone_counter = 1

for x in range(8):
    for y in range(5):
        lon = center_lon + (x - 4) * lon_step
        lat = center_lat + (y - 2.5) * lat_step
        
        # Add random offset for more natural look
        
        coords = [
            [
                [lon, lat],
                [lon + lon_step, lat],
                [lon + lon_step, lat + lat_step],
                [lon, lat + lat_step],
                [lon, lat]
            ]
        ]
        
        zone_id = f"Z{zone_counter:03d}"
        features.append({
            "type": "Feature",
            "properties": {
                "zoneId": zone_id,
                "name": f"Tampa District {zone_id}",
                "kind": "zone"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coords
            }
        })
        zone_counter += 1

geojson = {
    "type": "FeatureCollection",
    "features": features
}

out_path = "frontend/public/data/tampa_data.json"
with open(out_path, "w") as f:
    json.dump(geojson, f, indent=2)

print(f"Generated {len(features)} zones.")
