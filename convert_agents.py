import os
import glob
import json

out_dir = os.path.expanduser("~/.openjarvis/templates")
os.makedirs(out_dir, exist_ok=True)

for filepath in glob.glob("configs/agents/*.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    name = os.path.basename(filepath).replace(".md", "")
    desc = "Specialized Assistant"
    body = content
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) == 3:
            frontmatter = parts[1]
            body = parts[2].strip()
            
            for line in frontmatter.split("\n"):
                if line.startswith("name:"):
                    name = line.split("name:", 1)[1].strip()
                if line.startswith("specialty:"):
                    desc = line.split("specialty:", 1)[1].strip()

    # Escape curly braces for Python's .format() 
    body = body.replace("{", "{{").replace("}", "}}")
    
    toml_str = f"""[template]
id = "{name.lower().replace(' ', '_')}"
name = "{name}"
description = "{desc}"
agent_type = "orchestrator"
system_prompt_template = \"\"\"{body}

Task: {{instruction}}\"\"\"
tools = ["shell_exec", "file_read", "file_write", "web_search", "pdf_generate"]
"""
    
    out_path = os.path.join(out_dir, f"{name.lower().replace(' ', '_')}.toml")
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(toml_str)

print("Agents converted successfully.")
