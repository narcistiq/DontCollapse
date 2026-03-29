import os
import pandas as pd
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.tools import FunctionTool

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "tampa-resilience", "output", "master_fragility_with_explanations.csv")

# Constants for scenario weights
SCENARIOS = {
    "heavy_rainfall": {
        "label": "Heavy Rainfall",
        "Elevation_Risk": 0.25,
        "Flood_Exposure": 0.35, # maps to drainage/history
        "Road_Access_Risk": 0.20,
        "Shelter_Access_Risk": 0.10,
        "Social_Vulnerability": 0.10
    },
    "storm_surge": {
        "label": "Storm Surge",
        "Elevation_Risk": 0.40,
        "Flood_Exposure": 0.15,
        "Road_Access_Risk": 0.25,
        "Shelter_Access_Risk": 0.15,
        "Social_Vulnerability": 0.05
    },
    "sea_level_rise": {
        "label": "Sea Level Rise",
        "Elevation_Risk": 0.35,
        "Flood_Exposure": 0.20,
        "Road_Access_Risk": 0.20,
        "Shelter_Access_Risk": 0.15,
        "Social_Vulnerability": 0.10
    },
    "repeated_flooding_days": {
        "label": "Repeated Flooding Days",
        "Elevation_Risk": 0.20,
        "Flood_Exposure": 0.30,
        "Road_Access_Risk": 0.20,
        "Shelter_Access_Risk": 0.10,
        "Social_Vulnerability": 0.20
    }
}

def calculate_fragility_for_scenario(scenario_key: str) -> dict:
    """Calculates updated fragility scores using the CSV dataset and scenario-specific weights."""
    if scenario_key not in SCENARIOS:
        return {"error": f"Scenario {scenario_key} not found."}
        
    scenario = SCENARIOS[scenario_key]
    df = pd.read_csv(DATA_PATH)
    
    scored_zones = []
    for _, row in df.iterrows():
        # Baseline variables from the CSV (scale 0-100)
        elev_risk = row["Elevation_Risk"]
        flood_risk = row["Flood_Exposure"]
        road_risk = row["Road_Access_Risk"]
        shelter_risk = row["Shelter_Access_Risk"]
        social_risk = row["Social_Vulnerability"]
        
        # Calculate new score based on scenario weights
        raw_score = (
            (elev_risk * scenario["Elevation_Risk"]) +
            (flood_risk * scenario["Flood_Exposure"]) +
            (road_risk * scenario["Road_Access_Risk"]) +
            (shelter_risk * scenario["Shelter_Access_Risk"]) +
            (social_risk * scenario["Social_Vulnerability"])
        )
        
        scored_zones.append({
            "id": row["Zone_ID"],
            "name": row["Zone_Name"],
            "fragility_score": round(raw_score, 1),
            "original_category": row["Risk_Category"],
            "base_explanation": row["Explanation"]
        })
        
    scored_zones.sort(key=lambda x: x["fragility_score"], reverse=True)
    
    return {
        "scenario": scenario_key,
        "top_zones": scored_zones[:3]
    }

tool_heavy_rain = FunctionTool(func=lambda: calculate_fragility_for_scenario("heavy_rainfall"))
tool_storm_surge = FunctionTool(func=lambda: calculate_fragility_for_scenario("storm_surge"))
tool_sea_level = FunctionTool(func=lambda: calculate_fragility_for_scenario("sea_level_rise"))

def create_scenario_analyzer(scenario_name: str, tool: FunctionTool) -> LlmAgent:
    return LlmAgent(
        name=f"Analyzer_{scenario_name.replace(' ', '_')}",
        model="gemini-2.0-flash",
        description=f"Evaluates zone fragility for {scenario_name}",
        instruction=(
            f"You are evaluating the impact of {scenario_name}. "
            "Call the provided tool to get the deterministic CSV-driven fragility scores for this specific scenario. "
            "Return the JSON object exact result from the tool."
        ),
        tools=[tool],
        output_key=f"scores_{scenario_name.replace(' ', '_')}"
    )

# Parallel Agent running 3 variations simultaneously
simulator_agent = ParallelAgent(
    name="SimulatorParallel",
    description="The Simulator. Runs multiple predictive variants concurrently to handle high-velocity calculations based on the CSV data.",
    sub_agents=[
        create_scenario_analyzer("heavy_rainfall", tool_heavy_rain),
        create_scenario_analyzer("storm_surge", tool_storm_surge),
        create_scenario_analyzer("sea_level_rise", tool_sea_level),
    ]
)
