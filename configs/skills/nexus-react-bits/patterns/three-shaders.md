# Three.js Shader Patterns

Reference patterns for WebGL shader-based backgrounds like ColorBends, Aurora,
etc.

## Basic Three.js Setup

```tsx
import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function Background() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

        // Full-screen quad
        const geometry = new THREE.PlaneGeometry(2, 2);
        const material = new THREE.ShaderMaterial({
            vertexShader: vert,
            fragmentShader: frag,
            uniforms: {/* ... */},
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        // Renderer
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        // Animation loop
        const clock = new THREE.Clock();
        const animate = () => {
            material.uniforms.uTime.value = clock.getElapsedTime();
            renderer.render(scene, camera);
            requestAnimationFrame(animate);
        };
        animate();

        // Cleanup
        return () => {
            geometry.dispose();
            material.dispose();
            renderer.dispose();
        };
    }, []);

    return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
```

## Basic Vertex Shader

```glsl
// vert.glsl - Pass through with UV
varying vec2 vUv;

void main() {
  vUv = uv;
  gl_Position = vec4(position, 1.0);
}
```

## Common Uniforms

```glsl
uniform vec2 uResolution;  // Canvas size
uniform float uTime;       // Elapsed time
uniform vec2 uMouse;       // Mouse position (-1 to 1)
uniform vec3 uColors[8];   // Color palette
```

## Fragment Shader Patterns

### Gradient Animation

```glsl
uniform float uTime;
uniform vec3 uColor1;
uniform vec3 uColor2;
varying vec2 vUv;

void main() {
  float t = sin(uTime * 0.5) * 0.5 + 0.5;
  vec3 color = mix(uColor1, uColor2, vUv.y + t * 0.2);
  gl_FragColor = vec4(color, 1.0);
}
```

### Noise Pattern

```glsl
// Simple noise function
float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

float noise(vec2 st) {
  vec2 i = floor(st);
  vec2 f = fract(st);
  float a = random(i);
  float b = random(i + vec2(1.0, 0.0));
  float c = random(i + vec2(0.0, 1.0));
  float d = random(i + vec2(1.0, 1.0));
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

void main() {
  float n = noise(vUv * 10.0 + uTime);
  gl_FragColor = vec4(vec3(n), 1.0);
}
```

### Wave Pattern

```glsl
void main() {
  vec2 uv = vUv;
  float wave = sin(uv.x * 10.0 + uTime * 2.0) * 0.1;
  float y = uv.y + wave;
  vec3 color = mix(uColor1, uColor2, y);
  gl_FragColor = vec4(color, 1.0);
}
```

### Radial Gradient

```glsl
void main() {
  vec2 center = vec2(0.5);
  float dist = distance(vUv, center);
  float circle = smoothstep(0.5, 0.0, dist);
  vec3 color = mix(uColor2, uColor1, circle);
  gl_FragColor = vec4(color, 1.0);
}
```

### Mouse-Reactive

```glsl
uniform vec2 uMouse;

void main() {
  float dist = distance(vUv, uMouse * 0.5 + 0.5);
  float glow = smoothstep(0.3, 0.0, dist);
  vec3 color = mix(uColor1, uColor2, glow);
  gl_FragColor = vec4(color, 1.0);
}
```

## Color Utilities

### Hex to Vec3 (JavaScript)

```typescript
const hexToVec3 = (hex: string) => {
    const h = hex.replace("#", "");
    return new THREE.Vector3(
        parseInt(h.slice(0, 2), 16) / 255,
        parseInt(h.slice(2, 4), 16) / 255,
        parseInt(h.slice(4, 6), 16) / 255,
    );
};
```

### HSL to RGB (GLSL)

```glsl
vec3 hsl2rgb(vec3 c) {
  vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
  return c.z + c.y * (rgb - 0.5) * (1.0 - abs(2.0 * c.z - 1.0));
}
```

## Mouse Tracking

```typescript
useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
        const x = (e.clientX / window.innerWidth) * 2 - 1;
        const y = -(e.clientY / window.innerHeight) * 2 + 1;
        material.uniforms.uMouse.value.set(x, y);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
}, []);
```

## Smooth Mouse Following

```typescript
const targetMouse = useRef(new THREE.Vector2(0, 0));
const currentMouse = useRef(new THREE.Vector2(0, 0));

// In animation loop
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
currentMouse.current.x = lerp(
    currentMouse.current.x,
    targetMouse.current.x,
    0.1,
);
currentMouse.current.y = lerp(
    currentMouse.current.y,
    targetMouse.current.y,
    0.1,
);
material.uniforms.uMouse.value.copy(currentMouse.current);
```

## Performance Tips

1. **Limit pixel ratio**: `Math.min(window.devicePixelRatio, 2)`
2. **Use `powerPreference`**: `{ powerPreference: 'high-performance' }`
3. **Dispose resources**: Always clean up geometry, materials, textures
4. **Avoid conditionals in shaders**: Use `mix()` and `step()` instead
5. **Pre-calculate constants**: Move math outside the loop when possible
