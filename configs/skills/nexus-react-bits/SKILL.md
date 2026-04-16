# React Bits Component Skill

---
name: React Bits Components
description: Browse, install, customize, and create animated React components using React Bits patterns
---

## Purpose

Enable agents to work with the React Bits component library - a collection of
80+ animated React components including text animations, backgrounds,
interactive effects, and UI components.

## Capabilities

### 1. 🔍 Browse & Search

Search the React Bits registry for components via the shadcn MCP server.

```
"Show me all available backgrounds from React Bits"
"Find text animation components"
"List all hover effect components"
```

### 2. 📦 Install Components

Add components to a project using shadcn CLI.

```
"Add the Aurora background from React Bits"
"Install the SplitText animation"
```

### 3. ✨ Customize Components

Modify props, colors, and behavior of installed components.

```
"Change the Aurora colors to purple and orange"
"Make the text animation faster with 0.5s duration"
```

### 4. 🎨 Create Custom Components

Help users create custom components using the React Bits dashboard.

#### Workflow:

1. Agent asks: "Would you like to create a custom animated component?"
2. If yes, agent directs user to:
   https://reactbits.dev/backgrounds/[component-type]
3. User customizes in the dashboard (colors, speed, effects, etc.)
4. User copies the code from the "Code" tab
5. Agent helps integrate into the project

### 5. 🔧 Generate New Components

Create new components following React Bits patterns using templates.

## Component Categories

| Category            | Count | Description                                    |
| ------------------- | ----- | ---------------------------------------------- |
| **Text Animations** | 20+   | Split text, blur, gradient, glitch, typewriter |
| **Backgrounds**     | 30+   | Aurora, particles, dither, lightning, waves    |
| **Animations**      | 15+   | Fade, electric border, magnet, click spark     |
| **Components**      | 15+   | Animated list, tilted card, dock, carousel     |

## Quick Commands

### Browse

```
"List React Bits text animations"
"Show me all background components"
"What hover effects are available?"
```

### Install

```
"Add ColorBends background to my project"
"Install SplitText with TypeScript"
```

### Customize

```
"Create a ColorBends with these colors: #ff5c7a, #8a5cff, #00ffd1"
"Make the Aurora faster with higher amplitude"
```

### Custom Creation Flow

```
User: "I want a custom animated background"
Agent: "Would you like to create a custom component using the React Bits dashboard?

1. Go to https://reactbits.dev/backgrounds/color-bends
2. Customize using the interactive controls (colors, speed, warp, etc.)
3. Click the 'Code' tab
4. Copy the component code

Paste the code here and I'll help integrate it into your project."
```

## Registry Configuration

Add to your project's `components.json`:

```json
{
    "registries": {
        "@react-bits": "https://reactbits.dev/r/{name}.json"
    }
}
```

## Dependencies

Most React Bits components require:

| Package         | Purpose                             |
| --------------- | ----------------------------------- |
| `gsap`          | Animation library (text animations) |
| `three`         | 3D graphics (backgrounds)           |
| `framer-motion` | React animations (some components)  |

Install common dependencies:

```bash
npm install gsap three @react-three/fiber
```

## Templates

See `templates/` directory for base component patterns:

- `text-animation.tsx` - Text animation base
- `background.tsx` - WebGL/Canvas background base
- `interactive.tsx` - Hover/click effect base
- `composite.tsx` - Combined UI component base

## Patterns

See `patterns/` directory for animation techniques:

- `gsap-patterns.md` - GSAP timeline patterns
- `scroll-triggers.md` - Intersection observer patterns
- `three-shaders.md` - Three.js shader patterns

## Examples

See `examples/` directory for complete component implementations:

- `color-bends.tsx` - Full ColorBends implementation
- `split-text.tsx` - SplitText with customizations
- `aurora.tsx` - Aurora background

## MCP Integration

The skill works with the shadcn MCP server. Available tools:

| Tool                 | Purpose                         |
| -------------------- | ------------------------------- |
| `list_components`    | List all components in registry |
| `search_components`  | Search by name or category      |
| `get_component_docs` | Get props and usage             |
| `install_component`  | Add to project                  |

## Agent Assignment

| Agent      | Role                                     |
| ---------- | ---------------------------------------- |
| `creative` | Primary - Design, colors, visual effects |
| `coder`    | Secondary - Implementation, TypeScript   |
| `writer`   | Support - Documentation                  |

## Resources

- [React Bits](https://reactbits.dev/)
- [React Bits Dashboard](https://reactbits.dev/backgrounds/)
- [shadcn MCP Docs](https://ui.shadcn.com/docs/mcp)
- [GSAP Documentation](https://gsap.com/docs/)
