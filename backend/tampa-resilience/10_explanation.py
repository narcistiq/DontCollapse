import pandas as pd

df = pd.read_csv("output/master_fragility_table.csv")

def explain(row):
    reasons = []

    if row["Flood_Exposure"] > 80:
        reasons.append("high flood exposure")
    if row["Elevation_Risk"] > 70:
        reasons.append("low elevation")
    if row["Road_Access_Risk"] > 70:
        reasons.append("poor road access")
    if row["Social_Vulnerability"] > 70:
        reasons.append("high social vulnerability")
    if row["Power_Infrastructure_Risk"] > 70:
        reasons.append("power infrastructure at risk")

    return ", ".join(reasons)

def recommend(row):
    actions = []

    if row["Flood_Exposure"] > 80:
        actions.append("improve drainage systems")
    if row["Elevation_Risk"] > 70:
        actions.append("elevate infrastructure")
    if row["Road_Access_Risk"] > 70:
        actions.append("reinforce evacuation routes")
    if row["Power_Infrastructure_Risk"] > 70:
        actions.append("upgrade power grid resilience")
    if row["Social_Vulnerability"] > 70:
        actions.append("increase emergency support services")

    return ", ".join(actions) if actions else "no immediate action needed"

df["Explanation"] = df.apply(explain, axis=1)
df["Recommended_Action"] = df.apply(recommend, axis=1)

print(df[["Zone_Name", "Risk_Category", "Explanation", "Recommended_Action"]])

df.to_csv("output/master_fragility_with_explanations.csv", index=False)
print("Saved to output/master_fragility_with_explanations.csv")