# Tampa Bay Water Resilience Scoring System - Beginner's Guide

## Overview
This guide will help you build a vulnerability assessment tool that scores how fragile different areas of Tampa Bay are under water-related stress.

---

## STEP-BY-STEP PLAN

### Phase 1: Data Collection & Setup
- [ ] Identify and download public datasets
- [ ] Understand the structure of each dataset
- [ ] Set up Python environment with pandas

### Phase 2: Data Loading & Exploration
- [ ] Load each dataset into pandas DataFrames
- [ ] Explore columns, data types, and missing values
- [ ] Clean and standardize data

### Phase 3: Data Combining
- [ ] Create common geographic identifiers (zones, coordinates)
- [ ] Merge datasets using location keys
- [ ] Handle missing data in merged dataset

### Phase 4: Feature Engineering
- [ ] Calculate flood exposure scores
- [ ] Calculate elevation/risk scores
- [ ] Measure road connectivity/access weakness
- [ ] Calculate distance to critical facilities (shelters, hospitals)
- [ ] Assess population vulnerability

### Phase 5: Fragility Score Calculation
- [ ] Weight and normalize individual features
- [ ] Combine features into composite fragility score
- [ ] Rank areas by vulnerability

### Phase 6: Output & Visualization Prep
- [ ] Export results to CSV/GeoJSON
- [ ] Prepare data for mapping
- [ ] Create summary statistics

---

## RECOMMENDED PUBLIC DATASETS FOR TAMPA BAY

### 1. **NOAA Sea Level Rise & Flood Exposure**
   - **What it is**: Flood risk maps and sea-level rise projections
   - **Source**: https://www.noaa.gov/Media/Facts-About-NOAA-Flood-Mapping
   - **Format**: GeoTIFF, Shapefiles
   - **For beginners**: Download pre-made flood zone maps (FEMA Flood Zones)
   - **Easy alternative**: FEMA Flood Map Service Center
   - **URL**: https://msc.fema.gov/portal/home
   - **How to use**: Provides flood zone classifications (A, AE, X, etc.)

### 2. **U.S. Census Bureau - Population & Demographic Data**
   - **What it is**: Population density, median income, age distribution by census tract
   - **Source**: https://data.census.gov/
   - **Format**: CSV, JSON
   - **For beginners**: Download by county (Hillsborough, Pinellas, Pasco) using data.census.gov
   - **Useful tables**: 
     - B01003: Total Population
     - B17001: Poverty Status
     - B25001: Housing Units
   - **How to use**: Identify vulnerable populations (low income, elderly, children)

### 3. **OpenStreetMap (OSM) - Roads & Infrastructure**
   - **What it is**: Road network, bridges, hospitals, schools, evacuation centers
   - **Source**: https://www.openstreetmap.org/ or https://overpass-turbo.eu/
   - **Format**: GeoJSON, Shapefiles, or XML
   - **For beginners**: Use tools like Overpass Turbo to download for Tampa Bay
   - **What to extract**:
     - Roads (classify by type: highway, primary, secondary)
     - Hospitals and clinics
     - Schools
     - Shelters
   - **How to use**: Calculate distances to critical facilities and assess road connectivity

### 4. **USGS Elevation Data (DEM)**
   - **What it is**: Digital Elevation Model - terrain height data
   - **Source**: https://www.usgs.gov/3dep/
   - **Or simpler**: https://earthexplorer.usgs.gov/
   - **Format**: Raster (GeoTIFF)
   - **For beginners**: Download 30m resolution DEM for Tampa Bay
   - **How to use**: Identify low-lying areas (elevation < 5 feet = high flood risk)

### 5. **EPA Stormwater & Drainage Data**
   - **What it is**: Stormwater outfalls, drainage basins, sewage systems
   - **Source**: EPA ENVIROMAP or State of Florida DEP
   - **URL**: https://www.epa.gov/waterdata
   - **For beginners**: Start with local county stormwater maps (Hillsborough County publishes them)
   - **How to use**: Assess drainage quality and flood exposure in each area

### 6. **Local Data - Tampa Bay Area**
   - **Hillsborough County**: https://gis.hillsboroughcounty.org/
   - **City of Tampa**: https://data.tampagov.net/
   - **Pinellas County**: https://www.pinellascounty.org/gis/
   - **Pasco County**: https://www.pasco-county.net/gis/

---

## SIMPLEST STARTING APPROACH (For Immediate Progress)

If you want to start TODAY without spending time downloading large GIS files:

### Option A: Use Pre-Made Data (Fastest)
1. Download **FEMA Flood Zone map** (simple shapefile) from FEMA MSC
2. Download **Census 2020 data** (CSV) as demographic data
3. Create a **synthetic road network** from OpenStreetMap (use Overpass Turbo query)
4. Use a **simplified elevation dataset** (can download a small GeoTIFF)

### Option B: Start with Sample CSV Data
Create and use sample datasets in CSV format that mimic real data structure:
- Sample flood zones (Zone, Exposure Score, Average Elevation)
- Sample census data (Zone, Population, Median Income, %Elderly)
- Sample roads (Road ID, Zone, Type, Condition)
- Sample facilities (Facility ID, Type, Zone, Coordinates)

---

## NEXT SECTION

Jump to `01_load_data.py` to start coding!

---

## Key Concepts for Beginners

**Geographic Unit**: We'll aggregate data by "zones" (could be:
- Census tracts
- Zip codes
- Custom grid cells
- Neighborhood boundaries

**Fragility Score**: A composite measure (0-100) representing how vulnerable an area is:
- Lower score = more resilient
- Higher score = more fragile/at-risk

**Features**: Individual components that feed into the fragility score:
- Flood exposure (does this area flood?)
- Elevation (how high is the land?)
- Road access (can people evacuate?)
- Population vulnerability (who lives here?)
- Facility access (can people reach help?)

