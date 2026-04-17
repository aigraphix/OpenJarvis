"""Parallel Task Delegation Tool — allows the current agent to spawn multiple agents in parallel."""

from __future__ import annotations

from typing import Any
import concurrent.futures
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec



def _template_search_paths() -> list[Path]:
    """Return ordered list of directories to search for agent templates."""
    paths = []
    # 1. Bundled templates (always present)
    bundled = Path(__file__).parent.parent / "agents" / "templates"
    if bundled.is_dir():
        paths.append(bundled)
    # 2. Agency sub-folder
    agency = bundled / "agency"
    if agency.is_dir():
        paths.append(agency)
    # 3. User-installed templates (~/.openjarvis/templates)
    user = Path("~/.openjarvis/templates").expanduser()
    if user.is_dir():
        paths.append(user)
    return paths


def _find_template(agent_name: str) -> dict | None:
    """Find a template by agent name across all search paths."""
    name_lower = agent_name.lower().replace("-", "_").replace(" ", "_")
    for search_dir in _template_search_paths():
        for f in search_dir.glob("*.toml"):
            stem = f.stem.lower().replace("-", "_")
            if stem == name_lower or name_lower in stem:
                try:
                    if tomllib is not None:
                        data = tomllib.loads(f.read_text(encoding="utf-8"))
                        return data.get("template", {})
                    else:
                        import re
                        content = f.read_text(encoding="utf-8")
                        def _get(key: str) -> str:
                            m = re.search(rf'^{key}\s*=\s*"([^"]*)"', content, re.MULTILINE)
                            return m.group(1) if m else ""
                        sp_m = re.search(r'system_prompt_template\s*=\s*"""(.+?)"""', content, re.DOTALL)
                        tools_m = re.findall(r'"([^"]+)"', next(iter(re.findall(r'tools\s*=\s*\[([^\]]+)\]', content)), ""))
                        return {
                            "id": _get("id") or f.stem,
                            "name": _get("name"),
                            "description": _get("description"),
                            "icon": _get("icon"),
                            "tools": tools_m,
                            "max_turns": int(_get("max_turns") or 10),
                            "system_prompt_template": sp_m.group(1).strip() if sp_m else "You are an AI assistant.\n\n{instruction}",
                        }

                except Exception:
                    continue
    return None


def _run_agent_sync(agent_name: str, task: str) -> str:
    from openjarvis.core.config import load_config
    from openjarvis.agents.orchestrator import OrchestratorAgent
    from openjarvis.core.events import EventBus
    from openjarvis.agents._stubs import AgentContext
    from openjarvis.tools._stubs import ToolExecutor

    template_data = _find_template(agent_name)
    if not template_data:
        return f"Error: Agent '{agent_name}' not found. Available: coder, researcher, critic, writer, devops, architect, analyst, planner."

    system_prompt = template_data.get("system_prompt_template", "You are an AI assistant.")
    try:
        system_prompt = system_prompt.format(instruction=task)
    except KeyError:
        pass

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
        max_turns=template_data.get("max_turns", 10),
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
                "Delegate multiple complex tasks to specialist agents (e.g., coder, researcher, critic, architect, writer, devops, analyst, planner) in parallel. "
                "Use this to heavily accelerate multi-component work — agents run simultaneously and return independent results."
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
                                    "description": "Name of the specialist agent: coder, researcher, critic, writer, devops, architect, analyst, planner.",
                                },
                                "task": {
                                    "type": "string",
                                    "description": "The specific instruction for this agent.",
                                },
                            },
                            "required": ["agent_name", "task"],
                        },
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

        results: dict[str, str] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tasks), 8)) as executor:
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

        # Format results in the original task order
        task_order = [t.get("agent_name", "coder") for t in tasks]
        formatted: list[str] = []
        for name in task_order:
            if name in results:
                formatted.append(f"=== [{name.upper()}] ===\n{results.pop(name)}")
        # Any remaining (duplicate agent names)
        for name, res in results.items():
            formatted.append(f"=== [{name.upper()}] ===\n{res}")

        return ToolResult(
            tool_name="parallel_delegate_tasks",
            content="\n\n".join(formatted),
            success=True,
        )
