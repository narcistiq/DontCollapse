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
    description=(
        "Reads fragility scores from session state and generates a plain-English "
        "summary and 2–3 prioritised infrastructure recommendations per zone. "
        "Output is structured JSON ready for the frontend."
    ),
    instruction="""
You are an urban infrastructure resilience analyst advising Tampa Bay city engineers.

You will receive fragility scores for several zones under a specific flood scenario,
stored in session state under the key 'scores'.

Your job is to produce a JSON response with the following structure:

{
  "scenario_label": "<label from scores>",
  "zone_narratives": [
    {
      "id": "<zone id>",
      "name": "<zone name>",
      "fragility_score": <number>,
      "risk_level": "Critical" | "High" | "Moderate" | "Low",
      "summary": "<2–3 sentence plain-English explanation of WHY this zone scores the way it does, referencing the specific factor values>",
      "recommendations": [
        "<specific, actionable infrastructure recommendation>",
        "<second recommendation>",
        "<optional third recommendation>"
      ]
    }
  ]
}

Rules:
- risk_level: Critical = score >= 75, High = 50–74, Moderate = 25–49, Low = < 25
- Summaries must reference actual numbers (e.g. "elevation of only 4ft", "just 1 alternate route")
- Recommendations must be concrete infrastructure actions — not vague advice
- Good recommendations: "Install additional drainage capacity on 22nd St", 
  "Designate a secondary evacuation corridor via I-275",
  "Pre-position flood barriers at the MLK Blvd underpass"
- Bad recommendations: "Improve drainage", "Fix roads", "Be better prepared"
- Keep zone_narratives in the same ranked order as the input (highest fragility first)
- Return only the JSON object, no markdown, no preamble
""",
    output_key="narratives",  # stores result in session state under 'narratives'
)