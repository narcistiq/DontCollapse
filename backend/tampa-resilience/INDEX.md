# Tampa Bay Water Resilience Scoring System
## Complete Project Index & Quick Reference

Welcome! This project helps you identify Tampa Bay neighborhoods most vulnerable to flooding and why.

---

## 📋 Project Overview

**What it does:**
- Combines public flood, elevation, population, and infrastructure data
- Calculates a "Fragility Score" (0-100) for each zone
- Ranks neighborhoods by vulnerability
- Generates AI-style insights and actionable recommendations

**Who is it for:**
- City planners and emergency managers
- Community organizations
- Environmental advocates
- Anyone building resilient cities

**Your outcome:**
- Fragility scores for Tampa Bay neighborhoods
- Clear rankings of where to prioritize action
- Data-driven justification for improvements
- Ready-to-use web dashboard data

---

## 📚 Files & When to Use Them

### START HERE

| File | Purpose | Read When |
|------|---------|-----------|
| **README.md** | Quick start guide | First thing you read |
| **GUIDE.md** | Complete step-by-step plan | Planning your workflow |

### EXECUTE THESE (In Order)

| Step | File | What It Does | Time |
|------|------|-------------|------|
| 1️⃣ | `01_load_data.py` | Load and explore data | 1 min |
| 2️⃣ | `02_merge_data.py` | Combine datasets by location | 1 min |
| 3️⃣ | `03_feature_engineering.py` | Create vulnerability factors | 1 min |
| 4️⃣ | `04_calculate_fragility_score.py` | Calculate final scores | 1 min |
| 5️⃣ | `05_generate_insights.py` | Generate explanations & recommendations | 1 min |

**Total runtime: ~5 minutes**

### REFERENCE DOCS

| File | Purpose | Use When |
|------|---------|----------|
| **DATA_DICTIONARY.md** | Explains all columns & metrics | Understanding data |
| **DASHBOARD_GUIDE.md** | How to build a web app | Visualizing results |
| **requirements.txt** | Python dependencies | Installing packages |

---

## 🚀 Quick Start (5 minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

(Just pandas and numpy - very lightweight)

### 2. Run All 5 Steps

```bash
python 01_load_data.py          # Create sample data
python 02_merge_data.py         # Combine by location
python 03_feature_engineering.py # Calculate features
python 04_calculate_fragility_score.py # Get fragility scores
python 05_generate_insights.py   # Generate insights
```

### 3. View Results

Open `output/zones_ranked_by_fragility.csv` to see which zones are most fragile.

### 4. Read Explanations

Open `output/zone_insights_and_recommendations.txt` to understand why.

---

## 📊 What Gets Calculated

### Fragility Score Formula

```
Fragility = 
  (Flood Exposure      × 35%) +
  (Elevation Risk      × 25%) +
  (Population Vuln     × 20%) +
  (Facility Access     × 15%) +
  (Road Access Weakness × 5%)
```

**Output: 0-100 scale**
- **75-100**: CRITICAL - Act immediately
- **60-75**: HIGH - Urgent attention
- **40-60**: MODERATE - Plan soon
- **25-40**: LOW - Monitor
- **0-25**: MINIMAL - Safe

### 5 Vulnerability Factors

1. **Flood Exposure** (35%)
   - How often does water reach here?
   - Historical flood events

2. **Elevation Risk** (25%)
   - How high is the land?
   - Areas <5 feet are at high risk

3. **Population Vulnerability** (20%)
   - Percentage elderly, children, poor
   - Who needs extra help during disasters?

4. **Facility Access Risk** (15%)
   - Distance to hospitals, shelters, schools
   - Can people evacuate?

5. **Road Access Weakness** (5%)
   - Road connectivity and elevation
   - Can vehicles move people safely?

---

## 📁 Output Files (What You Get)

### In `output/` folder after running:

| File | Contains | Use For |
|------|----------|---------|
| **fragility_scores_summary.csv** | All zones + scores + location | Mapping, analysis |
| **zones_ranked_by_fragility.csv** | Ranking 1 (most fragile) → N | Priority planning |
| **fragility_scores_full.csv** | All data + all calculations | Detailed analysis |
| **zone_insights_and_recommendations.txt** | Detailed explanations per zone | Understanding results |
| **insights_for_webapp.csv** | Ready for web app | Building dashboards |
| **executive_summary.txt** | High-level report | Stakeholder communication |

---

## 💡 Understanding Results

### Example: Most Fragile Zone

```
Zone: Downtown Tampa
Score: 87/100 (CRITICAL)
Rank: #1 (Most Fragile)

Why Critical:
  • Flood Exposure: 95/100 (flooded 3× in last 10 years)
  • Elevation: 82/100 (average 4 feet - very low)
  • Population: 72/100 (15% elderly, 14% children, 18% in poverty)
  • Facilities: 70/100 (some hospitals nearby but at risk too)
  • Roads: 55/100 (Main evacuation routes are low-lying)

What to Do:
  • Build permanent pumping station
  • Elevate critical evacuation routes
  • Establish community shelters on high ground
  • Create evacuation assistance for vulnerable groups
  • Partner with hospitals on emergency plans
```

### Example: Safe Zone

```
Zone: North Tampa
Score: 22/100 (MINIMAL)
Rank: #5 (Most Resilient)

Why Safe:
  • Flood Exposure: 15/100 (rarely floods)
  • Elevation: 25/100 (mostly 7-10 feet - safe)
  • Population: 35/100 (healthy mix, good income, few in poverty)
  • Facilities: 60/100 (several hospitals easily accessible)
  • Roads: 45/100 (good road network)

What to Do:
  • Routine monitoring
  • Maintain current infrastructure
  • Help neighboring vulnerable areas
```

---

## 🔧 Customization (Change Weights)

Don't like the 35-25-20-15-5 weights? Change them!

**Edit `04_calculate_fragility_score.py` and change these lines:**

```python
weights = {
    'Flood_Exposure_Norm': 0.35,           # Change this to 0.50 if flood is priority
    'Elevation_Risk': 0.25,                # Change this to 0.15 if elevation is less important
    'Population_Vulnerability': 0.20,
    'Facility_Access_Risk': 0.15,
    'Road_Access_Weakness': 0.05
}
# Must add up to 1.0!
```

Then re-run Step 4. Scores instantly update!

---

## 🌐 Next: Build a Web Dashboard

You now have the data. The next step is visualize it!

**See DASHBOARD_GUIDE.md for:**
- Simple web table (Flask, 2 hours)
- Interactive map (Folium, 4 hours)
- Full dashboard (React + database, 1-2 weeks)

---

## ❓ Frequently Asked Questions

**Q: Can I use this with different cities?**
A: Yes! Just replace the sample data with your city's data. Same process works.

**Q: How do I get real data instead of samples?**
A: See GUIDE.md "Recommended Public Datasets" section.

**Q: Can I add more factors?**
A: Absolutely! Edit Step 3 (feature engineering) and Step 4 (weights).

**Q: How often should I update?**
A: Quarterly or when major changes occur (new flooding, construction, etc.).

**Q: How do I explain this to non-technical people?**
A: Show the map (colored red→yellow→green) + the insights (human-readable explanations).

**Q: Our data is in different format (shapefile, GeoJSON)?**
A: Use a tool like QGIS or Python's geopandas to convert to simple CSV first.

---

## 📖 Document Reading Order

### For Beginners (New to this)
1. **README.md** - Overview and quick start
2. **GUIDE.md** - Understand the 5-step plan
3. Run the 5 Python scripts
4. **DATA_DICTIONARY.md** - Understand what each column means
5. **DASHBOARD_GUIDE.md** - Visualize the results

### For Data Analysts
1. **README.md** - Quick overview
2. **DATA_DICTIONARY.md** - Column definitions
3. Run Python scripts with your data
4. Customize weights as needed
5. Export to analysis tools (Excel, R, Tableau, etc.)

### For Web Developers
1. **README.md** - Quick start
2. Skip Python (or run once to understand)
3. **DASHBOARD_GUIDE.md** - Start with Option 1 (Flask)
4. Create web app using CSV outputs
5. Add maps when ready (Option 2 or 3)

### For Decision-Makers/Planners
1. **README.md** - Overview
2. **GUIDE.md** - Context on what's being measured
3. Ask analyst to run 5 steps
4. Review **output/executive_summary.txt**
5. Read **output/zone_insights_and_recommendations.txt**
6. Use **output/zones_ranked_by_fragility.csv** for prioritization

---

## 🛠️ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pandas'"
**Solution:** Run `pip install -r requirements.txt`

### Problem: Data looks wrong/scores don't make sense
**Solution:** 
1. Check the data in Step 1 output (describe statistics)
2. Verify values are in expected ranges
3. Review weight adjustments in Step 4
4. Run Step 5 insights to see breakdown

### Problem: Files not found
**Solution:** 
1. Make sure you're in the project directory
2. Run Step 1 first (creates sample data)
3. Check that data/ and output/ folders exist

### Problem: Want to use different data
**Solution:** See GUIDE.md → "Using Your Own Data" section

---

## 📞 Getting Help

### For Python/Pandas Questions
- Search "pandas [topic]" on officaial docs: docs.pandas.pydata.org
- YouTube "pandas tutorial"

### For GIS/Flood Science Questions
- FEMA Flood Maps: https://msc.fema.gov/portal/home
- NOAA Resources: https://www.noaa.gov/
- USGS Elevation Data: https://www.usgs.gov/3dep/

### For Web Development Questions
- Flask: https://flask.palletsprojects.com/
- React: https://react.dev/
- Folium: https://python-visualization.github.io/folium/

### For Tampa Bay Specific Data
- Hillsborough County GIS: https://gis.hillsboroughcounty.org/
- City of Tampa Data: https://data.tampagov.net/
- Pinellas County GIS: https://www.pinellascounty.org/gis/

---

## 🎯 Success Checklist

- [ ] Downloaded/cloned this project
- [ ] Installed Python dependencies (`pip install -r requirements.txt`)
- [ ] Ran all 5 Python scripts
- [ ] Reviewed output/ folder files
- [ ] Understand how fragility score was calculated
- [ ] Can explain what each output file contains
- [ ] Planned next steps (customize weights? build dashboard?)
- [ ] Shared results with stakeholders

---

## 📝 License & Attribution

This project uses public data:
- NOAA (flood, sea-level rise)
- FEMA (flood zones)
- Census Bureau (population)
- OpenStreetMap (roads, facilities)
- USGS (elevation)

Always credit your data sources in presentations!

---

## 🎓 Learn More

This project demonstrates:
- **Data engineering**: Loading, cleaning, combining data
- **Feature engineering**: Creating meaningful metrics
- **Scoring systems**: Combining factors into composite measure
- **Data visualization**: Presenting results clearly
- **Spatial analysis**: Working with geographic data
- **Community engagement**: Using data for actionable decisions

These concepts apply to many domains:
- Public health
- Economic development
- Environmental assessment
- Infrastructure planning
- Disaster response

---

## 🌟 That's It!

You now have a complete system for:
1. Identifying vulnerable areas
2. Understanding why they're vulnerable
3. Recommending specific improvements
4. Sharing results with communities

**Next step: Build your dashboard!** 🗺️

Read **DASHBOARD_GUIDE.md** to learn how.

---

## Version & Updates

- **Version**: 1.0
- **Created**: 2024
- **Status**: Ready to use
- **Last Updated**: [Current Date]

For updates and improvements, check the project repository.

---

Good luck with your resilience assessment! 💪

