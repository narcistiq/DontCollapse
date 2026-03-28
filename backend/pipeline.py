"""
pipeline.py — Orchestrates the two-agent workflow using ADK's SequentialAgent.
 
Flow:
  1. ScorerAgent   → scores all zones, writes to session state['scores']
  2. NarrativeAgent → reads scores, writes AI narratives to session state['narratives']
 
The final output in session state['narratives'] is what the FastAPI
endpoint returns to the frontend.
"""
 
from google.adk.agents import SequentialAgent
from backend.agents.scorer_agent import scorer_agent
from backend.agents.narrative_agent import narrative_agent
 
 
resilience_pipeline = SequentialAgent(
    name="ResiliencePipeline",
    description=(
        "End-to-end Tampa Bay infrastructure resilience pipeline. "
        "Scores zones for fragility under a flood scenario, then generates "
        "plain-English explanations and infrastructure recommendations."
    ),
    sub_agents=[scorer_agent, narrative_agent],
)
 