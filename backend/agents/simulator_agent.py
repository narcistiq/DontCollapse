import json
import logging
from backend.scoring import get_all_scored_zones

logger = logging.getLogger(__name__)

def run_simulator(scenario: str) -> dict:
    """
    Simulator Agent: Runs deterministic Pandas scoring.
    No LLM calls here because parallel bulk grading hits rate limits instantly.
    """
    try:
        zones = get_all_scored_zones(scenario)
        return {"rankedAreas": zones, "scenario": scenario, "count": len(zones)}
    except Exception as e:
        logger.error(f"Failed to run simulator scoring: {e}")
        return {"rankedAreas": [], "scenario": scenario, "error": str(e)}
