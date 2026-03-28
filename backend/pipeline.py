from google.adk.agents import SequentialAgent
from backend.agents.sentinel_agent import sentinel_agent
from backend.agents.simulator_agent import simulator_agent
from backend.agents.dispatcher_agent import dispatcher_agent

# Assemble the final pipeline showing Sequential chaining of: LlmAgent -> ParallelAgent -> LoopAgent
resilience_pipeline = SequentialAgent(
    name="ResiliencePipeline",
    description="The top-level orchestrator routing through Sentinel, Simulator, and Dispatcher.",
    sub_agents=[
        sentinel_agent,
        simulator_agent,
        dispatcher_agent
    ]
)
