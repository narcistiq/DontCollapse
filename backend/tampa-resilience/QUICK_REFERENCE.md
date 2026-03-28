# QUICK REFERENCE CARD
## Tampa Bay Water Resilience Scoring System

---

## ⚡ 5-Minute Start

```bash
pip install -r requirements.txt
python 01_load_data.py
python 02_merge_data.py
python 03_feature_engineering.py
python 04_calculate_fragility_score.py
python 05_generate_insights.py
```

**Results** → `output/zones_ranked_by_fragility.csv`

---

## 🎯 Fragility Score at a Glance

| Score | Risk | Status | Action |
|-------|------|--------|--------|
| **75-100** | CRITICAL | 🔴 | **ACT NOW** |
| **60-75** | HIGH | 🟠 | **URGENT** |
| **40-60** | MODERATE | 🟡 | **PLAN** |
| **25-40** | LOW | 🟢 | **MONITOR** |
| **0-25** | MINIMAL | ✅ | **SAFE** |

---

## 📊 What Gets Measured

**Flood Exposure (35%)** - Historical floods + water risk
**Elevation (25%)** - How high (low = bad)
**Population (20%)** - Vulnerable groups (elderly, poor, children)
**Facilities (15%)** - Access to hospitals, shelters, schools
**Roads (5%)** - Evacuation route quality

---

## 📁 Output Files

| File | Use |
|------|-----|
| `zones_ranked_by_fragility.csv` | **Main result** - who to help first |
| `fragility_scores_summary.csv` | For mapping + analysis |
| `insights_for_webapp.csv` | For web dashboard |
| `zone_insights_and_recommendations.txt` | Detailed explanations |
| `executive_summary.txt` | Report for stakeholders |

---

## 🔧 Customize Weights

Edit `04_calculate_fragility_score.py`:

```python
weights = {
    'Flood_Exposure_Norm': 0.35,      # ← Adjust these (sum = 1.0)
    'Elevation_Risk': 0.25,
    'Population_Vulnerability': 0.20,
    'Facility_Access_Risk': 0.15,
    'Road_Access_Weakness': 0.05
}
```

Then re-run Step 4.

---

## 📖 Key Files

| File | Purpose |
|------|---------|
| `README.md` | Start here |
| `GUIDE.md` | Complete plan |
| `INDEX.md` | Document index |
| `DATA_DICTIONARY.md` | Column definitions |
| `DASHBOARD_GUIDE.md` | Build web app |

---

## ✅ Success Checklist

- [ ] Ran all 5 Python scripts
- [ ] Reviewed output files
- [ ] Understand fragility score formula
- [ ] Can explain what factors were included
- [ ] Have results ready for stakeholders

---

## ❓ Common Questions

**Q: What's the scale?**
A: 0-100, where higher = more fragile/at-risk

**Q: Can I change weights?**
A: Yes! Edit Step 4, make sure they sum to 1.0

**Q: How do I add more zones?**
A: Add rows to sample CSV files and re-run

**Q: How do I visualize on a map?**
A: See DASHBOARD_GUIDE.md

**Q: What if scores don't match reality?**
A: 1) Check data quality, 2) Adjust weights, 3) Add more factors

---

## 🚀 Next Steps

1. Run the 5 scripts ✓
2. Review results ✓
3. Customize if needed
4. **Build dashboard** (see DASHBOARD_GUIDE.md)
5. Share with stakeholders

---

## 📞 Syntax Cheat Sheet

### Run a script:
```bash
python 01_load_data.py
```

### Install packages:
```bash
pip install pandas numpy
```

### Common pandas operations (in Python):
```python
import pandas as pd

df = pd.read_csv('file.csv')              # Load
df.head()                                  # See first 5 rows
df.describe()                              # Statistics
df.columns                                 # See column names
df[df['Column'] > 50]                     # Filter rows
df.sort_values('Column')                  # Sort
df.to_csv('output.csv', index=False)     # Save
```

---

## 📍 File Locations

```
tampa-resilience/
├── 01_load_data.py              # STEP 1
├── 02_merge_data.py             # STEP 2
├── 03_feature_engineering.py    # STEP 3
├── 04_calculate_fragility_score.py # STEP 4
├── 05_generate_insights.py      # STEP 5
├── data/                        # Sample data (created by Step 1)
├── output/                      # Results (created by Step 5)
├── README.md                    # START HERE
├── GUIDE.md                     # Full plan
├── INDEX.md                     # This document
├── DATA_DICTIONARY.md           # Column definitions
└── DASHBOARD_GUIDE.md           # Build web app
```

---

## 🎯 What You Achieve

✅ **Fragility Scores** - Know which zones are most vulnerable
✅ **Rankings** - Clear priority order for action
✅ **Insights** - Understand why each zone is fragile
✅ **Recommendations** - Know what to do about it
✅ **Data Ready** - Prepared for web visualization

---

## 💡 Pro Tips

1. **Start small** - Use sample data first, then your data
2. **Check results** - Do scores match your intuition?
3. **Vary weights** - Test different priorities
4. **Engage community** - Validate results with locals
5. **Iterate** - Keep improving as you learn

---

**Print this page or bookmark it!** 📌

---

**Version 1.0 | Questions? See INDEX.md or README.md**
