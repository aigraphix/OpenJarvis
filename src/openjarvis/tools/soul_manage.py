"""Manage persistent agent core identity (SOUL.md)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec


@ToolRegistry.register("soul_manage")
class SoulManageTool(BaseTool):
    """Manage persistent agent core identity (SOUL.md) and heartbeat."""

    def __init__(self, soul_path: Path | str = "~/.openjarvis/SOUL.md") -> None:
        self._soul_path = Path(soul_path).expanduser()

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="soul_manage",
            description=(
                "Read or update the agent's core identity, or pulse a heartbeat to SOUL.md."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["read", "pulse", "update"],
                        "description": "Action to perform on identity/soul.",
                    },
                    "content": {
                        "type": "string",
                        "description": (
                            "The identity content (for update action)."
                        ),
                    },
                },
                "required": ["action"],
            },
            category="memory",
        )

    def execute(self, **params: Any) -> ToolResult:
        action = params.get("action", "read")
        content = params.get("content", "")
        
        self._soul_path.parent.mkdir(parents=True, exist_ok=True)

        if action == "read":
            return self._read()
        elif action == "pulse":
            return self._pulse()
        elif action == "update":
            return self._update(content)
        
        return ToolResult(
            tool_name=self.spec.name,
            success=False,
            content=f"Unknown action: {action}",
        )

    def _read(self) -> ToolResult:
        content = ""
        if self._soul_path.exists():
            content = self._soul_path.read_text()
        else:
            content = "# Agent SOUL\nIdentity not yet established."
            self._soul_path.write_text(content)
            
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=content,
        )

    def _pulse(self) -> ToolResult:
        """Register a heartbeat timestamp."""
        now = datetime.now().isoformat()
        heartbeat_marker = f"Last Heartbeat: {now}"
        
        if self._soul_path.exists():
            text = self._soul_path.read_text()
            if "Last Heartbeat:" in text:
                import re
                text = re.sub(r"Last Heartbeat:.*", heartbeat_marker, text)
            else:
                text += f"\n\n{heartbeat_marker}"
            self._soul_path.write_text(text)
        else:
            self._soul_path.write_text(f"# Agent SOUL\n{heartbeat_marker}")
            
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content=f"Heartbeat updated to {now}",
        )

    def _update(self, content: str) -> ToolResult:
        if not content:
            return ToolResult(
                tool_name=self.spec.name,
                success=False,
                content="Content cannot be empty.",
            )
        self._soul_path.write_text(content)
        return ToolResult(
            tool_name=self.spec.name,
            success=True,
            content="Identity/SOUL updated successfully.",
        )
