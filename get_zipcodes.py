import requests
import json
import os

query = """
[out:json][timeout:90];
area["name"="Tampa"]->.searchArea;
(
  relation["boundary"="zip_code"](area.searchArea);
  relation["boundary"="postal_code"](area.searchArea);
  way["boundary"="postal_code"](area.searchArea);
);
out geom;
"""
response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=100)
data = response.json()
print("Got results:", len(data.get("elements", [])))
