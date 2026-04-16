import asyncio
import concurrent.futures
from pathlib import Path
import tomllib
from openjarvis.core.config import load_config
from openjarvis.core.registry import ToolRegistry
from openjarvis.agents.orchestrator import OrchestratorAgent
from openjarvis.core.events import EventBus
from openjarvis.agents._stubs import AgentContext
from openjarvis.tools._stubs import ToolExecutor
from openjarvis.engine.cloud import CloudEngine
from openjarvis.engine.ollama import OllamaEngine
from dotenv import load_dotenv  # type: ignore

load_dotenv()

def run_agent_sync(agent_name, task):
    user_dir = Path("~/.openjarvis/templates").expanduser()
    template_data = None
    if user_dir.is_dir():
        for f in user_dir.glob("*.toml"):
            if agent_name.lower() in f.name.lower():
                template_data = tomllib.loads(f.read_text(encoding="utf-8")).get("template", {})
                break
                
    if not template_data:
        return f"Error: Agent '{agent_name}' not found."

    system_prompt = template_data.get("system_prompt_template", "You are an AI assistant.")
    system_prompt = system_prompt.format(instruction=task)

    config = load_config()
    cfg_engine = getattr(config.intelligence, "preferred_engine", "cloud")
    cfg_model = config.intelligence.default_model

    if cfg_engine == "ollama":
        engine = OllamaEngine()
    else:
        engine = CloudEngine()

    tools_list = template_data.get("tools", ["shell_exec", "file_read", "file_write"])
    sub_tools = []
    
    for t_name in tools_list:
        try:
            cls = ToolRegistry.get(t_name)
            if cls:
                tool_inst = cls()
                if hasattr(tool_inst, "bind_engine"):
                    tool_inst.bind_engine(engine, cfg_model)
                sub_tools.append(tool_inst)
        except Exception:
            pass

    agent = OrchestratorAgent(
        engine=engine,
        model=cfg_model,
        tools=sub_tools,
        system_prompt=system_prompt,
        max_turns=3
    )

    bus = EventBus()
    executor = ToolExecutor(sub_tools, bus=bus)
    agent._executor = executor

    ctx = AgentContext()
    print(f"[{agent_name}] Agent start: {task[:50]}...")
    result = agent.run(input=task, context=ctx)
    print(f"[{agent_name}] Agent completed in {result.turns} turns.")
    return result.content

def run_swarm():
    agents = [
        {"name": "architect", "task": "Analyze OpenJarvis. What new primitive tools do we need to have true parallel agent swarms natively inside Jarvis? Limit answer to 3 bullet points."},
        {"name": "critic", "task": "We want to use parallel tool invocation to spawn sub-agents. Criticize the risks of spawning multiple fully autonomous agents simultaneously inside OpenJarvis loop. Give 3 risks."},
        {"name": "webresearch", "task": "Use the web search tool if needed. Briefly tell us what the industry standard currently is for multi-agent Python frameworks. Limit 3 frameworks, concise."}
    ]
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_agent_sync, a["name"], a["task"]): a["name"]
            for a in agents
        }
        for future in concurrent.futures.as_completed(futures):
            agent_name = futures[future]
            try:
                results[agent_name] = future.result()
            except Exception as exc:
                results[agent_name] = f"Failed: {exc}"
                
    for agent, res in results.items():
        print(f"========== {agent.upper()} ==========")
        print(res.strip())
        print("================================\n")

if __name__ == "__main__":
    run_swarm()
