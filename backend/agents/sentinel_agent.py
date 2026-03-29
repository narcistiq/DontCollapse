import requests
import json
import logging
from backend.groq_client import invoke_groq

logger = logging.getLogger(__name__)

def run_sentinel() -> dict:
    """
    Sentinel Agent: Checks live data (Weather) and contextualizes via Groq.
    Acts as the early warning observer.
    """
    weather_data_str = "Clear skies, no active alerts."
    try:
        # Tampa coordinates: 27.9506, -82.4572
        url = "https://api.open-meteo.com/v1/forecast?latitude=27.9506&longitude=-82.4572&current_weather=true"
        req = requests.get(url, timeout=5)
        if req.status_code == 200:
            data = req.json().get("current_weather", {})
            weather_data_str = f"Temperature: {data.get('temperature')}C, Wind Speed: {data.get('windspeed')} km/h"
    except Exception as e:
        logger.warning(f"Failed to fetch live weather: {e}")

    prompt = f"""
    You are the Sentinel Agent for the Tampa Resilience project.
    Your job is to observe live data and provide a brief status report.
    Live Weather Data: {weather_data_str}
    
    Output a JSON object with:
    - "status": A short summary string of the current conditions.
    - "alert_level": "low", "medium", or "high". 
    Must be valid JSON.
    """

    fallback_json = '{"status": "Current conditions are baseline. Using standard metrics.", "alert_level": "low"}'
    
    response_text = invoke_groq(prompt, response_format="json_object", fallback=fallback_json)
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return json.loads(fallback_json)
