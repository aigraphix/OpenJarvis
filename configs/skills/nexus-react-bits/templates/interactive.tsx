// Interactive Component Base Template
// Use this for hover effects, click animations, and cursor-following effects

import { useRef, useEffect, useState, useCallback } from 'react';
import { gsap } from 'gsap';

interface InteractiveProps {
  /** Child content */
  children: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Inline styles */
  style?: React.CSSProperties;
  /** Enable magnetic cursor effect */
  magnetic?: boolean;
  /** Magnetic strength (0-1) */
  magneticStrength?: number;
  /** Enable glow on hover */
  glowOnHover?: boolean;
  /** Glow color */
  glowColor?: string;
  /** Enable scale on hover */
  scaleOnHover?: boolean;
  /** Scale amount */
  scaleAmount?: number;
  /** Animation duration */
  duration?: number;
  /** GSAP easing */
  ease?: string;
  /** Click callback */
  onClick?: () => void;
}

export default function Interactive({
  children,
  className = '',
  style,
  magnetic = true,
  magneticStrength = 0.3,
  glowOnHover = true,
  glowColor = 'rgba(99, 102, 241, 0.5)',
  scaleOnHover = true,
  scaleAmount = 1.05,
  duration = 0.3,
  ease = 'power2.out',
  onClick,
}: InteractiveProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  // Magnetic effect
  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!magnetic || !containerRef.current || !contentRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const deltaX = (e.clientX - centerX) * magneticStrength;
      const deltaY = (e.clientY - centerY) * magneticStrength;

      gsap.to(contentRef.current, {
        x: deltaX,
        y: deltaY,
        duration: duration * 0.5,
        ease,
      });
    },
    [magnetic, magneticStrength, duration, ease]
  );

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);

    if (contentRef.current) {
      gsap.to(contentRef.current, {
        scale: scaleOnHover ? scaleAmount : 1,
        duration,
        ease,
      });
    }
  }, [scaleOnHover, scaleAmount, duration, ease]);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);

    if (contentRef.current) {
      gsap.to(contentRef.current, {
        x: 0,
        y: 0,
        scale: 1,
        duration,
        ease,
      });
    }
  }, [duration, ease]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('mouseenter', handleMouseEnter);
    container.addEventListener('mouseleave', handleMouseLeave);
    container.addEventListener('mousemove', handleMouseMove);

    return () => {
      container.removeEventListener('mouseenter', handleMouseEnter);
      container.removeEventListener('mouseleave', handleMouseLeave);
      container.removeEventListener('mousemove', handleMouseMove);
    };
  }, [handleMouseEnter, handleMouseLeave, handleMouseMove]);

  return (
    <div
      ref={containerRef}
      className={`interactive-container ${className}`}
      style={{
        position: 'relative',
        display: 'inline-block',
        cursor: 'pointer',
        ...style,
      }}
      onClick={onClick}
    >
      {/* Glow effect */}
      {glowOnHover && (
        <div
          style={{
            position: 'absolute',
            inset: -10,
            borderRadius: 'inherit',
            background: glowColor,
            filter: 'blur(20px)',
            opacity: isHovered ? 0.6 : 0,
            transition: `opacity ${duration}s ease`,
            pointerEvents: 'none',
          }}
        />
      )}

      {/* Content */}
      <div
        ref={contentRef}
        style={{
          position: 'relative',
          willChange: 'transform',
        }}
      >
        {children}
      </div>
    </div>
  );
}

// Usage Example:
// <Interactive
//   magnetic
//   magneticStrength={0.4}
//   glowOnHover
//   glowColor="rgba(147, 51, 234, 0.5)"
//   scaleOnHover
//   scaleAmount={1.1}
// >
//   <button className="my-button">Hover Me</button>
// </Interactive>
