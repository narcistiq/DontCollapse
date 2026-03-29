import json
import logging
import requests
from backend.groq_client import invoke_groq

logger = logging.getLogger(__name__)

def run_dispatcher(scenario: str, sentinel_data: dict, simulator_data: dict) -> dict:
    """
    Dispatcher Agent: Consolidates the outputs of Sentinel and Simulator.
    Simulates A2A interactions and uses Groq to write a final narrative report.
    """
    ranked_areas = simulator_data.get("rankedAreas", [])
    top_3 = ranked_areas[:3]
    
    top_3_str = "\n".join([f"- {z['zoneName']} (Score: {z['score']})" for z in top_3])
    
    # Optional A2A simulation
    # Imagine calling another deployed agent to request logistics...
    logistics_status = "A2A Handshake simulated: Not called."
    try:
        if top_3:
            resp = requests.post("http://localhost:8000/logistics/handshake", json={"zone_id": top_3[0]["zoneId"], "severity": top_3[0]["score"]}, timeout=5)
            if resp.status_code == 200:
                logistics_status = f"A2A Success: {resp.json().get('allocation_status')}"
    except Exception as err:
        logger.warning(f"A2A Handshake failed: {err}")
        pass

    prompt = f"""
    You are the final Dispatcher Agent for the city of Tampa's Resilience system.
    Summarize the disaster scenario and response into short, highly professional actionable paragraphs.

    Input Data:
    - Scenario: {scenario}
    - Live Sentinel Report: {sentinel_data.get('status')}
    - Top 3 At-Risk Zones Output by Simulator: 
    {top_3_str}
    - A2A Logistics Handshake Status: {logistics_status}
    
    Return a valid JSON object with:
    - "narrative": A clear 3-sentence summary of the current situation and what is being done.
    - "status": "critical" if severity implies it, else "warning".
    """

    fallback_json = json.dumps({
        "narrative": "Based on current data, the system successfully ranked all zones. Appropriate responses have been dispatched.",
        "status": "warning"
    })
    
    response_text = invoke_groq(prompt, response_format="json_object", fallback=fallback_json)
    
    try:
        final_summary = json.loads(response_text)
    except json.JSONDecodeError:
        final_summary = json.loads(fallback_json)
    
    # We must return the rankedAreas payload to visually color the map on frontend
    return {
        "status": final_summary.get("status", "success"),
        "adk_trace": prompt, # Kept for UI backwards compatibility 
        "narrative": final_summary.get("narrative", "Summary not available."),
        "logistics": logistics_status,
        "rankedAreas": ranked_areas
    }
