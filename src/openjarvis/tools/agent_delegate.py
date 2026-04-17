"""Agent Delegation Tool — allows the current agent to spawn and delegate tasks to specialized agents."""

from __future__ import annotations

from typing import Any
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
    bundled = Path(__file__).parent.parent / "agents" / "templates"
    if bundled.is_dir():
        paths.append(bundled)
    agency = bundled / "agency"
    if agency.is_dir():
        paths.append(agency)
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
                        # Fallback: regex extraction for Python <3.11
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


@ToolRegistry.register("delegate_task")
class DelegateTaskTool(BaseTool):
    """Delegate a task to a specialized agent."""

    tool_id = "delegate_task"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="delegate_task",
            description=(
                "Delegate a complex task to a specialist agent. "
                "Available specialists: coder, researcher, critic, writer, devops, architect, analyst, planner. "
                "Also supports any agency persona by name (e.g. 'agency-seo-specialist'). "
                "Always use this when you need specialized expertise or need files generated/processed."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Specialist to delegate to: coder, researcher, critic, writer, devops, architect, analyst, planner.",
                    },
                    "task": {
                        "type": "string",
                        "description": "The specific instruction or task for the specialist agent.",
                    },
                },
                "required": ["task"],
            },
            category="intelligence",
            required_capabilities=[],
        )

    def execute(self, **params: Any) -> ToolResult:
        task = params.get("task", "")
        agent_name = params.get("agent_name", "coder")

        if not task:
            return ToolResult(
                tool_name="delegate_task",
                content="No task provided.",
                success=False,
            )

        try:
            from openjarvis.engine._stubs import InferenceEngine
            from openjarvis.agents.orchestrator import OrchestratorAgent
            from openjarvis.core.config import load_config
            from openjarvis.core.registry import ToolRegistry

            template_data = _find_template(agent_name)
            if not template_data:
                return ToolResult(
                    tool_name="delegate_task",
                    content=(
                        f"Agent '{agent_name}' not found. "
                        "Available specialists: coder, researcher, critic, writer, devops, architect, analyst, planner."
                    ),
                    success=False,
                )

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

            from openjarvis.core.events import EventBus
            from openjarvis.agents._stubs import AgentContext
            from openjarvis.tools._stubs import ToolExecutor

            bus = EventBus()
            executor = ToolExecutor(sub_tools, bus=bus)
            agent._executor = executor

            ctx = AgentContext()
            result = agent.run(input=task, context=ctx)

            return ToolResult(
                tool_name="delegate_task",
                content=f"[{agent_name.upper()}] {result.content}",
                success=True,
                metadata={"sub_turns": result.turns},
            )

        except Exception as exc:
            import traceback
            err = traceback.format_exc()
            return ToolResult(
                tool_name="delegate_task",
                content=f"Delegation failed: {str(exc)}\n{err}",
                success=False,
            )


__all__ = ["DelegateTaskTool"]
