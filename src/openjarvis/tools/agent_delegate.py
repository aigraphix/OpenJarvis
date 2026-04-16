"""Agent Delegation Tool — allows the current agent to spawn and delegate tasks to specialized agents."""

from __future__ import annotations

from typing import Any
import json
from pathlib import Path

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

@ToolRegistry.register("delegate_task")
class DelegateTaskTool(BaseTool):
    """Delegate a task to a specialized agent."""

    tool_id = "delegate_task"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="delegate_task",
            description=(
                "Delegate a complex task or ask a question to one of the specialist real agents in the system (e.g., Coder, UI Builder, Researcher, Critic)."
                " Always use this tool when you need specialized expertise or need multiple files generated/processed."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "The name of the agent to delegate to (e.g. 'coder', 'creative', 'architect', 'devops', 'writer'). Leave empty to use 'coder'.",
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
            # Import everything needed to spawn the engine and run an agent synchronously 
            from openjarvis.engine._stubs import InferenceEngine
            from openjarvis.agents.orchestrator import OrchestratorAgent
            from openjarvis.agents.manager import AgentManager
            from openjarvis.core.config import load_config
            from openjarvis.core.registry import ToolRegistry
            import tomllib

            # Find the template to get the system prompt
            user_dir = Path("~/.openjarvis/templates").expanduser()
            template_data = None
            if user_dir.is_dir():
                for f in user_dir.glob("*.toml"):
                    if agent_name.lower() in f.name.lower():
                        template_data = tomllib.loads(f.read_text(encoding="utf-8")).get("template", {})
                        break
                        
            if not template_data:
                # If specifically requested but not found
                return ToolResult(
                    tool_name="delegate_task",
                    content=f"Error: Specialized agent '{agent_name}' not found. Try 'coder', 'creative', or 'research'.",
                    success=False,
                )

            system_prompt = template_data.get("system_prompt_template", "")
            system_prompt = system_prompt.format(instruction=task)

            # Re-initialize the same engine we use
            config = load_config()
            cfg_engine = config.intelligence.preferred_engine
            cfg_model = config.intelligence.default_model

            if cfg_engine == "ollama":
                from openjarvis.engine.ollama import OllamaEngine
                engine = OllamaEngine()
            else:
                from openjarvis.engine.cloud import CloudEngine
                engine = CloudEngine()

            # Instantiate tools for the sub-agent
            tools_list = template_data.get("tools", ["shell_exec", "file_read", "file_write", "pdf_generate"])
            sub_tools = []
            
            # Helper to bind tools safely
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

            # Bind Executor manually as it usually happens via standard loop
            from openjarvis.core.events import EventBus
            from openjarvis.agents._stubs import AgentContext
            from openjarvis.tools._stubs import ToolExecutor
            bus = EventBus()
            executor = ToolExecutor(sub_tools, bus=bus)
            agent._executor = executor

            # Execute run synchronously
            ctx = AgentContext()
            result = agent.run(input=task, context=ctx)
            
            return ToolResult(
                tool_name="delegate_task",
                content=f"Agent '{agent_name}' completed the task:\n{result.content}",
                success=True,
                metadata={"sub_turns": result.turns}
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
