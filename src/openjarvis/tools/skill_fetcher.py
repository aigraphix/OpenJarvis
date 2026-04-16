"""SkillFetcherTool — retrieve and parse new skills from officialskills.sh."""

from __future__ import annotations

import httpx
import re
from typing import Any

from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

@ToolRegistry.register("skill_fetcher")
class SkillFetcherTool(BaseTool):
    """Fetch skills from officialskills/awesome-agent-skills."""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="skill_fetcher",
            description=(
                "Fetch a skill's details from officialskills.sh or VoltAgent/awesome-agent-skills. "
                "Use this when you need a new capability that is not currently built into OpenJarvis. "
                "Provide a search query (e.g. 'figma' or 'remotion'), and this tool will "
                "search the global awesome-agent-skills repository, resolve the Github source, "
                "and return the documentation/source of the skill so you can write a new Python tool in src/openjarvis/tools/."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword (e.g., 'playwright', 'apollo-router', 'stripe')."
                    }
                },
                "required": ["query"]
            },
            category="skill"
        )

    def execute(self, **params: Any) -> ToolResult:
        query = params.get("query", "").lower()
        if not query:
            return ToolResult(tool_name="skill_fetcher", success=False, content="Query missing.")

        try:
            # 1. Fetch awesome-agent-skills README
            readme_url = "https://raw.githubusercontent.com/VoltAgent/awesome-agent-skills/main/README.md"
            readme_res = httpx.get(readme_url, timeout=10.0)
            readme_res.raise_for_status()
            content = readme_res.text
            
            # 2. Find matching skills
            matches = []
            for line in content.split("\n"):
                if query in line.lower() and ("http" in line or "officialskills.sh" in line):
                    matches.append(line.strip())
            
            if not matches:
                return ToolResult(
                    tool_name="skill_fetcher",
                    success=False,
                    content=f"No skills found matching '{query}' in the awesome-agent-skills repository."
                )

            # 3. If there is a match, try to fetch the actual markdown for the first one
            match_line = matches[0]
            link_match = re.search(r'\((https?://[^\)]+)\)', match_line)
            
            result_text = f"Found matches for '{query}':\n" + "\n".join(matches) + "\n\n"
            
            if link_match:
                skill_url = link_match.group(1)
                # If it's officialskills.sh, it normally redirects to a github tree. 
                # For simplicity, we just return the URL and ask the LLM to use browser_navigate if needed,
                # or we follow redirects to get the github raw text.
                
                # Resolving officialskills.sh manually -> github raw
                # Eg: https://officialskills.sh/openai/skills/yeet -> https://github.com/openai/skills/tree/main/skills/yeet
                if "officialskills.sh" in skill_url:
                    parts = skill_url.replace("https://officialskills.sh/", "").split("/")
                    if len(parts) >= 3 and parts[1] == "skills":
                        org = parts[0]
                        skill_name = parts[2]
                        # Assuming structure: github.com/{org}/{repo}/tree/main/skills/{skill_name}/README.md
                        # We don't always know {repo}, typically the repo is named 'skills' or 'agent-skills'.
                        # Let's just return instruction to use browser.
                        pass
                
                result_text += f"\nTo adapt the top match, please use the `browser_navigate` tool to visit: {skill_url}\n"
                result_text += "Read the skill's README and implementation, then create a new Python tool in `src/openjarvis/tools/`."

            return ToolResult(
                tool_name="skill_fetcher",
                success=True,
                content=result_text
            )
        except Exception as e:
            return ToolResult(
                tool_name="skill_fetcher",
                success=False,
                content=f"Error fetching skills: {e}"
            )

__all__ = ["SkillFetcherTool"]
