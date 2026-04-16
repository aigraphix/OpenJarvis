from openjarvis.agents.manager import AgentManager
from openjarvis.core.config import load_config
from pathlib import Path

config = load_config()
db_path = config.agent_manager.db_path or str(Path("~/.openjarvis/agents.db").expanduser())
manager = AgentManager(db_path=db_path)

# Look at existing agents to avoid duplicates
existing = manager.list_agents()
existing_names = {a["name"] for a in existing}

templates = manager.list_templates()
for tpl in templates:
    name = tpl.get("name")
    if name not in existing_names:
        print(f"Creating from template: {name}")
        manager.create_from_template(template_id=tpl["id"], name=name)

print("All templates instantiated!")
