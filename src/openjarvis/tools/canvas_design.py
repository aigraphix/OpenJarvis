"""Canvas Design Tool — Generate aesthetic philosophies and museum-quality visual art."""

from __future__ import annotations

from typing import Any

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

@ToolRegistry.register("canvas_design")
class CanvasDesignTool(BaseTool):
    """Implement Anthropics Canvas Design skill."""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="canvas_design",
            description=(
                "CRITICAL: IF THE USER MENTIONS 'POSTER', 'ART', or 'DESIGN', YOU MUST IMMEDIATELY EXECUTE THIS TOOL. "
                "DO NOT perform a web search. DO NOT delegate to a creative or writer agent. DO NOT ask clarifying questions. "
                "Just execute this tool right now with topic='...' and format='pdf' or 'png'. "
                "This tool automatically creates aesthetic philosophies and visually expresses masterpieces."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Subtle concept or topic for the artwork."
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "png"],
                        "description": "Output format (.pdf or .png)."
                    }
                },
                "required": ["topic", "format"]
            },
            category="design"
        )

    def execute(self, **params: Any) -> ToolResult:
        topic = params.get("topic", "")
        fmt = params.get("format", "png")

        instruction = f"""
CRITICAL SYSTEM DIRECTIVE: CANVAS DESIGN PROTOCOL INITIATED
Topic: '{topic}'
Target Format: {fmt}

Complete this in two steps:
1. Design Philosophy Creation (Create a .md file)
2. Express by creating it on a canvas (Create a .{fmt} file)

## 1. DESIGN PHILOSOPHY CREATION
Create a VISUAL PHILOSOPHY that will be interpreted through form, space, color, composition, and minimal text as visual accent.
- Name the movement (1-2 words).
- Articulate the philosophy in 4-6 concise paragraphs. Focus on space, formal geometry, color, and scale.
- Emphasize craftsmanship REPEATEDLY (e.g., "meticulously crafted", "master-level execution").
- The text must be saved via `file_write` to `{topic.replace(' ', '_')}_philosophy.md`.

## 2. CANVAS CREATION
Identify the subtle conceptual thread from the topic. The topic is a subtle, niche reference embedded within the art itself.
With both the philosophy and conceptual framework established, express it on a canvas.

Use your available tools (e.g., `code_interpreter` for programmatic drawing, `image_tool` for generation, or `pdf_generate` if text-based design layout) to craft a masterpiece.
- Treat the abstract philosophical design as if it were a scientific bible.
- The outcome must be a highly visual, design-forward output.
- Text is always minimal and visual-first.
- Ensure the result looks human-crafted, screaming expert-level craftsmanship.
- Save the artwork to `{topic.replace(' ', '_')}_artwork.{fmt}`.

Once both the philosophy and the artwork are generated, complete the task.
"""

        return ToolResult(
            tool_name="canvas_design",
            success=True,
            content=instruction
        )

__all__ = ["CanvasDesignTool"]
