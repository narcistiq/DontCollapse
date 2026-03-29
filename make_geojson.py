import json

geojson = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"zoneId": "Z001", "name": "Downtown Tampa", "kind": "zone"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-82.464, 27.940], [-82.450, 27.940], [-82.450, 27.955], [-82.464, 27.955], [-82.464, 27.940]]]
      }
    },
    {
      "type": "Feature",
      "properties": {"zoneId": "Z002", "name": "Ybor City", "kind": "zone"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-82.448, 27.955], [-82.430, 27.955], [-82.430, 27.965], [-82.448, 27.965], [-82.448, 27.955]]]
      }
    },
    {
      "type": "Feature",
      "properties": {"zoneId": "Z003", "name": "South Tampa", "kind": "zone"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-82.520, 27.870], [-82.470, 27.870], [-82.470, 27.925], [-82.520, 27.925], [-82.520, 27.870]]]
      }
    },
    {
      "type": "Feature",
      "properties": {"zoneId": "Z004", "name": "North Tampa", "kind": "zone"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-82.480, 28.020], [-82.420, 28.020], [-82.420, 28.080], [-82.480, 28.080], [-82.480, 28.020]]]
      }
    },
    {
      "type": "Feature",
      "properties": {"zoneId": "Z005", "name": "East Tampa", "kind": "zone"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-82.420, 27.960], [-82.380, 27.960], [-82.380, 28.000], [-82.420, 28.000], [-82.420, 27.960]]]
      }
    }
  ]
}

with open("frontend/public/data/tampa_data.json", "w") as f:
    json.dump(geojson, f, indent=2)

print("GeoJSON generated.")
