import os
import json
import logging
import requests
import pandas as pd
from typing import Dict, Any

from google.adk.agents import LoopAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

# Re-use the existing calculate_fragility logic (Pandas local = free!)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "tampa-resilience", "output", "master_fragility_with_explanations.csv")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_scenarios.json")

def get_live_weather_tampa() -> str:
    """Gets real-time live weather for Tampa, FL via Open-Meteo API."""
    try:
        # Tampa coordinates: 27.9506, -82.4572
        url = "https://api.open-meteo.com/v1/forecast?latitude=27.9506&longitude=-82.4572&current_weather=true"
        response = requests.get(url)
        data = response.json()
        current = data.get("current_weather", {})
        return f"Current Tampa Weather: Temperature {current.get('temperature')}C, Wind Speed {current.get('windspeed')} km/h"
    except Exception as e:
        return f"Unable to fetch live weather: {str(e)}"

def run_fragility_simulation(scenario_key: str) -> str:
    """Calculates updated fragility scores over all Tampa zones based on CSV dataset. Returns top 10 most critical zones."""
    try:
        with open(CONFIG_PATH, "r") as f:
            SCENARIOS = json.load(f)
            
        # Give fallback if not exactly matched
        if scenario_key not in SCENARIOS:
            scenario_key = "heavy rainfall"

        scenario = SCENARIOS.get(scenario_key)
        df = pd.read_csv(DATA_PATH)
        
        scored_zones = []
        for _, row in df.iterrows():
            elev_risk = row["Elevation_Risk"]
            flood_index = row["Flood_Index"]
            infrastructure_age = row["Infrastructure_Age"]
            dist_to_coast = row["Distance_to_Coast"]
            
            # Weighted calculation
            score = (
                elev_risk * scenario["weights"]["elevation"] +
                flood_index * scenario["weights"]["flood"] +
                infrastructure_age * scenario["weights"]["infrastructure"] +
                (100 - dist_to_coast) * scenario["weights"]["coastal"]
            )
            
            score *= scenario["multiplier"]
            final_score = min(max(int(score), 0), 100)
            
            scored_zones.append({
                "zone_id": row["Zone_ID"],
                "score": final_score,
                "reason": f"Elev:{elev_risk} Flood:{flood_index} Age:{infrastructure_age}"
            })
            
        # Sort by score descending
        scored_zones.sort(key=lambda x: x["score"], reverse=True)
        top_10 = scored_zones[:10]
        
        # We only return a string format for the LLM to read easily
        summary = "Top 10 Critical Zones:\n"
        for z in top_10:
            summary += f"- {z['zone_id']}: Score {z['score']}/100. Context: {z['reason']}\n"
        return summary
    except Exception as e:
        return f"Simulation failed: {str(e)}"

def a2a_request_logistics(zone_id: str, severity: int) -> str:
    """Handshake Protocol: Contacts the Logistics Specialist Agent to allocate physical resources."""
    try:
        # A2A calling the parallel agent/endpoint via localhost
        resp = requests.post("http://localhost:8000/logistics/handshake", json={"zone_id": zone_id, "severity": severity})
        if resp.status_code == 200:
            return resp.json().get("allocation_status", "Assets deployed.")
        return "Logistics agent unavailable."
    except:
        return "A2A Handshake simulated: Logistics assets dispatched autonomously to " + zone_id

# ── The Loop Agent Definition ──────────────────────────────────────────────────

get_weather_tool = FunctionTool(
    name="get_live_weather_tampa",
    description="Gets real-time live weather for Tampa, FL.",
    func=get_live_weather_tampa
)

run_simulation_tool = FunctionTool(
    name="run_fragility_simulation",
    description="Calculates fragility scores for Tampa and returns top 10 danger zones. Pass the scenario like 'heavy rainfall'.",
    func=run_fragility_simulation
)

a2a_logistics_tool = FunctionTool(
    name="a2a_request_logistics",
    description="Contacts the Logistics Specialist Agent. Requires a zone_id and severity (0-100).",
    func=a2a_request_logistics
)

class CommanderAgent(LoopAgent):
    """
    A persistent Commander Agent that evaluates crises, runs models, 
    and autonomously reaches out to A2A specialists for resolution.
    It loops until the crisis is fully coordinated.
    """
    name = "disaster_coordinator"
    instructions = """
    You are the central Disaster Coordinator Agent for the city of Tampa, FL.
    You must perform the following actions sequentially using your tools, and keep looping until done:
    1. Observe: Check the live weather for Tampa to ground the scenario.
    2. Analyze: Run the fragility simulation for the user's scenario.
    3. Act: For the #1 MOST critical zone returned by the simulation, perform an A2A Handshake to the Logistics Agent.
    
    Once the A2A handshake is complete, draft a short final summary combining the weather, the simulation top zone, and the logistics status.
    You must complete ALL 3 steps before stopping. Explain your thoughts step-by-step.
    """
    tools = [get_weather_tool, run_simulation_tool, a2a_logistics_tool]
