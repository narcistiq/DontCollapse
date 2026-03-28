# Building a Web Dashboard for the Fragility Scores

## Overview

Once you have the fragility scores, you can build a web app/dashboard that lets users:
- View interactive map of zones colored by fragility
- Select flood scenario (rainfall, storm surge, sea-level rise)
- Click on zones to see insights & recommendations
- View ranking of vulnerabilities

This guide shows 3 different approaches, from simplest to most feature-rich.

---

## Option 1: Simple Web App (Easiest - No GIS Experience)

### What You'll Build
- Table showing all zones ranked by fragility
- Color-coded by risk category
- Click each zone to see detailed insights
- Shows insights generated in Step 5

### Tools Needed
- Python Flask (simple web framework)
- HTML/CSS (basic web design)
- Bootstrap (CSS styling - makes it look nice)

### Time Required
- 2-3 hours if familiar with Python
- 4-5 hours if new to web apps

### Basic Structure

```
dashboard/
├── app.py                    (Flask server)
├── templates/
│   ├── index.html           (Main page)
│   └── zone_detail.html     (Zone detail view)
├── static/
│   └── style.css            (Styling)
└── data/
    └── insights_for_webapp.csv  (Output from Step 5)
```

### Simple Flask Example

**app.py:**
```python
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Load fragility scores
df = pd.read_csv('data/insights_for_webapp.csv')

@app.route('/')
def index():
    """Show ranking of all zones"""
    zones = df.sort_values('Fragility_Rank').to_dict('records')
    return render_template('index.html', zones=zones)

@app.route('/zone/<zone_id>')
def zone_detail(zone_id):
    """Show details for one zone"""
    zone = df[df['Zone_ID'] == zone_id].iloc[0]
    return render_template('zone_detail.html', zone=zone)

if __name__ == '__main__':
    app.run(debug=True)
```

**templates/index.html (simplified):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Tampa Bay Resilience</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        .critical { background-color: #ff4444; }
        .high { background-color: #ff8800; }
        .moderate { background-color: #ffdd00; }
        .low { background-color: #88ff88; }
    </style>
</head>
<body>
    <h1>Tampa Bay Water Resilience Assessment</h1>
    <table>
        <tr>
            <th>Rank</th>
            <th>Zone</th>
            <th>Score</th>
            <th>Risk Level</th>
            <th>Action</th>
        </tr>
        {% for zone in zones %}
        <tr class="{{ zone['Risk_Category'].lower() }}">
            <td>{{ zone['Fragility_Rank'] }}</td>
            <td>{{ zone['Zone_Name'] }}</td>
            <td>{{ zone['Fragility_Score'] }}</td>
            <td>{{ zone['Risk_Category'] }}</td>
            <td><a href="/zone/{{ zone['Zone_ID'] }}">View Details</a></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
```

### Installation & Running

```bash
# Install Flask
pip install flask

# Run the app
python app.py

# Go to http://localhost:5000 in your browser
```

---

## Option 2: Add Interactive Map (Moderate - Some GIS)

### What You'll Build
- Interactive map showing zones colored by fragility
- Click on zone to see details
- Color scale: red (critical) → yellow (moderate) → green (safe)

### Tools Needed
- Folium (Python library for maps)
- Geojson or Shapefile (zone boundaries - optional)
- GeoJSON format for zones

### Time Required
- 3-4 hours if you have GeoJSON files
- 6-8 hours if you need to create GeoJSON first

### Python Code Example

```python
import folium
import pandas as pd
import json

# Load scores and zones
df = pd.read_csv('output/fragility_scores_summary.csv')

# Load GeoJSON with zone boundaries
# (Download from county GIS or create from shapefile)
with open('data/tampa_zones.geojson', 'r') as f:
    geojson_data = json.load(f)

# Create base map (centered on Tampa)
m = folium.Map(
    location=[27.9506, -82.4573],  # Tampa, FL
    zoom_start=10
)

# Color scale: red (high fragility) to green (low fragility)
def get_color(score):
    if score >= 75:
        return '#ff0000'  # Red - critical
    elif score >= 60:
        return '#ff8800'  # Orange - high
    elif score >= 40:
        return '#ffff00'  # Yellow - moderate
    else:
        return '#00ff00'  # Green - low

# Add zones to map
for feature in geojson_data['features']:
    zone_id = feature['properties']['Zone_ID']
    
    # Get score for this zone
    row = df[df['Zone_ID'] == zone_id]
    if len(row) > 0:
        score = row['Fragility_Score'].values[0]
        risk = row['Risk_Category'].values[0]
        
        # Add to map
        folium.GeoJson(
            feature,
            style_function=lambda x, score=score: {
                'fillColor': get_color(score),
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.7
            },
            popup=f"{zone_id}: {risk} ({score})"
        ).add_to(m)

# Save map
m.save('map.html')
print("Map saved to map.html - open in browser!")
```

### Getting Zone Boundaries

**Option A: Download from county GIS**
- Hillsborough County: https://gis.hillsboroughcounty.org/
- Download shapefile → convert to GeoJSON

**Option B: Create simple circles (no boundary data)**
```python
# If you don't have zone boundaries, use circles
for idx, row in df.iterrows():
    folium.Circle(
        location=[row['Latitude'], row['Longitude']],
        radius=row['Population']/10,  # Size by population
        popup=row['Zone_Name'],
        color=get_color(row['Fragility_Score']),
        fill=True,
        fillColor=get_color(row['Fragility_Score'])
    ).add_to(m)
```

---

## Option 3: Full Dashboard (Advanced - Professional)

### What You'll Build
- Full web dashboard with:
  - Interactive map (Mapbox or Leaflet)
  - Flood scenario selector (rainfall, surge, sea-level rise)
  - Filter by risk category
  - Export data
  - Real-time updates from database

### Tech Stack
- **Frontend**: React.js or Vue.js
- **Backend**: Python FastAPI or Node.js
- **Database**: PostgreSQL with PostGIS
- **Mapping**: Mapbox GL JS or Leaflet
- **Deployment**: AWS, Heroku, or DigitalOcean

### Time Required
- 1-2 weeks if experienced with web apps
- 3-4 weeks if learning as you go

### High-level Architecture

```
┌─────────────────────────────────────────┐
│         WEB BROWSER (User)              │
│  ┌─────────────────────────────────┐   │
│  │  React/Vue Dashboard            │   │
│  │  - Map visualization            │   │
│  │  - Scenario selector            │   │
│  │  - Zone details panel           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
             │ (HTTP API calls)
┌─────────────────────────────────────────┐
│     BACKEND SERVER (FastAPI/Python)     │
│  ┌─────────────────────────────────┐   │
│  │  API Endpoints:                 │   │
│  │  /zones                         │   │
│  │  /zones/{id}                    │   │
│  │  /fragility_scores              │   │
│  │  /scenario/{rainfall|surge}     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
             │ (SQL queries)
┌─────────────────────────────────────────┐
│      DATABASE (PostgreSQL + PostGIS)    │
│  ┌─────────────────────────────────┐   │
│  │  Tables:                        │   │
│  │  - zones (geometry + data)      │   │
│  │  - fragility_scores             │   │
│  │  - scenarios                    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Minimal FastAPI Backend Example

```python
from fastapi import FastAPI
import pandas as pd
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Load data
df = pd.read_csv('output/fragility_scores_summary.csv')

@app.get("/zones")
def get_zones():
    """Get all zones with scores"""
    return df.to_dict('records')

@app.get("/zones/{zone_id}")
def get_zone(zone_id: str):
    """Get specific zone details"""
    zone = df[df['Zone_ID'] == zone_id]
    if len(zone) > 0:
        return zone.iloc[0].to_dict()
    return {"error": "Zone not found"}

@app.get("/fragility_scores")
def get_scores(risk_category: str = None):
    """Get zones, optionally filtered by risk"""
    if risk_category:
        filtered = df[df['Risk_Category'] == risk_category]
        return filtered.to_dict('records')
    return df.to_dict('records')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Recommended Next Steps

### Phase 1 (Weeks 1-2): Get Option 1 Working
- Build simple Flask app
- Display ranking table
- Show insights page
- Deploy locally

### Phase 2 (Weeks 3-4): Add Maps
- Get zone boundaries (GeoJSON)
- Add Folium map visualization
- Deploy to Heroku (free tier)

### Phase 3 (Weeks 5+): Build Full Dashboard
- Migrate to React + FastAPI
- Add database
- Implement flood scenarios
- Add real-time updates

---

## Flood Scenarios (Adding Later)

Once you have the base dashboard, you can add scenario analysis:

```python
# Different scenarios adjust fragility scores differently

def apply_scenario(df, scenario):
    """Adjust scores based on flood scenario"""
    df_scenario = df.copy()
    
    if scenario == 'heavy_rainfall':
        # Rainfall affects low elevation areas more
        df_scenario['Fragility_Score'] += df_scenario['Elevation_Risk'] * 0.1
        
    elif scenario == 'storm_surge':
        # Storm surge affects flood exposure + elevation
        df_scenario['Fragility_Score'] += (
            df_scenario['Flood_Exposure_Norm'] * 0.2 +
            df_scenario['Elevation_Risk'] * 0.15
        )
        
    elif scenario == 'sea_level_rise':
        # SLR permanently increases low elevation risk
        df_scenario['Elevation_Risk'] = df_scenario['Elevation_Risk'] * 1.2
        df_scenario['Fragility_Score'] = recalculate_scores(df_scenario)
    
    # Cap at 100
    df_scenario['Fragility_Score'] = df_scenario['Fragility_Score'].clip(0, 100)
    
    return df_scenario

# Use in API:
@app.get("/scenario/{scenario_type}")
def get_scenario_scores(scenario_type: str):
    scores = apply_scenario(df, scenario_type)
    return scores.to_dict('records')
```

---

## Hosting Options

### Free/Cheap (Starting Out)
- **Heroku** (Flask/FastAPI): Free tier available, then ~$7/month
- **GitHub Pages** (Static dashboards): Completely free
- **Vercel** (React frontend): Free tier
- **Render.com** (Backend): Free tier, then pay-as-you-go

### Medium (Production-Ready)
- **AWS**: $20-100/month (with free tier)
- **DigitalOcean**: $5-20/month (super affordable)
- **Azure**: $20-50/month

### Enterprise
- Run on city government servers
- Share with stakeholders via VPN
- Enterprise databases & support

---

## A Complete Checklist

- [ ] Step 1-5: Run Python pipeline (get fragility scores)
- [ ] Option 1a: Build simple Flask table app
- [ ] Option 1b: Deploy Flask app to Heroku
- [ ] Option 2a: Get zone boundaries (GeoJSON)
- [ ] Option 2b: Add Folium map to app
- [ ] Option 3a: Build React frontend (if desired)
- [ ] Option 3b: Migrate to FastAPI backend
- [ ] Option 3c: Set up PostgreSQL database
- [ ] Option 3d: Deploy full dashboard
- [ ] Final: Share with stakeholders

---

## Getting Help

### Learning Resources
- **Flask tutorial**: https://flask.palletsprojects.com/
- **React tutorial**: https://react.dev/
- **Folium examples**: https://python-visualization.github.io/folium/
- **Mapbox examples**: https://docs.mapbox.com/

### GIS Tools
- **QGIS** (free desktop tool): https://www.qgis.org/
- **MapShaper** (online tool): https://mapshaper.org/
- **GeoJSON.io** (online GeoJSON editor): https://geojson.io/

### Community Resources
- Stack Overflow (Python, React, Flask questions)
- GitHub Discussions (open source projects)
- Local tech meetups (find Python/web dev groups)

---

## Next Document to Read

Once you're comfortable with Option 1, read through Option 2 to add maps.

Good luck building your dashboard! 🗺️

