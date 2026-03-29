from backend.agents.sentinel_agent import run_sentinel
from backend.agents.simulator_agent import run_simulator
from backend.agents.dispatcher_agent import run_dispatcher

def run_resilience_pipeline(scenario: str) -> dict:
    """Manually orchestrates Sentinel -> Simulator -> Dispatcher using Groq API."""
    
    print("[Pipeline] Running Sentinel (Live Data + Groq)...")
    sentinel_result = run_sentinel()
    
    print("[Pipeline] Running Simulator (Pandas Deterministic Models)...")
    simulator_result = run_simulator(scenario)
    
    print("[Pipeline] Running Dispatcher (A2A Handshakes + Groq Narratives)...")
    dispatcher_result = run_dispatcher(scenario, sentinel_result, simulator_result)
    
    print("[Pipeline] Complete. Returning payload to frontend.")
    return dispatcher_result
