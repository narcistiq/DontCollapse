# Tampa Bay Water Resilience Scoring System

## Quick Start

This project helps you identify which parts of Tampa Bay are most vulnerable to water-related flooding and why.

### What You Need

- **Python 3.7+** with pandas installed
- **Data files** (we provide sample data to get started)
- **30 minutes** to run through all steps

### Install Dependencies

```bash
pip install pandas numpy
```

### Run the Complete Analysis (5 Steps)

```bash
# Step 1: Load and explore data
python 01_load_data.py

# Step 2: Combine datasets by location
python 02_merge_data.py

# Step 3: Create vulnerability features
python 03_feature_engineering.py

# Step 4: Calculate fragility scores
python 04_calculate_fragility_score.py

# Step 5: Generate insights & recommendations
python 05_generate_insights.py
```

### Output Files (in `output/` folder)

- **fragility_scores_summary.csv** - Use for mapping (has coordinates if available)
- **zones_ranked_by_fragility.csv** - Ranking from most to least fragile
- **zone_insights_and_recommendations.txt** - Detailed explanations for each zone
- **insights_for_webapp.csv** - Ready to load into web app
- **executive_summary.txt** - Report for stakeholders

---

## What Each Step Does

### Step 1: Load & Explore Data
- Loads sample CSV files (census, flood, roads, facilities)
- Shows what the data looks like
- Creates clean, standardized format
- **Time**: ~1 minute

### Step 2: Merge Data by Location
- Combines all datasets using Zone_ID as the "glue"
- One row per zone with all information
- Handles missing values
- **Time**: ~1 minute

### Step 3: Feature Engineering
- Creates 5 vulnerability factors (0-100 scale):
  1. **Flood Exposure**: Does water reach here?
  2. **Elevation Risk**: How high is the land?
  3. **Road Access**: Can people evacuate?
  4. **Population Vulnerability**: Who needs help?
  5. **Facility Access**: Can people reach hospitals/shelters?
- **Time**: ~1 minute

### Step 4: Calculate Fragility Score
- Combines all 5 factors into ONE score (0-100)
- Ranks zones by fragility (1 = most fragile)
- Categorizes into risk levels (CRITICAL, HIGH, MODERATE, LOW, MINIMAL)
- **Time**: ~1 minute

### Step 5: Generate Insights
- Creates human-readable explanations
- Generates actionable recommendations per zone
- Produces summary reports
- **Time**: ~1 minute

---

## Understanding the Fragility Score

**Fragility Score**: 0-100 scale showing how vulnerable an area is to water-related stress

### Formula (Weighted Average)
```
Fragility = 
  (Flood Exposure × 0.35) +
  (Elevation Risk × 0.25) +
  (Population Vulnerability × 0.20) +
  (Facility Access Risk × 0.15) +
  (Road Access Weakness × 0.05)
```

### Risk Categories
| Score | Category | Status |
|-------|----------|--------|
| 75-100 | CRITICAL | Immediate action needed |
| 60-75 | HIGH | Urgent attention required |
| 40-60 | MODERATE | Planning needed |
| 25-40 | LOW | Monitor situation |
| 0-25 | MINIMAL | Currently safe |

### Example Interpretation
- **Score 85 (CRITICAL)**: This zone has high flood exposure, low elevation, vulnerable population, and limited facility access. Multiple reinforcing factors drive up the score.
- **Score 45 (MODERATE)**: This zone has some risks but also some strengths. Strategic improvements could significantly reduce vulnerability.

---

## Using Your Own Data

The sample data is just for learning. To use real data:

### 1. Replace Sample Files
Edit the CSV files in the `data/` folder:
- `sample_census_data.csv` → your census data
- `sample_flood_data.csv` → your flood zone/exposure data
- `sample_roads_data.csv` → your road network data
- `sample_facilities_data.csv` → your hospital/shelter data

### 2. Adjust Column Names
In each script, update column names to match your data:
```python
# Old (sample data)
df_census = pd.read_csv('data/sample_census_data.csv')

# New (your data)
df_census = pd.read_csv('data/your_census_data.csv')
```

### 3. Adjust Feature Calculations
In `03_feature_engineering.py`, update the feature calculations to match your column names and ranges.

---

## Understanding the Code

### Key Pandas Operations

**Read CSV:**
```python
df = pd.read_csv('data/file.csv')
```

**Show first 5 rows:**
```python
df.head()
```

**Statistics:**
```python
df.describe()
```

**Merge tables:**
```python
df_merged = df1.merge(df2, on='Zone_ID', how='left')
```

**Normalize to 0-100:**
```python
(value - min) / (max - min) * 100
```

**Create new column:**
```python
df['New_Column'] = df['Column1'] * 2 + df['Column2']
```

### Key Concepts

**DataFrame**: Table with rows (zones) and columns (attributes)

**Zone_ID**: The common identifier that connects all datasets

**Normalization**: Scaling different measurements to same 0-100 range

**Weighting**: Different factors have different importance (flood exposure = 35%, elevation = 25%, etc.)

**Fragility Score**: Final composite measure combining all factors

---

## Next: Build a Web Dashboard

Once you have the fragility scores, you can build a web app to visualize them:

### Option 1: Simple Flask Web App (No GIS Experience Needed)
```python
# Display rankings as interactive table
# Show insights when user clicks a zone
# Color-code by risk category
```

### Option 2: Add Interactive Maps (Requires Geospatial Data)
- Use **Folium** (Python) or **Mapbox/Leaflet** (JavaScript)
- Show zone boundaries + color by fragility score
- Add flood scenarios (rainfall, surge, sea-level rise)

### Option 3: Full Dashboard (Advanced)
- React/Vue.js frontend
- Python backend (Flask/FastAPI)
- PostgreSQL database
- Real-time data updates

---

## Customizing Weights

The fragility score weights can be adjusted based on your priorities:

**Current weights:**
```
Flood Exposure:      35% (most important)
Elevation Risk:      25%
Population Vuln:     20%
Facility Access:     15%
Road Access:          5%
```

**To change weights**, edit `04_calculate_fragility_score.py`:

```python
weights = {
    'Flood_Exposure_Norm': 0.40,           # Increased
    'Elevation_Risk': 0.25,
    'Population_Vulnerability': 0.20,
    'Facility_Access_Risk': 0.10,          # Decreased
    'Road_Access_Weakness': 0.05
}
```

Then re-run Step 4. Scores will update automatically.

---

## Troubleshooting

### Error: "No such file or directory"
- Make sure you're in the project folder
- Run `python 01_load_data.py` first (creates sample data)

### Error: "KeyError: 'Column_Name'"
- Column name doesn't exist in your data
- Check CSV files and spelling
- Use `df.columns` to see all column names

### Scores don't look right
- Check data ranges (are values in expected range?)
- Verify normalization (0-100 scale?)
- Review weights (sum to 1.0?)
- Run Step 5 insights to see breakdown

### Missing data (NaN values)
- Normal after merge if not all zones have all data
- Scripts automatically fill with median/mean
- Check data quality in Step 1

---

## Data Sources for Tampa Bay

### Public Datasets (Beginner-Friendly)

1. **FEMA Flood Maps**: https://msc.fema.gov/portal/home
   - Free flood zone shapefiles
   - Download for Hillsborough, Pinellas, Pasco counties

2. **Census Data**: https://data.census.gov/
   - Population, income, age, vulnerability metrics
   - Download by county

3. **OpenStreetMap**: https://overpass-turbo.eu/
   - Roads, hospitals, schools, shelters
   - Free, always updated

4. **USGS Elevation**: https://earthexplorer.usgs.gov/
   - Terrain elevation (DEM - Digital Elevation Model)
   - Free 30m resolution

5. **Local Government**:
   - Hillsborough County GIS: https://gis.hillsboroughcounty.org/
   - City of Tampa Open Data: https://data.tampagov.net/
   - Pinellas County GIS: https://www.pinellascounty.org/gis/

---

## Common Questions

**Q: Can I use this with satellite data or real-time sensors?**
A: Yes! Just add new columns to your CSV files and include them in feature engineering.

**Q: How often should I update scores?**
A: When major changes occur (new infrastructure, new flooding events, demographic shifts). Quarterly/annually recommended.

**Q: What if my data has different geographic units (blocks, tracts, grids)?**
A: Works with any geographic unit. Just make sure all datasets use the same unit (Zone_ID).

**Q: How do I explain this to non-technical stakeholders?**
A: Show the fragility scores as maps + the insights generated in Step 5. Color-code by risk category.

**Q: Can I add more features?**
A: Absolutely! Just add the calculation in Step 3 and update the weights in Step 4.

---

## License & Attribution

This project uses public data sources (FEMA, Census Bureau, OpenStreetMap, USGS).
Always credit data sources when sharing results.

---

## Support & Questions

For help with:
- **Python/pandas**: Search "pandas [topic]" on docs.pandas.pydata.org
- **GIS data**: Watch "QGIS tutorial" on YouTube (free GIS tool)
- **Flood science**: Read FEMA flood risk documents
- **Web dashboards**: Follow Flask or React tutorials

Good luck with your resilience assessment! 🌊

