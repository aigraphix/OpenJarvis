---
name: nexushub
description: Use the nexusHub CLI to search, install, update, and publish agent skills from nexushub.com. Use when you need to fetch new skills on the fly, sync installed skills to latest or a specific version, or publish new/updated skill folders with the npm-installed nexushub CLI.
metadata: {"nexus":{"requires":{"bins":["nexushub"]},"install":[{"id":"node","kind":"node","package":"nexushub","bins":["nexushub"],"label":"Install nexusHub CLI (npm)"}]}}
---

# nexusHub CLI

Install
```bash
npm i -g nexushub
```

Auth (publish)
```bash
nexushub login
nexushub whoami
```

Search
```bash
nexushub search "postgres backups"
```

Install
```bash
nexushub install my-skill
nexushub install my-skill --version 1.2.3
```

Update (hash-based match + upgrade)
```bash
nexushub update my-skill
nexushub update my-skill --version 1.2.3
nexushub update --all
nexushub update my-skill --force
nexushub update --all --no-input --force
```

List
```bash
nexushub list
```

Publish
```bash
nexushub publish ./my-skill --slug my-skill --name "My Skill" --version 1.2.0 --changelog "Fixes + docs"
```

Notes
- Default registry: https://nexushub.com (override with nexusHUB_REGISTRY or --registry)
- Default workdir: cwd (falls back to Nexus workspace); install dir: ./skills (override with --workdir / --dir / nexusHUB_WORKDIR)
- Update command hashes local files, resolves matching version, and upgrades to latest unless --version is set
