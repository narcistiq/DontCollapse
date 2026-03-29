import pandas as pd

# Load your base file
df_base = pd.read_csv("master_fragility_with_explanations.csv")

def risk_category(score):
    if score >= 80:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 30:
        return "MODERATE"
    else:
        return "LOW"

def explain_and_recommend(row, scenario):
    reasons = []
    actions = []

    if scenario == "heavy_rainfall":
        if row["Flood_Exposure"] > 70:
            reasons.append("high rainfall flooding risk")
            actions.append("improve drainage systems")
        if row["Road_Access_Risk"] > 60:
            reasons.append("road flooding risk")
            actions.append("reinforce evacuation routes")

    elif scenario == "storm_surge":
        if row["Elevation_Risk"] > 60:
            reasons.append("low elevation and surge vulnerability")
            actions.append("reinforce coastal protection")
        if row["Flood_Exposure"] > 60:
            reasons.append("coastal flood exposure")
            actions.append("protect critical access corridors")

    elif scenario == "sea_level_rise":
        if row["Elevation_Risk"] > 60:
            reasons.append("long-term sea level vulnerability")
            actions.append("elevate critical infrastructure")
        if row["Social_Vulnerability"] > 60:
            reasons.append("community exposure to long-term flooding")
            actions.append("prioritize resilience planning for vulnerable communities")

    elif scenario == "repeated_flooding":
        if row["Flood_Exposure"] > 60:
            reasons.append("recurrent flood exposure")
            actions.append("install flood mitigation systems")
        if row["Power_Infrastructure_Risk"] > 60:
            reasons.append("repeated infrastructure stress")
            actions.append("upgrade power grid resilience")
        if row["Road_Access_Risk"] > 60:
            reasons.append("repeated road disruption")
            actions.append("strengthen transportation access")

    explanation = ", ".join(reasons) if reasons else "moderate infrastructure risk under this scenario"
    recommendation = ", ".join(actions) if actions else "monitor conditions and maintain preparedness"

    return explanation, recommendation

def make_scenario(df, scenario, weights):
    df = df.copy()

    # Recalculate fragility score using scenario-specific weights
    df["Fragility_Score"] = (
        df["Flood_Exposure"] * weights["Flood_Exposure"] +
        df["Elevation_Risk"] * weights["Elevation_Risk"] +
        df["Road_Access_Risk"] * weights["Road_Access_Risk"] +
        df["Shelter_Access_Risk"] * weights["Shelter_Access_Risk"] +
        df["Social_Vulnerability"] * weights["Social_Vulnerability"] +
        df["Power_Infrastructure_Risk"] * weights["Power_Infrastructure_Risk"]
    )

    # Round score
    df["Fragility_Score"] = df["Fragility_Score"].round(1)

    # Risk category
    df["Risk_Category"] = df["Fragility_Score"].apply(risk_category)

    # Rank (1 = highest risk)
    df = df.sort_values(by="Fragility_Score", ascending=False).reset_index(drop=True)
    df["Fragility_Rank"] = df.index + 1

    # Scenario-specific explanation + action
    results = df.apply(lambda row: explain_and_recommend(row, scenario), axis=1)
    df["Explanation"] = [r[0] for r in results]
    df["Recommended_Action"] = [r[1] for r in results]

    return df

# Scenario weight settings
scenario_weights = {
    "heavy_rainfall": {
        "Flood_Exposure": 0.35,
        "Elevation_Risk": 0.15,
        "Road_Access_Risk": 0.25,
        "Shelter_Access_Risk": 0.10,
        "Social_Vulnerability": 0.10,
        "Power_Infrastructure_Risk": 0.05
    },
    "storm_surge": {
        "Flood_Exposure": 0.30,
        "Elevation_Risk": 0.30,
        "Road_Access_Risk": 0.15,
        "Shelter_Access_Risk": 0.10,
        "Social_Vulnerability": 0.10,
        "Power_Infrastructure_Risk": 0.05
    },
    "sea_level_rise": {
        "Flood_Exposure": 0.20,
        "Elevation_Risk": 0.35,
        "Road_Access_Risk": 0.10,
        "Shelter_Access_Risk": 0.10,
        "Social_Vulnerability": 0.20,
        "Power_Infrastructure_Risk": 0.05
    },
    "repeated_flooding": {
        "Flood_Exposure": 0.25,
        "Elevation_Risk": 0.10,
        "Road_Access_Risk": 0.25,
        "Shelter_Access_Risk": 0.10,
        "Social_Vulnerability": 0.10,
        "Power_Infrastructure_Risk": 0.20
    }
}

# Make and save each scenario file
for scenario_name, weights in scenario_weights.items():
    df_scenario = make_scenario(df_base, scenario_name, weights)
    output_file = f"scenario_{scenario_name}.csv"
    df_scenario.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")