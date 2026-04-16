"""Parallel Task Delegation Tool — allows the current agent to spawn multiple agents in parallel."""

from __future__ import annotations

from typing import Any
import json
import concurrent.futures
from pathlib import Path
import tomllib

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec


def _run_agent_sync(agent_name: str, task: str) -> str:
    from openjarvis.core.config import load_config
    from openjarvis.agents.orchestrator import OrchestratorAgent
    from openjarvis.core.events import EventBus
    from openjarvis.agents._stubs import AgentContext
    from openjarvis.tools._stubs import ToolExecutor

    user_dir = Path("~/.openjarvis/templates").expanduser()
    template_data = None
    if user_dir.is_dir():
        for f in user_dir.glob("*.toml"):
            if agent_name.lower() in f.name.lower():
                try:
                    template_data = tomllib.loads(f.read_text(encoding="utf-8")).get("template", {})
                    break
                except Exception:
                    continue

    if not template_data:
        return f"Error: Agent '{agent_name}' not found."

    system_prompt = template_data.get("system_prompt_template", "You are an AI assistant.")
    system_prompt = system_prompt.format(instruction=task)

    config = load_config()
    cfg_engine = getattr(config.intelligence, "preferred_engine", "cloud")
    cfg_model = config.intelligence.default_model

    if cfg_engine == "ollama":
        from openjarvis.engine.ollama import OllamaEngine
        engine = OllamaEngine()
    else:
        from openjarvis.engine.cloud import CloudEngine
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
        max_turns=10
    )

    bus = EventBus()
    executor = ToolExecutor(sub_tools, bus=bus)
    agent._executor = executor

    ctx = AgentContext()
    result = agent.run(input=task, context=ctx)
    return result.content


@ToolRegistry.register("parallel_delegate_tasks")
class ParallelDelegateTasksTool(BaseTool):
    """Delegate multiple tasks to specialized agents in parallel."""

    tool_id = "parallel_delegate_tasks"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="parallel_delegate_tasks",
            description=(
                "Delegate multiple complex tasks or questions to specialist agents (e.g., Coder, UI Builder, Researcher) in parallel. "
                "Use this tool to heavily speed up multi-component development."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "A list of tasks to execute. Each task specifies the agent name and the instruction.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "agent_name": {
                                    "type": "string",
                                    "description": "Name of the agent to delegate to (e.g. 'coder', 'researcher', 'critic')."
                                },
                                "task": {
                                    "type": "string",
                                    "description": "The instruction to run."
                                }
                            },
                            "required": ["agent_name", "task"]
                        }
                    }
                },
                "required": ["tasks"],
            },
            category="intelligence",
            required_capabilities=[],
        )

    def execute(self, **params: Any) -> ToolResult:
        tasks = params.get("tasks", [])
        if not tasks:
            return ToolResult(
                tool_name="parallel_delegate_tasks",
                content="No tasks provided.",
                success=False,
            )

        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {
                executor.submit(_run_agent_sync, t.get("agent_name", "coder"), t.get("task", "")): t.get("agent_name", "coder")
                for t in tasks
            }
            for future in concurrent.futures.as_completed(futures):
                agent_name = futures[future]
                try:
                    results[agent_name] = future.result()
                except Exception as exc:
                    results[agent_name] = f"Error: {exc}"

        # Format results concisely
        formatted_results = []
        for agent_name, res in results.items():
            formatted_results.append(f"=== Agent: {agent_name.upper()} ===\\n{res}")

        return ToolResult(
            tool_name="parallel_delegate_tasks",
            content="\\n\\n".join(formatted_results),
            success=True,
        )
