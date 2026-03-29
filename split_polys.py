import json
import os
from shapely.geometry import shape, mapping, box

def grid_bounds(geom, num_x=2, num_y=2):
    minx, miny, maxx, maxy = geom.bounds
    dx = (maxx - minx) / num_x
    dy = (maxy - miny) / num_y
    grid = []
    for i in range(num_x):
        for j in range(num_y):
            grid.append(box(minx + i*dx, miny + j*dy, minx + (i+1)*dx, miny + (j+1)*dy))
    return grid

with open("frontend/public/data/tampa_data.json", "r") as f:
    data = json.load(f)

new_features = []
zones_count = 1

for feature in data["features"]:
    props = feature["properties"]
    parent_id = props.get("zoneId", "Z")
    try:
        geom = shape(feature["geometry"])
    except:
        continue
    
    # 7x7 grid per zip code => 49 chunks each!
    grid_polys = grid_bounds(geom, 7, 7)
    
    for gpoly in grid_polys:
        intersection = geom.intersection(gpoly)
        if not intersection.is_empty:
            if intersection.geom_type == 'Polygon':
                parts = [intersection]
            elif intersection.geom_type == 'MultiPolygon':
                parts = list(intersection.geoms)
            else:
                continue
                
            for part in parts:
                if part.area > 0.000000001:  # ignore tiny slivers
                    new_feat = {
                        "type": "Feature",
                        "properties": {
                            "zoneId": f"{parent_id}_{zones_count:04d}",
                            "name": f"{props.get('name', 'Zone')} Part {zones_count.__str__()}",
                            "kind": "zone"
                        },
                        "geometry": mapping(part)
                    }
                    new_features.append(new_feat)
                    zones_count += 1

print(f"Split {len(data['features'])} geometries into {len(new_features)} highly detailed sub-geometries.")

with open("frontend/public/data/tampa_data.json", "w") as f:
    json.dump({"type": "FeatureCollection", "features": new_features}, f, indent=2)

