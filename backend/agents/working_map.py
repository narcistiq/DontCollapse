import requests
import json
import os

def run():
    print("Pulling all major Tampa zones bounds...")
    query = """
    [out:json][timeout:30];
    area["name"="Tampa"]->.searchArea;
    (
      way["landuse"~"residential|commercial|retail|industrial"](area.searchArea);
    );
    out geom;
    """
    response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=35)
    data = response.json()
    
    features = []
    for element in data.get("elements", []):
        if element.get("type") == "way":
            pts = element.get("geometry", [])
            if len(pts) > 3 and pts[0] == pts[-1]:
                coords = [[ [pt["lon"], pt["lat"]] for pt in pts ]]
                min_lon = min(pt[0] for pt in coords[0])
                max_lon = max(pt[0] for pt in coords[0])
                min_lat = min(pt[1] for pt in coords[0])
                max_lat = max(pt[1] for pt in coords[0])
                area = (max_lon - min_lon) * (max_lat - min_lat)
                
                # LOWERED AREA REQUIREMENT TO GET UP TO 150 BLOCKS!
                if area > 0.000005: 
                    tags = element.get("tags", {})
                    name = tags.get("name", tags.get("landuse", "Tampa Zone").title())
                    features.append({"name": name, "area": area, "coords": coords})
    
    features.sort(key=lambda x: x["area"], reverse=True)
    top_features = features[:150]
    
    geojson_features = []
    for i, f in enumerate(top_features):
        name_val = f["name"] if f["name"] not in ["Residential", "Commercial", "Retail", "Industrial"] else f"{f['name']} Zone {i+1}"
        geojson_features.append({
            "type": "Feature",
            "properties": {"zoneId": f"Z{(i+1):03d}", "name": name_val, "kind": "zone"},
            "geometry": {"type": "Polygon", "coordinates": f["coords"]}
        })
        
    print(f"Processed {len(geojson_features)} clean zones.")
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "data", "tampa_data.json"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": geojson_features}, f, indent=2)

if __name__ == "__main__":
    run()
