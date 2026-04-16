// Background Base Template
// Use this as a starting point for WebGL/Canvas background components

import { useRef, useEffect, useCallback } from 'react';

interface BackgroundProps {
  /** Color stops for gradient/effect */
  colors?: string[];
  /** Animation speed multiplier */
  speed?: number;
  /** Effect scale */
  scale?: number;
  /** Additional CSS classes */
  className?: string;
  /** Inline styles */
  style?: React.CSSProperties;
  /** Child content to overlay */
  children?: React.ReactNode;
  /** Enable transparency */
  transparent?: boolean;
}

export default function Background({
  colors = ['#3A29FF', '#FF94B4', '#FF3232'],
  speed = 1.0,
  scale = 1.0,
  className = '',
  style,
  children,
  transparent = false,
}: BackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(Date.now());

  // Parse hex color to RGB
  const hexToRgb = useCallback((hex: string) => {
    const h = hex.replace('#', '');
    return {
      r: parseInt(h.slice(0, 2), 16) / 255,
      g: parseInt(h.slice(2, 4), 16) / 255,
      b: parseInt(h.slice(4, 6), 16) / 255,
    };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle resize
    const handleResize = () => {
      const rect = container.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio, 2);
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      ctx.scale(dpr, dpr);
    };

    handleResize();

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    // Animation loop
    const animate = () => {
      const elapsed = (Date.now() - startTimeRef.current) / 1000;
      const t = elapsed * speed;

      const { width, height } = container.getBoundingClientRect();
      ctx.clearRect(0, 0, width, height);

      // Example: Animated gradient
      const gradient = ctx.createLinearGradient(
        0,
        0,
        width * Math.sin(t * 0.5) + width,
        height * Math.cos(t * 0.3) + height
      );

      colors.forEach((color, i) => {
        const offset = (i / (colors.length - 1) + t * 0.1) % 1;
        gradient.addColorStop(Math.abs(offset), color);
      });

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // Add animated circles (example effect)
      colors.forEach((color, i) => {
        const rgb = hexToRgb(color);
        const x = (Math.sin(t + i) * 0.3 + 0.5) * width;
        const y = (Math.cos(t * 0.7 + i * 2) * 0.3 + 0.5) * height;
        const radius = (Math.sin(t * 0.5 + i) * 0.5 + 1) * 100 * scale;

        const circleGradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
        circleGradient.addColorStop(0, `rgba(${rgb.r * 255}, ${rgb.g * 255}, ${rgb.b * 255}, 0.8)`);
        circleGradient.addColorStop(1, `rgba(${rgb.r * 255}, ${rgb.g * 255}, ${rgb.b * 255}, 0)`);

        ctx.fillStyle = circleGradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
      });

      rafRef.current = requestAnimationFrame(animate);
    };

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      resizeObserver.disconnect();
    };
  }, [colors, speed, scale, hexToRgb]);

  return (
    <div
      ref={containerRef}
      className={`background-container ${className}`}
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        ...style,
      }}
    >
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
        }}
      />
      {children && (
        <div style={{ position: 'relative', zIndex: 1 }}>
          {children}
        </div>
      )}
    </div>
  );
}

// Usage Example:
// <Background
//   colors={['#667eea', '#764ba2', '#f093fb']}
//   speed={0.5}
//   scale={1.5}
// >
//   <h1>Content on top of background</h1>
// </Background>
