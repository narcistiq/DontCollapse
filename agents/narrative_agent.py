"""
NarrativeAgent — reads the scored zones from session state and uses
Gemini to produce plain-English explanations and infrastructure
recommendations for each zone.
"""

from google.adk.agents import LlmAgent


# ── Agent definition ──────────────────────────────────────────────────────────

narrative_agent = LlmAgent(
    name="NarrativeAgent",
    model="gemini-2.0-flash",
    description="Generates fragility summaries and recommendations from scored zones.",
    instruction="""
You are a resilience analyst advising Tampa Bay engineers.

Read the scores from session state key 'scores'. Process only the top 3 zones (highest fragility_score).

Return ONLY this JSON, no markdown, no preamble:
{
  "scenario_label": "<from scores>",
  "zone_narratives": [
    {
      "id": "<zone id>",
      "name": "<zone name>",
      "fragility_score": <number>,
      "risk_level": "Critical|High|Moderate|Low",
      "summary": "<2 sentences referencing actual numbers like elevation, routes, drainage>",
      "recommendations": ["<specific action>", "<specific action>"]
    }
  ]
}

risk_level: Critical>=75, High=50-74, Moderate=25-49, Low<25
""",
    output_key="narratives",
)