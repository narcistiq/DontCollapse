import json

with open("frontend/public/data/tampa_data.json") as f:
    data = json.load(f)

min_lon = 180
max_lon = -180
min_lat = 90
max_lat = -90

for feature in data["features"]:
    coords_list = []
    if feature["geometry"]["type"] == "Polygon":
        coords_list = feature["geometry"]["coordinates"]
    elif feature["geometry"]["type"] == "MultiPolygon":
        for poly in feature["geometry"]["coordinates"]:
            coords_list.extend(poly)
            
    for ring in coords_list:
        if type(ring[0]) in (float, int):
            ring = [ring] # fix if not nested
        for pt in ring:
            try:
                min_lon = min(min_lon, pt[0])
                max_lon = max(max_lon, pt[0])
                min_lat = min(min_lat, pt[1])
                max_lat = max(max_lat, pt[1])
            except:
                pass
print(f"[{min_lon}, {min_lat}], [{max_lon}, {max_lat}]")
