import json
import os

min_lon = -82.68
max_lon = -82.35
min_lat = 27.80
max_lat = 28.15

cols = 40
rows = 40

lon_step = (max_lon - min_lon) / cols
lat_step = (max_lat - min_lat) / rows

features = []
zone_counter = 1

for x in range(cols):
    for y in range(rows):
        lon = min_lon + (x * lon_step)
        lat = min_lat + (y * lat_step)
        
        coords = [
            [
                [lon, lat],
                [lon + lon_step, lat],
                [lon + lon_step, lat + lat_step],
                [lon, lat + lat_step],
                [lon, lat]
            ]
        ]
        
        zone_id = f"Z{zone_counter:04d}"
        features.append({
            "type": "Feature",
            "properties": {
                "zoneId": zone_id,
                "name": f"Sector {zone_id}",
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

out_path = os.path.join(os.path.dirname(__file__), "frontend", "public", "data", "tampa_data.json")
with open(out_path, "w") as f:
    json.dump(geojson, f, indent=2)

print(f"Generated {len(features)} zones for full coverage.")
