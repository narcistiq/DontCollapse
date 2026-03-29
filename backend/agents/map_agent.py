import requests
import json
import logging
import os

def run_map_agent():
    print("MapAgent: Pulling landuse boundaries for Tampa...")
    
    query = """
    [out:json][timeout:25];
    area["name"="Tampa"]->.searchArea;
    (
      way["landuse"~"residential|commercial|retail|industrial"](area.searchArea);
    );
    out geom;
    """
    
    try:
        response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=30)
        response.raise_for_status()
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
                    
                    if area > 0.00005:
                        tags = element.get("tags", {})
                        name = tags.get("name", tags.get("landuse", "Tampa Zone").title())
                        features.append({
                            "name": name,
                            "area": area,
                            "coords": coords
                        })
        
        # Sort by area descending and take top 100
        features.sort(key=lambda x: x["area"], reverse=True)
        top_features = features[:100]
        
        geojson_features = []
        for i, f in enumerate(top_features):
            zone_id = f"Z{(i+1):03d}"
            name_val = f["name"]
            if name_val in ["Residential", "Commercial", "Retail", "Industrial"]:
                name_val = f"{name_val} District {i+1}"
            geojson_features.append({
                "type": "Feature",
                "properties": {
                    "zoneId": zone_id,
                    "name": name_val,
                    "kind": "zone",
                    "area": f["area"]
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": f["coords"]
                }
            })
            
        print(f"Processed {len(geojson_features)} large zones from Tampa.")
        
        geojson = {
            "type": "FeatureCollection",
            "features": geojson_features
        }
        
        out_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "data", "tampa_data.json")
        with open(out_path, "w") as f:
            json.dump(geojson, f, indent=2)
            
        print(f"GeoJSON saved successfully.")
        return geojson
        
    except Exception as e:
        print(f"Failed to fetch from Overpass: {e}")
        return None

if __name__ == "__main__":
    run_map_agent()
