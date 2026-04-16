import os
import json
import socket
from datetime import datetime

def generate_manifest():
    """Gathers system and workspace data and writes a manifest file."""
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "cwd": os.getcwd(),
        "workspace_structure": [],
        "env_vars": {k: v for k, v in os.environ.items() if "NEXUS" in k or "GEMINI" in k}
    }

    # List top level files
    for item in os.listdir("."):
        if not item.startswith("."):
            manifest["workspace_structure"].append(item)

    manifest_path = "workspace_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"SUCCESS: Manifest generated at {manifest_path}")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    generate_manifest()
