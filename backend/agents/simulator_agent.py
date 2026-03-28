import json
import os
import pandas as pd
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.tools import FunctionTool

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "tampa-resilience", "output", "master_fragility_with_explanations.csv")

def extract_base_fragility() -> str:
    """Returns the base fragility scores from the local dataset."""
    df = pd.read_csv(DATA_PATH)
    return df.to_csv(index=False)

data_tool = FunctionTool(func=extract_base_fragility)

def create_scenario_analyzer(scenario_name: str) -> LlmAgent:
    return LlmAgent(
        name=f"Analyzer_{scenario_name.replace(' ', '_')}",
        model="gemini-2.5-flash",
        description=f"Scores the area under the context of {scenario_name}",
        instruction=(
            f"You are a simulation evaluator for the scenario: {scenario_name}. "
            "Use the extract_base_fragility tool to get base scores, then adjust them slightly based on the severity of your specific baseline scenario combined with any live_conditions present in session state. "
            f"Output ONLY a JSON array of the top 2 most at-risk zones under {scenario_name} (their Id, Name, and raw adjusted score)."
        ),
        tools=[data_tool],
        output_key=f"scores_{scenario_name.replace(' ', '_')}"
    )

# Parallel Agent running 3 variations simultaneously
simulator_agent = ParallelAgent(
    name="SimulatorParallel",
    description="The Simulator. Runs multiple predictive variants concurrently to handle high-velocity calculations.",
    sub_agents=[
        create_scenario_analyzer("heavy_rainfall"),
        create_scenario_analyzer("storm_surge"),
        create_scenario_analyzer("sea_level_rise"),
    ]
)
