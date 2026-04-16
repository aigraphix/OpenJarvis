# GSAP Animation Patterns

Reference patterns for creating animations with GSAP in React Bits style.

## Basic Timeline

```tsx
import { gsap } from "gsap";

const tl = gsap.timeline({
    defaults: {
        duration: 1,
        ease: "power3.out",
    },
});

tl.from(".element", { opacity: 0, y: 50 })
    .from(".element2", { opacity: 0, x: -50 }, "-=0.5") // overlaps previous
    .to(".element", { scale: 1.1 }, "+=0.2"); // delay after previous
```

## Stagger Animation

```tsx
// Stagger through array of elements
gsap.from(".items", {
    opacity: 0,
    y: 40,
    duration: 0.8,
    stagger: {
        each: 0.05, // Time between each
        from: "start", // 'start', 'end', 'center', 'edges', 'random'
        grid: "auto", // For grid layouts
        ease: "power2.in", // Easing of stagger timing
    },
});
```

## Common Easing Functions

| Ease                  | Description         | Use Case             |
| --------------------- | ------------------- | -------------------- |
| `power1.out`          | Gentle deceleration | Subtle movements     |
| `power2.out`          | Medium deceleration | General purpose      |
| `power3.out`          | Strong deceleration | Dramatic entrances   |
| `power4.out`          | Very strong decel   | Snappy feel          |
| `back.out(1.7)`       | Overshoot           | Bouncy elements      |
| `elastic.out(1, 0.3)` | Elastic bounce      | Playful animations   |
| `expo.out`            | Exponential         | Fast start, slow end |

## Scroll-Triggered Animation

```tsx
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

gsap.from(".element", {
    scrollTrigger: {
        trigger: ".element",
        start: "top 80%", // When top of element hits 80% of viewport
        end: "bottom 20%",
        toggleActions: "play none none reverse",
        // scrub: true,        // Tie animation to scroll position
        // pin: true,          // Pin element during animation
        // markers: true,      // Debug markers
    },
    opacity: 0,
    y: 100,
    duration: 1,
});
```

## React useEffect Pattern

```tsx
useEffect(() => {
    const ctx = gsap.context(() => {
        // All animations scoped to container
        gsap.from(".item", { opacity: 0, y: 50, stagger: 0.1 });
    }, containerRef); // Scope to ref

    return () => ctx.revert(); // Cleanup
}, []);
```

## Text Split Animation

```tsx
// Split text into spans first
const splitText = (text: string) => {
    return text.split("").map((char, i) => (
        <span key={i} className="char" style={{ display: "inline-block" }}>
            {char === " " ? "\u00A0" : char}
        </span>
    ));
};

// Then animate
gsap.from(".char", {
    opacity: 0,
    y: 50,
    rotateX: -90,
    duration: 0.8,
    ease: "back.out(1.7)",
    stagger: 0.02,
});
```

## Hover Animation

```tsx
const handleMouseEnter = () => {
    gsap.to(elementRef.current, {
        scale: 1.1,
        boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
        duration: 0.3,
    });
};

const handleMouseLeave = () => {
    gsap.to(elementRef.current, {
        scale: 1,
        boxShadow: "0 0 0 rgba(0,0,0,0)",
        duration: 0.3,
    });
};
```

## Magnetic Cursor Effect

```tsx
const handleMouseMove = (e: MouseEvent) => {
    const rect = element.getBoundingClientRect();
    const x = e.clientX - (rect.left + rect.width / 2);
    const y = e.clientY - (rect.top + rect.height / 2);

    gsap.to(element, {
        x: x * 0.3, // 30% of distance
        y: y * 0.3,
        duration: 0.3,
        ease: "power2.out",
    });
};
```

## Infinite Loop

```tsx
gsap.to(".element", {
    rotate: 360,
    duration: 10,
    ease: "none",
    repeat: -1, // Infinite
});

// Or with timeline
const tl = gsap.timeline({ repeat: -1, yoyo: true });
tl.to(".element", { scale: 1.2, duration: 1 })
    .to(".element", { scale: 1, duration: 1 });
```

## Performance Tips

1. **Use `will-change`**: Add to animated elements
   ```css
   .animated {
       will-change: transform, opacity;
   }
   ```

2. **Prefer transforms**: `x`, `y`, `scale`, `rotate` over `top`, `left`

3. **Use `force3D`**: Enables GPU acceleration
   ```tsx
   gsap.to(".element", { x: 100, force3D: true });
   ```

4. **Kill animations on unmount**:
   ```tsx
   useEffect(() => {
     const animation = gsap.to(...);
     return () => animation.kill();
   }, []);
   ```

5. **Use context for cleanup**:
   ```tsx
   const ctx = gsap.context(() => { ... }, ref);
   return () => ctx.revert();
   ```
