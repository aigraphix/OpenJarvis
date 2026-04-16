#!/usr/bin/env python3
"""task_data_integration_sync.py

Autonomous Team Task: Cross-Repo Pattern Extraction

Collaborators:
- Architect: Antigravity (Design & Multi-modal logic)
- Worker: Nexus (File System & Asset logic)

Purpose:
- Index the document schema from external sources.
- Extract compatible assets for testing.
- Verify communication between Nexus's local brain and the target app.
"""

import sys
from pathlib import Path
from lib import AutomationAgentTask

HEALTH_REPO = Path("/Users/danny/Desktop/healthappgemma-build")

def main():
    task = AutomationAgentTask(
        name="Team Integration: External Data Sync",
        description="Extracting production patterns for advanced integration."
    )
    
    task.start()
    
    # 1. Verify Health Repo Existence
    def check_repo():
        if not HEALTH_REPO.exists():
            raise FileNotFoundError(f"Health repo not found at {HEALTH_REPO}")
        return {"path": str(HEALTH_REPO), "status": "Found"}
    
    task.step("Locate Target Repository", check_repo)

    # 2. Extract Migrations Context
    def extract_schema():
        migrations_dir = HEALTH_REPO / "supabase" / "migrations"
        migration_files = sorted(list(migrations_dir.glob("*.sql")))
        # Focus on document-related migrations
        doc_migrations = [f.name for f in migration_files if any(x in f.name for x in ["logs", "doc_", "attachments"])]
        return {"total_migrations": len(migration_files), "document_related": doc_migrations}

    task.step("Extract Database Schema Context", extract_schema)

    # 3. Catalog Production UI Components
    def catalog_ui():
        components_dir = HEALTH_REPO / "components"
        # Look for PDF or Document related components
        doc_components = [p.name for p in components_dir.rglob("*.tsx") if any(x in p.name.lower() for x in ["doc", "pdf", "log", "export"])]
        return {"doc_ui_count": len(doc_components), "samples": doc_components[:10]}

    task.step("Catalog Document UI Components", catalog_ui)

    task.finish(success=True, final_result={"status": "Synced", "collaborator": "Nexus-Local"})

if __name__ == "__main__":
    main()
