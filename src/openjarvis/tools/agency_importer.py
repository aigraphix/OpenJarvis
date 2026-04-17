"""
agency_importer.py — Convert agency-agents markdown personas into OpenJarvis TOML templates.

Run once from the project root:
    python src/openjarvis/tools/agency_importer.py --source /tmp/agency-agents --out src/openjarvis/agents/templates/agency

Usage:
    python agency_importer.py [--source <path>] [--out <path>] [--priority-only]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── Category directories to include (skip game-dev, spatial-computing, academic) ──
INCLUDE_CATEGORIES = {
    "engineering",
    "design",
    "marketing",
    "paid-media",
    "product",
    "project-management",
    "sales",
    "specialized",
    "support",
    "finance",
    "testing",
}

# Division label mapping for display in the UI
DIVISION_LABELS = {
    "engineering": "Engineering",
    "design": "Design",
    "marketing": "Marketing",
    "paid-media": "Paid Media",
    "product": "Product",
    "project-management": "Project Management",
    "sales": "Sales",
    "specialized": "Specialized",
    "support": "Support",
    "finance": "Finance",
    "testing": "Testing",
}

# Priority agents to flag (for curated installs)
PRIORITY_AGENTS = {
    "ai-engineer", "backend-architect", "frontend-developer", "code-reviewer",
    "devops-automator", "software-architect", "agents-orchestrator",
    "document-generator", "mcp-builder", "product-manager", "sprint-prioritizer",
    "reality-checker", "api-tester", "ui-designer", "ux-architect",
    "growth-hacker", "seo-specialist", "senior-project-manager",
    "analytics-reporter", "workflow-architect",
}


def slugify(text: str) -> str:
    """Convert a name like 'AI Engineer' → 'ai-engineer'."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a markdown file."""
    frontmatter: dict = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_block = parts[1]
            body = parts[2].strip()
            for line in fm_block.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    frontmatter[key.strip()] = val.strip().strip('"').strip("'")

    return frontmatter, body


def escape_toml_multiline(text: str) -> str:
    """Escape text for TOML triple-quoted strings."""
    # Escape backslashes first, then any triple-quotes in the body
    text = text.replace("\\", "\\\\")
    text = text.replace('"""', '\\"""')
    return text


def convert_file(md_path: Path, category: str, out_dir: Path) -> str | None:
    """Convert one agency-agent markdown file to an OpenJarvis TOML template."""
    content = md_path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(content)

    name = fm.get("name", md_path.stem.replace("-", " ").title())
    description = fm.get("description", f"Specialized {name} agent.")
    emoji = fm.get("emoji", "🤖")
    slug = slugify(name)
    division = DIVISION_LABELS.get(category, category.title())
    is_priority = slug in PRIORITY_AGENTS

    # Build the system prompt from the body — use it directly
    system_prompt = body.strip()

    # Generate TOML
    toml_id = f"agency-{slug}"
    safe_sys = escape_toml_multiline(system_prompt)
    safe_desc = description.replace('"', '\\"')

    toml_content = f'''[template]
id = "{toml_id}"
name = "{name}"
description = "{safe_desc}"
icon = "{emoji}"
division = "{division}"
priority = {str(is_priority).lower()}
agent_type = "orchestrator"
max_turns = 15
temperature = 0.7
tools = ["web_search", "file_read", "file_write", "think", "shell_exec"]
system_prompt_template = """
{safe_sys}
"""
'''

    out_file = out_dir / f"{toml_id}.toml"
    out_file.write_text(toml_content, encoding="utf-8")
    return toml_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Import agency-agents into OpenJarvis")
    parser.add_argument("--source", default="/tmp/agency-agents", help="Path to cloned agency-agents repo")
    parser.add_argument("--out", default="src/openjarvis/agents/templates/agency", help="Output directory for TOML files")
    parser.add_argument("--priority-only", action="store_true", help="Only import priority 20 agents")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()

    if not source.exists():
        print(f"ERROR: Source not found: {source}", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    imported = 0
    skipped = 0

    for category_dir in sorted(source.iterdir()):
        if not category_dir.is_dir():
            continue
        cat = category_dir.name
        if cat.startswith(".") or cat in ("examples", "integrations", "scripts", ".github"):
            continue

        # Recurse into subdirectories (e.g. game-development/unity/)
        md_files = list(category_dir.rglob("*.md"))

        for md_path in sorted(md_files):
            if md_path.name in ("README.md", "CONTRIBUTING.md", "SECURITY.md"):
                continue

            # Determine the category for this file
            rel = md_path.relative_to(source)
            top_cat = rel.parts[0]

            if top_cat not in INCLUDE_CATEGORIES:
                skipped += 1
                continue

            fm, _ = parse_frontmatter(md_path.read_text(encoding="utf-8", errors="replace"))
            name = fm.get("name", md_path.stem.replace("-", " ").title())
            slug = slugify(name)

            if args.priority_only and slug not in PRIORITY_AGENTS:
                skipped += 1
                continue

            toml_id = convert_file(md_path, top_cat, out_dir)
            if toml_id:
                print(f"  ✓ {toml_id}")
                imported += 1

    print(f"\n✅ Done. Imported {imported} agents. Skipped {skipped}.")
    print(f"   Templates written to: {out_dir}")


if __name__ == "__main__":
    main()
