---
name: strategic-compact
description: Suggests context compaction at logical workflow boundaries instead of arbitrary auto-compaction. Prevents mid-task context loss.
---

# Strategic Compaction Skill

Suggests context compaction at logical workflow boundaries rather than
relying on arbitrary auto-compaction that can trigger mid-task.

## Why Strategic Compaction?

Auto-compaction triggers at arbitrary points:
- Often mid-task, losing important context
- No awareness of logical task boundaries
- Can interrupt complex multi-step operations

Strategic compaction at logical boundaries:
- **After exploration, before execution** — Compact research context, keep plan
- **After completing a milestone** — Fresh start for next phase
- **Before major context shifts** — Clear old context before different task

## When to Compact

### ✅ Good Compaction Points

| Boundary | Why |
|----------|-----|
| After planning phase | Plan is finalized, research context can go |
| After debugging session | Error-resolution context no longer needed |
| After completing a feature | Implementation details can be summarized |
| Before starting new task type | Clear old context for fresh approach |
| After large file exploration | File contents cached, structure understood |

### ❌ Bad Compaction Points

| Boundary | Why |
|----------|-----|
| Mid-implementation | Lose implementation context and decisions |
| During multi-file refactor | Lose cross-file relationship awareness |
| While investigating a bug | Lose error traces and hypothesis chain |
| During code review | Lose review context across files |

## Protocol

### For Long Sessions (50+ tool calls)

1. **Check milestone**: Have you completed a logical unit of work?
2. **Save state**: Write critical context to `team_brain.md` or working memory
3. **Summarize**: Create a brief summary of what was done and what's next
4. **Compact**: Trigger compaction with the summary as preservation context

### For Agent Sessions

Agents should self-assess after each major phase:
- If context is 60%+ consumed → suggest compaction at next boundary
- If switching task types → compact before starting new type
- If research phase complete → compact before implementation phase

## Best Practices

1. **Compact after planning** — Once plan is finalized, compact to start fresh
2. **Compact after debugging** — Clear error-resolution context before continuing
3. **Don't compact mid-implementation** — Preserve context for related changes
4. **Save before compacting** — Triple-write any critical learnings first
5. **Include next-steps in summary** — So post-compaction context knows what to do

## Integration with Nexus

This skill works alongside:
- **Triple-Write Protocol** — Save learnings before compaction
- **Convergence Triggers** — "update everything" naturally includes compaction
- **TVC Protocol** — Verify work is saved before compacting
