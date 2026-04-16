# MCP Apps UX & UI Design Guidelines

> **For Nexus Agents**: Follow these principles when creating or modifying MCP
> Apps widgets. Source: OpenAI Apps SDK Documentation (2026-02)

---

## 🎯 Core UX Principles

### 1. Extract, Don't Port

- **DO**: Focus on core jobs users need
- **DO**: Identify atomic actions that can be extracted as tools
- **DON'T**: Mirror your full website or app
- Each tool should expose **minimum inputs and outputs** needed

### 2. Design for Conversational Entry

Support multiple entry patterns:

- **Open-ended prompts**: "Help me plan a team offsite"
- **Direct commands**: "Book the conference room Thursday at 3pm"
- **First-run onboarding**: Teach users how to engage through ChatGPT

### 3. Design for the ChatGPT Environment

- Use UI **selectively** to clarify actions, capture inputs, or present
  structured results
- Skip ornamental components that don't advance the current task
- Lean on conversation for history, confirmation, and follow-up

### 4. Optimize for Conversation, Not Navigation

The model handles state management and routing. Your app supplies:

- **Clear, declarative actions** with well-typed parameters
- **Concise responses** (tables, lists, short paragraphs) instead of dashboards
- **Helpful follow-up suggestions** so the model can keep the user in flow

### 5. Embrace the Ecosystem

- Accept rich natural language instead of form fields
- Personalize with context from the conversation
- Compose with other apps when it saves user time

---

## 📋 Pre-Publish Checklist

| Question                                                       | Required Answer |
| -------------------------------------------------------------- | --------------- |
| Does at least one capability rely on ChatGPT's strengths?      | ✅ Yes          |
| Does the app provide new knowledge/actions/presentation?       | ✅ Yes          |
| Are tools atomic, model-friendly with explicit inputs/outputs? | ✅ Yes          |
| Would replacing widgets with plain text degrade UX?            | ✅ Yes          |
| Can users finish at least one task without leaving ChatGPT?    | ✅ Yes          |
| Does the app respond quickly enough for chat rhythm?           | ✅ Yes          |
| Is it easy to imagine prompts where model would select this?   | ✅ Yes          |

### ❌ Avoid

- Long-form or static content better suited for websites
- Complex multi-step workflows exceeding display modes
- Ads, upsells, or irrelevant messaging
- Sensitive/private information directly in cards
- Duplicating ChatGPT's system functions (e.g., input composer)

---

## 🎨 Visual Design Guidelines

### Color

| Do                                          | Don't                               |
| ------------------------------------------- | ----------------------------------- |
| Use system colors for text, icons, dividers | Override backgrounds or text colors |
| Use brand accent colors on primary buttons  | Use custom gradients or patterns    |
| Apply brand colors to accents and badges    | Change core component styles        |

### Typography

- **Always inherit system font stack** (SF Pro on iOS, Roboto on Android)
- Use partner styling (bold, italic) only within content areas
- Limit font size variation - prefer `body` and `body-small`
- **Never use custom fonts**, even in fullscreen modes

### Spacing & Layout

- Use system grid spacing for cards and panels
- Keep padding consistent - no edge-to-edge text
- Respect system corner radius for shape consistency
- Maintain visual hierarchy: Headline → Supporting text → CTA

### Icons & Imagery

- Use system icons OR custom monochromatic outlined icons
- **Don't include your logo in the response** - ChatGPT appends it automatically
- All imagery must follow enforced aspect ratios

### Accessibility (MANDATORY)

- ✅ Text + background must meet **WCAG AA contrast ratio**
- ✅ Provide **alt text for all images**
- ✅ Support **text resizing** without breaking layouts

---

## 📱 Display Modes

### 1. Inline Card

Lightweight, single-purpose widgets embedded in conversation.

**When to use:**

- Single action or decision (confirm booking)
- Small structured data (map, order summary, status)
- Fully self-contained widget (audio player, score card)

**Rules:**

- Max 2 primary actions at bottom
- No deep navigation or multiple views
- No nested scrolling - auto-fit content
- No duplicative inputs (don't replicate ChatGPT features)

### 2. Inline Carousel

Side-by-side cards for scanning multiple options.

**When to use:**

- Small list of similar items (restaurants, playlists, events)
- Items with more visual content than fits in rows

**Rules:**

- Keep 3-8 items for scannability
- Reduce metadata to 3 lines max
- Single optional CTA per card
- Use consistent visual hierarchy

### 3. Fullscreen

Immersive experiences for multi-step workflows.

**When to use:**

- Rich tasks that can't fit in a single card
- Browsing detailed content (listings, menus)

**Rules:**

- Design UX to work with the system composer
- Don't replicate your native app wholesale
- Composer is always present

### 4. Picture-in-Picture (PiP)

Persistent floating window for ongoing sessions.

**When to use:**

- Activities running parallel to conversation (games, videos)
- Widget that reacts to chat input

**Rules:**

- Close automatically when session ends
- Don't overload with static content
- Must update/respond to composer input

---

## 🚀 Nexus Widget Standards

When building Nexus MCP Apps widgets, apply these additional standards:

### Theme

```css
:root {
    --bg-primary: #0a0a0b; /* Obsidian */
    --bg-secondary: #141416;
    --bg-card: #1a1a1d;
    --border: #2a2a2e;
    --text-primary: #ffffff;
    --text-secondary: #a0a0a5;
    --accent: #ff6b35; /* Rocket Orange */
    --accent-glow: rgba(255, 107, 53, 0.3);
    --success: #22c55e;
    --warning: #f59e0b;
    --error: #ef4444;
}
```

### Spacing

- Use 8px base unit
- Card padding: 16px
- Gap between elements: 12px
- Border radius: 8px (cards), 4px (buttons)

### Typography

- Headers: 18px, font-weight 600
- Body: 14px, line-height 1.5
- Caption: 11px, uppercase, letter-spacing 0.5px

### Actions

- Primary: Filled button with accent color
- Secondary: Ghost button with border
- Max 2 actions per card

---

## 📚 Resources

- [Apps SDK UI (Storybook)](https://openai.github.io/apps-sdk-ui/)
- [Figma Component Library](https://www.figma.com/community/file/1560064615791108827)
- [UX Principles](https://developers.openai.com/apps-sdk/concepts/ux-principles)
- [UI Guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)
- [MCP Apps Spec](https://modelcontextprotocol.io/docs/extensions/apps)

---

_Last Updated: 2026-02-04_ _For Nexus Agents: creative, coder, architect_
