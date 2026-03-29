# Data Dictionary - Column Definitions

## Input Data (Loaded in Step 1)

### Census Data (`sample_census_data.csv`)
| Column | Type | Range | Meaning |
|--------|------|-------|---------|
| Zone_ID | Text | e.g. Z001 | Unique geographic identifier (PRIMARY KEY) |
| Zone_Name | Text | - | Name of the zone/neighborhood |
| Population | Integer | 0+ | Total population in zone |
| Median_Income | Integer | $/year | Typical household income |
| Pct_Elderly | Float | 0-100 | Percentage of population 65+ years |
| Pct_Children | Float | 0-100 | Percentage of population <18 years |
| Pct_Poverty | Float | 0-100 | Percentage below poverty line |

### Flood Zone Data (`sample_flood_data.csv`)
| Column | Type | Range | Meaning |
|--------|------|-------|---------|
| Zone_ID | Text | e.g. Z001 | Geographic identifier (must match census) |
| Flood_Zone | Text | A, AE, X | FEMA flood zone classification |
| Elevation_ft | Float | feet | Average land elevation above sea level |
| Flood_Exposure_Score | Float | 0-100 | How exposed to flooding (0=safe, 100=very exposed) |
| Repeat_Flood_Events_10y | Integer | 0+ | Number of damaging floods in past 10 years |

### Roads/Infrastructure Data (`sample_roads_data.csv`)
| Column | Type | Range | Meaning |
|--------|------|-------|---------|
| Zone_ID | Text | e.g. Z001 | Geographic identifier |
| Road_ID | Text | e.g. R101 | Unique road identifier |
| Road_Type | Text | Highway, Primary, Secondary | Classification of road |
| Elevation_ft | Float | feet | Road elevation |
| Flood_Risk_Level | Text | Critical, High, Medium, Low | Risk level for specific road |

### Facilities Data (`sample_facilities_data.csv`)
| Column | Type | Range | Meaning |
|--------|------|-------|---------|
| Facility_ID | Text | e.g. F001 | Unique facility identifier |
| Zone_ID | Text | e.g. Z001 | Geographic identifier |
| Facility_Type | Text | Hospital, School, Shelter | Type of critical facility |
| Accessibility_Score | Float | 0-100 | How easy to reach (0=isolated, 100=easy) |
| Elevation_ft | Float | feet | Facility elevation |

---

## Processed Data (After merging - `output/combined_data.csv`)

All input columns PLUS:
| Column | Type | Range | Meaning |
|--------|------|-------|---------|
| Num_Facilities | Integer | 0+ | Total facilities in zone |
| Avg_Facility_Accessibility | Float | 0-100 | Average accessibility of all facilities |
| Min_Facility_Elevation | Float | feet | Lowest facility elevation |

---

## Features (After engineering - `output/features_engineered.csv`)

All combined data PLUS:
| Column | Type | Range | Meaning |
|--------|------|-------|---------|
| Flood_Exposure_Norm | Float | 0-100 | Normalized flood exposure (0=safe, 100=very exposed) |
| Elevation_Risk | Float | 0-100 | Risk from low elevation (0=high, 100=low = safe) |
| Road_Access_Weakness | Float | 0-100 | Risk from poor road access (0=good, 100=very poor) |
| Population_Vulnerability | Float | 0-100 | Vulnerability of population (0=strong, 100=vulnerable) |
| Facility_Access_Risk | Float | 0-100 | Risk from distant hospitals/shelters (0=close, 100=far) |

---

## Final Results (After scoring - `output/fragility_scores_*.csv`)

### fragility_scores_summary.csv
| Column | Type | Range | Meaning |
|--------|------|-------|---------|
| Zone_ID | Text | e.g. Z001 | Unique zone identifier |
| Zone_Name | Text | - | Zone name |
| Fragility_Score | Float | 0-100 | **MAIN RESULT**: Overall vulnerability (0=resilient, 100=fragile) |
| Risk_Category | Text | CRITICAL, HIGH, MODERATE, LOW, MINIMAL | **Category for quick identification** |
| Fragility_Rank | Integer | 1-N | **Ranking** (1=most fragile, highest number=safest) |
| Population | Integer | 0+ | Number of people in zone |
| Elevation_ft | Float | feet | Average elevation |

### zones_ranked_by_fragility.csv (Simplified version for priority planning)
Same columns as fragility_scores_summary.csv but sorted by rank (most fragile first).

### insights_for_webapp.csv
| Column | Type | Meaning |
|--------|------|---------|
| Zone_ID | Text | Zone identifier |
| Zone_Name | Text | Zone name |
| Fragility_Score | Float | Vulnerability score |
| Risk_Category | Text | Risk level |
| Fragility_Rank | Integer | Priority ranking |
| Insight_Summary | Text | **Why is this zone fragile?** (AI-generated explanation) |
| Key_Recommendations | Text | **What should be done?** (Action items) |

---

## Understanding the Fragility Score

### How It's Calculated

```
Fragility_Score = 
  (Flood_Exposure_Norm × 0.35) +
  (Elevation_Risk × 0.25) +
  (Population_Vulnerability × 0.20) +
  (Facility_Access_Risk × 0.15) +
  (Road_Access_Weakness × 0.05)
```

### Weights (Importance)
- **Flood Exposure (35%)**: Most important - if water reaches here, serious problems
- **Elevation Risk (25%)**: Low-lying areas are inherently vulnerable
- **Population Vulnerability (20%)**: Elderly, children, poor need more help
- **Facility Access (15%)**: Can people reach hospitals/shelters?
- **Road Access (5%)**: Can people evacuate?

### Interpretation

| Score | Meaning | Status | Action |
|-------|---------|--------|--------|
| 75-100 | CRITICAL | Immediate danger | Act now (days) |
| 60-75 | HIGH | High vulnerability | Plan urgently (weeks) |
| 40-60 | MODERATE | Some risk | Plan (months) |
| 25-40 | LOW | Minor risk | Monitor (yearly) |
| 0-25 | MINIMAL | Safe | Routine (as-needed) |

### Example Scores

**Score 90 (CRITICAL)**
- Flood Exposure: 95/100 (floods here often)
- Elevation: 85/100 (very low-lying)
- Population: 70/100 (many vulnerable people)
- Facilities: 80/100 (hard to reach)
- Roads: 60/100 (some access issues)

**Score 35 (LOW)**
- Flood Exposure: 20/100 (rarely floods)
- Elevation: 30/100 (mostly safe elevation)
- Population: 40/100 (reasonably strong population)
- Facilities: 40/100 (good access)
- Roads: 50/100 (good roads)

---

## Key Metrics in Results

### Flood Risk Factors
- **Flood_Exposure_Score**: Percentile of flood exposure (higher = more at risk)
- **Repeat_Flood_Events_10y**: Times zone has flooded in past decade
- **Elevation_ft**: Height above sea level (critical: <5ft = extreme risk)

### Population Risk Factors
- **Pct_Elderly**: Percentage 65+ (higher = more vulnerable)
- **Pct_Children**: Percentage <18 (higher = more vulnerable)
- **Pct_Poverty**: Percentage below poverty line (higher = less resilience)

### Infrastructure Risk Factors
- **Num_Facilities**: Count of hospitals, shelters, schools
- **Avg_Facility_Accessibility**: Average ease-of-reach score
- **Road_Type**: Classification (Highway > Primary > Secondary)

---

## How to Read the Output Files

### For Decision-Makers
**Read**: `zones_ranked_by_fragility.csv` (Ranked by urgency)
**Columns to focus on**: Zone_Name, Fragility_Score, Risk_Category

### For Planners
**Read**: `fragility_scores_summary.csv` (All scores + location)
**Columns to focus on**: All (create maps using Zone_ID + Fragility_Score)

### For Community Leaders
**Read**: `zone_insights_and_recommendations.txt` (Detailed explanations)
**Contains**: Why is my zone fragile? What should we do?

### For Web App Developers
**Read**: `insights_for_webapp.csv` (Ready to display)
**Columns to use**: Zone_Name, Fragility_Score, Risk_Category, Insight_Summary, Key_Recommendations

---

## Adjusting Weights (If Needed)

If you think some factors are more/less important:

1. Edit `04_calculate_fragility_score.py`
2. Change weights (must sum to 1.0):
   ```python
   weights = {
       'Flood_Exposure_Norm': 0.40,           # Increase if flood is priority
       'Elevation_Risk': 0.25,
       'Population_Vulnerability': 0.20,
       'Facility_Access_Risk': 0.10,          # Decrease if facilities are plentiful
       'Road_Access_Weakness': 0.05
   }
   ```
3. Re-run Step 4
4. Scores automatically update

Example scenarios:
- **Prioritize flood first**: Increase Flood_Exposure to 0.50, lower others
- **Focus on vulnerable people**: Increase Population_Vulnerability to 0.30
- **Emphasize evacuation routes**: Increase Road_Access to 0.15, lower Facility_Access to 0.10

---

## Data Quality Notes

### What Causes Missing Values?
- Zone has no facilities nearby
- Road data not available for zone
- Census tract boundaries don't align with zones
- Data collection incomplete for area

### How Are They Handled?
- **Step 2**: Filled with median (numeric) or 'Unknown' (text)
- **Step 3**: Features calculated with available data
- **Step 4**: Zeros treated as "neutral" (average of 50 in some scores)

### Best Practice
- Always check original data sources for missing areas
- Document "no data" zones separately
- Flag for field verification on ground truth

