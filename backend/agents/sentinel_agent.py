import requests
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

def fetch_tampa_weather() -> dict:
    """Fetches real-time weather data for Tampa Bay to ground the scenario in current reality."""
    try:
        # Tampa Bay coordinates
        res = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=27.9475&longitude=-82.4584&current_weather=true"
        )
        data = res.json()
        current = data.get("current_weather", {})
        return {
            "temperature_celsius": current.get("temperature", 25),
            "wind_speed_kmh": current.get("windspeed", 0),
            "condition_code": current.get("weathercode", 0)
        }
    except Exception as e:
        return {"error": str(e), "note": "falling back to baseline estimates."}

weather_tool = FunctionTool(func=fetch_tampa_weather)

sentinel_agent = LlmAgent(
    name="SentinelAgent",
    model="gemini-2.0-flash",
    description="The Sentinel. Pulls live feed weather from Open-Meteo to act as real-world grounding before scenario simulation.",
    instruction=(
        "You are the Sentinel. Your job is to fetch live weather data for Tampa Bay using the provided tool. "
        "Take the live data and write a short 2-sentence summary of current conditions. Store it in output_key 'live_conditions'."
    ),
    tools=[weather_tool],
    output_key="live_conditions"
)
