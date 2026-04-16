---
name: github
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries."
metadata: {
    "nexus": {
        "emoji": "🐙",
        "requires": { "bins": ["gh"] },
        "install": [
            {
                "id": "brew",
                "kind": "brew",
                "formula": "gh",
                "bins": ["gh"],
                "label": "Install GitHub CLI (brew)",
            },
            {
                "id": "apt",
                "kind": "apt",
                "package": "gh",
                "bins": ["gh"],
                "label": "Install GitHub CLI (apt)",
            },
        ],
    },
}
---

# GitHub Skill

Use the `gh` CLI to interact with GitHub. Always specify `--repo owner/repo`
when not in a git directory, or use URLs directly.

## Pull Requests

Check CI status on a PR:

```bash
gh pr checks 55 --repo owner/repo
```

List recent workflow runs:

```bash
gh run list --repo owner/repo --limit 10
```

View a run and see which steps failed:

```bash
gh run view <run-id> --repo owner/repo
```

View logs for failed steps only:

```bash
gh run view <run-id> --repo owner/repo --log-failed
```

## API for Advanced Queries

The `gh api` command is useful for accessing data not available through other
subcommands.

Get PR with specific fields:

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

## JSON Output

Most commands support `--json` for structured output. You can use `--jq` to
filter:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

## Security Gate — RLS Probe Failures

The CI security gate (`security-gate.yml`) runs an `rls_policy_probe` agent that
tests Supabase Row Level Security by attempting cross-tenant reads, writes, and
deletes. If `cross_tenant_read_health_logs` fails, follow this procedure.

### Diagnosis

1. Check whether the failing test involves a **doctor→patient** relationship:
   ```bash
   gh run view <run-id> --repo aigraphix/health-erecords-app --log-failed
   ```
   Look for:
   `FAIL: cross_tenant_read_health_logs_<id> — User A reading User B health log`

2. The test users are `doctor.smoke@example.com` (User A, role: doctor) and
   `patient.smoke@example.com` (User B, role: patient). An active
   `patient_authorization` between them is **expected and correct** for the app.

3. The seed code in `packages/security-agents/src/lib/supabase/seed.ts`
   temporarily revokes this authorization before probing. If the revocation is
   silently blocked, the doctor can still read the patient's logs and the test
   fails.

### Root Cause: RLS Silent Blocking

Supabase PostgREST does **not** raise an error when RLS blocks an UPDATE/DELETE
— it returns **0 affected rows**. The `patient_authorizations` UPDATE policy is:

```sql
patient_id = auth.uid()
```

This means **only the patient's client** can modify authorization rows. If the
seed uses the wrong client (the doctor's), the revocation is silently skipped.

### Fix Pattern

In `seed.ts`, each user must revoke authorizations where **they are the
patient**:

```typescript
// ✅ CORRECT — B is the patient, so B's client satisfies patient_id = auth.uid()
const { data: revokedByB } = await userBClient
    .from("patient_authorizations")
    .update({ revoked_at: revokeTs })
    .eq("doctor_id", userAId)
    .eq("patient_id", userBId)
    .is("revoked_at", null)
    .select("id");

// ✅ CORRECT — A is the patient, so A's client satisfies patient_id = auth.uid()
const { data: revokedByA } = await userAClient
    .from("patient_authorizations")
    .update({ revoked_at: revokeTs })
    .eq("doctor_id", userBId)
    .eq("patient_id", userAId)
    .is("revoked_at", null)
    .select("id");
```

### Key Rules

- **Always check row counts** after seed UPDATEs — 0 rows = RLS blocked it
- **Match the client to the RLS policy** — query `pg_policies` to confirm which
  `auth.uid()` the policy expects
- **Restore revoked data in cleanup** — use the same client pattern in
  `cleanupTestData()` to un-revoke authorizations after tests complete
- **This fix does NOT affect production** — only the CI test harness changes;
  all RLS policies and doctor→patient visibility remain intact
