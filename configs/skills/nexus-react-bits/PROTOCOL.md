# React Bits Component Creation Protocol

## Overview

This protocol defines how agents should help users create, customize, and
integrate React Bits components.

---

## Protocol 1: Install Existing Component

### Trigger

User asks to add a React Bits component that exists in the registry.

### Steps

1. **Identify Component**
   ```
   User: "Add the Aurora background"
   Agent: Searching for "aurora" in @react-bits registry...
   ```

2. **Check Dependencies**
   ```
   This component requires: three, @react-three/fiber
   Installing dependencies first...
   ```

3. **Install via shadcn CLI**
   ```bash
   npx shadcn@latest add @react-bits/aurora
   ```

4. **Provide Usage Example**
   ```tsx
   import { Aurora } from "@/components/ui/aurora";

   <Aurora
       colorStops={["#3A29FF", "#FF94B4", "#FF3232"]}
       speed={1.0}
       amplitude={1.0}
   />;
   ```

5. **Verify Installation (TVC)**
   - Test: Check file exists
   - Verify: Import works
   - Confirm: Show user the file location

---

## Protocol 2: Custom Component via Dashboard

### Trigger

User wants a customized version of a component, or asks "I want a custom
[component type]".

### Steps

1. **Offer Dashboard Option**
   ```
   Agent: "Would you like to create a custom component using the React Bits dashboard?

   The dashboard has interactive controls for:
   - Colors and gradients
   - Speed and timing
   - Effect intensity
   - Size and scale

   Shall I guide you through it?"
   ```

2. **Direct to Dashboard**
   ```
   Agent: "Here's how to create your custom component:

   1. 🌐 Go to: https://reactbits.dev/backgrounds/color-bends
   2. 🎨 Use the 'Customize' tab to adjust:
      - Colors (click color pickers)
      - Speed slider
      - Warp strength
      - Mouse influence
      - etc.
   3. 👀 Preview updates in real-time
   4. 📋 Click 'Code' tab when satisfied
   5. 📝 Copy the full component code
   6. 📤 Paste it here

   I'll help you integrate it into your project!"
   ```

3. **Receive Code from User** User pastes the component code.

4. **Parse and Organize**
   ```
   Agent: "I received your ColorBends component. Here's what I'll do:

   ✅ Create: components/ui/color-bends.tsx
   ✅ Create: components/ui/color-bends.css
   ✅ Install: three (dependency)
   ✅ Generate: Usage example

   Proceed?"
   ```

5. **Create Files**
   - Split JSX and CSS into separate files
   - Add TypeScript types if requested
   - Add to component index

6. **Verify (TVC)**
   - Test: File created
   - Verify: No syntax errors
   - Confirm: Show import statement

---

## Protocol 3: Generate New Component

### Trigger

User wants a completely new component based on patterns.

### Steps

1. **Gather Requirements**
   ```
   Agent: "What type of component do you need?

   A) Text Animation (like SplitText, GradientText)
   B) Background (like Aurora, Particles)
   C) Interactive Effect (like Magnet, ClickSpark)
   D) UI Component (like AnimatedList, TiltedCard)

   And what effect are you looking for?"
   ```

2. **Select Base Template** Based on category, use appropriate template from
   `templates/`.

3. **Customize Template**
   ```
   Agent: "I'll create a custom text animation with:
   - Split by: characters
   - Effect: fade up with rotation
   - Timing: staggered 50ms
   - Trigger: on scroll into view

   Here's the generated component..."
   ```

4. **Generate Code** Use template + patterns to generate component.

5. **Review with User** Show generated code, ask for adjustments.

6. **Create Files and Verify (TVC)**

---

## Component Structure Standard

Every React Bits component follows this structure:

```tsx
// ComponentName.tsx
import { useEffect, useRef } from "react";
// Dependencies (gsap, three, etc.)

// Props interface
interface ComponentNameProps {
    // Required props
    // Optional props with defaults
    className?: string;
    style?: React.CSSProperties;
}

// Component implementation
export default function ComponentName({
    className = "",
    style,
    // destructure props with defaults
}: ComponentNameProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Setup animation/effect
        // Return cleanup function
    }, [/* dependencies */]);

    return (
        <div ref={containerRef} className={className} style={style}>
            {/* Component content */}
        </div>
    );
}
```

```css
/* ComponentName.css */
.component-container {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
}
```

---

## Props Reference

### Common Props (all components)

| Prop        | Type          | Default | Description            |
| ----------- | ------------- | ------- | ---------------------- |
| `className` | string        | ""      | Additional CSS classes |
| `style`     | CSSProperties | {}      | Inline styles          |

### Animation Props

| Prop       | Type   | Default      | Description                  |
| ---------- | ------ | ------------ | ---------------------------- |
| `duration` | number | 1.0          | Animation duration (seconds) |
| `delay`    | number | 0            | Start delay (seconds)        |
| `ease`     | string | "power3.out" | GSAP easing                  |
| `stagger`  | number | 0.05         | Stagger between items        |

### Background Props

| Prop          | Type     | Default                | Description            |
| ------------- | -------- | ---------------------- | ---------------------- |
| `colors`      | string[] | ["#3A29FF", "#FF94B4"] | Color stops            |
| `speed`       | number   | 1.0                    | Animation speed        |
| `scale`       | number   | 1.0                    | Effect scale           |
| `transparent` | boolean  | true                   | Transparent background |

### Interactive Props

| Prop             | Type   | Default  | Description            |
| ---------------- | ------ | -------- | ---------------------- |
| `mouseInfluence` | number | 1.0      | Mouse effect strength  |
| `threshold`      | number | 0.1      | Intersection threshold |
| `rootMargin`     | string | "-100px" | Trigger margin         |

---

## Error Handling

### Missing Dependencies

```
Error: Cannot find module 'three'

Agent Response:
"This component requires Three.js. Installing now..."
npm install three @types/three
```

### TypeScript Errors

```
Agent: "The component is written in JavaScript. Would you like me to:
A) Convert to TypeScript with proper types
B) Keep as JavaScript with JSDoc types
C) Keep as JavaScript without types"
```

### CSS Conflicts

```
Agent: "The component CSS uses '.container' which may conflict.
Renaming to '.color-bends-container' for isolation."
```

---

## Dashboard URLs Reference

| Category        | Base URL                                     |
| --------------- | -------------------------------------------- |
| Text Animations | https://reactbits.dev/text-animations/{name} |
| Backgrounds     | https://reactbits.dev/backgrounds/{name}     |
| Animations      | https://reactbits.dev/animations/{name}      |
| Components      | https://reactbits.dev/components/{name}      |

### Popular Components

| Component    | Dashboard URL                                       |
| ------------ | --------------------------------------------------- |
| ColorBends   | https://reactbits.dev/backgrounds/color-bends       |
| Aurora       | https://reactbits.dev/backgrounds/aurora            |
| Particles    | https://reactbits.dev/backgrounds/particles         |
| SplitText    | https://reactbits.dev/text-animations/split-text    |
| GradientText | https://reactbits.dev/text-animations/gradient-text |
| FadeContent  | https://reactbits.dev/animations/fade-content       |
| AnimatedList | https://reactbits.dev/components/animated-list      |
| TiltedCard   | https://reactbits.dev/components/tilted-card        |

---

## Quality Checklist

Before completing any React Bits task:

- [ ] Dependencies installed
- [ ] Component file created
- [ ] CSS file created (if separate)
- [ ] No TypeScript errors
- [ ] Usage example provided
- [ ] Import statement shown
- [ ] Props documented
