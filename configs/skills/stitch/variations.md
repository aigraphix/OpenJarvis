---
name: stitch:variations
description: Generate multiple design variations in Stitch to explore layouts, themes, and styles. Use Creative Range to control how far designs diverge from the original.
---

# Stitch Variations Skill

## Overview

Variations let you generate **1–5 design options at once**, breaking out of
linear editing. Instead of tweaking one screen, you explore multiple directions
simultaneously and pick the winner.

## When to Use Variations (vs. Standard Chat)

| Scenario                                            | Use Variations | Use Standard Chat |
| --------------------------------------------------- | -------------- | ----------------- |
| "I don't know what's wrong, but this isn't working" | ✅             |                   |
| "Show me 3 different layout concepts"               | ✅             |                   |
| "Change the entire vibe to cyberpunk"               | ✅             |                   |
| "Change this button color to #ff6b35"               |                | ✅                |
| "Make the header font bigger"                       |                | ✅                |

**Rule of thumb**: Standard Chat = one specific change. Variations = big swings
and exploration.

## Creative Range

Every variation request includes a **Creative Range** that controls divergence:

### Refined (Low Range)

- Keeps structure intact
- Adjusts fonts, subtle spacing, colors
- **Use for**: Polish, fine-tuning, A/B testing minor differences
- **Example**: "Try 3 different color schemes for this dashboard"

### Creative (High Range)

- Complete restructuring allowed
- Can swap imagery, overhaul theme, rebuild layout
- **Use for**: Exploration, pivoting direction, getting unstuck
- **Example**: "Reimagine this as a luxury brand experience"

## Prompt Writing for Variations

Unlike standard editing (one change at a time), **Variations are the place for
big, combined prompts**. You can mix theme + layout + content changes in a
single request.

### Anatomy of a Good Variations Prompt

```
[Set the vibe] + [Specific color/style request] + [Target screen] + [Clear instruction]
```

### Example Prompts

**Exploration (High Range):**

```
Update the app theme to a luxury aesthetic using a strict black and white palette.
On the Episode List screen, change the layout to a minimalist grid.
```

**Getting Unstuck (High Range):**

```
This dashboard feels too corporate. Show me 5 completely different directions —
try warm earth tones, dark neon, soft pastels, brutalist, and glassmorphism.
```

**Polish (Low Range):**

```
Keep the current layout but try 3 different font pairings and adjust
the spacing between cards for better readability.
```

**Pivoting (High Range):**

```
Transform this from a healthcare app into a fitness app aesthetic.
Use energetic colors, bold typography, and dynamic card layouts.
```

## Iteration Workflow: Pick → Refine → Converge

### Step 1: Generate (High Range, 3-5 options)

Run variations with a broad prompt. Let Stitch explore freely.

### Step 2: Pick the Winner

Select the variation closest to your vision. It doesn't need to be perfect.

### Step 3: Vary the Variation (Low Range)

Run variations _on top of_ your winner with Refined range. Cherry-pick elements
from other options.

**Example iteration:**

```
Round 1 (Creative): "Show me 5 dashboard layouts for a fitness app"
  → Option 3 has the best layout, Option 5 has the better colors

Round 2 (Refined): Select Option 3, then:
  "Keep this layout but adopt the teal-and-coral color scheme
   from the previous Option 5. Polish the typography."
  
Round 3 (Refined): Final polish
  "Tighten the card spacing, add subtle shadows, and ensure
   the CTA button has maximum contrast."
```

## Anti-Patterns (Don't Do This)

| ❌ Bad                                | ✅ Better                                                                 |
| ------------------------------------- | ------------------------------------------------------------------------- |
| "Make it different"                   | "Make it minimalist with more whitespace"                                 |
| "Try some variations"                 | "Show me 3 dark-mode versions with neon accents"                          |
| "I don't like it, change everything"  | "The layout works but the color scheme feels cold — try warm earth tones" |
| Using Creative range for small tweaks | Use Refined range for polish                                              |
| Using Refined range when you're stuck | Use Creative range for exploration                                        |

## Integration with React Workflow

After selecting a winning variation:

1. **Download the HTML** via `get_screen`
2. **Download the reference PNG** for visual QA
3. **Convert to React components** using `react:components` skill
4. **Compare** the live React output against the PNG
5. **Iterate** if the conversion misses any details

## Quick Reference

```
Variations API call pattern:
  generate_screen_from_text →
    project_id: "<project>"
    prompt: "<your variations prompt>"
    model_id: "GEMINI_3_PRO"  (use Pro for variations — quality matters)

Creative Range is set in the Stitch UI, not via MCP API.
When calling via MCP, write your prompt to imply the range:
  - For Refined: "Keep the current layout but try..."  
  - For Creative: "Reimagine / Transform / Show me completely different..."
```
