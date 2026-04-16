// Text Animation Base Template
// Use this as a starting point for creating text-based animations

import { useRef, useEffect, useMemo } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

type SplitType = 'chars' | 'words' | 'lines';
type TagType = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span' | 'div';

interface TextAnimationProps {
  /** The text content to animate */
  text: string;
  /** HTML tag to render */
  tag?: TagType;
  /** Additional CSS classes */
  className?: string;
  /** How to split the text */
  splitType?: SplitType;
  /** Animation duration in seconds */
  duration?: number;
  /** Delay before animation starts */
  delay?: number;
  /** GSAP easing function */
  ease?: string;
  /** Stagger time between elements */
  stagger?: number;
  /** Starting animation values */
  from?: gsap.TweenVars;
  /** Ending animation values */
  to?: gsap.TweenVars;
  /** Intersection observer threshold */
  threshold?: number;
  /** Root margin for trigger */
  rootMargin?: string;
  /** Text alignment */
  textAlign?: 'left' | 'center' | 'right';
  /** Callback when animation completes */
  onAnimationComplete?: () => void;
}

export default function TextAnimation({
  text,
  tag: Tag = 'p',
  className = '',
  splitType = 'chars',
  duration = 1,
  delay = 0,
  ease = 'power3.out',
  stagger = 0.05,
  from = { opacity: 0, y: 40 },
  to = { opacity: 1, y: 0 },
  threshold = 0.1,
  rootMargin = '-100px',
  textAlign = 'center',
  onAnimationComplete,
}: TextAnimationProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const hasAnimated = useRef(false);

  // Split text into elements based on splitType
  const elements = useMemo(() => {
    switch (splitType) {
      case 'words':
        return text.split(' ').map((word, i) => (
          <span key={i} className="text-animation-word" style={{ display: 'inline-block' }}>
            {word}
            {i < text.split(' ').length - 1 ? '\u00A0' : ''}
          </span>
        ));
      case 'lines':
        return text.split('\n').map((line, i) => (
          <span key={i} className="text-animation-line" style={{ display: 'block' }}>
            {line}
          </span>
        ));
      case 'chars':
      default:
        return text.split('').map((char, i) => (
          <span
            key={i}
            className="text-animation-char"
            style={{ display: 'inline-block' }}
          >
            {char === ' ' ? '\u00A0' : char}
          </span>
        ));
    }
  }, [text, splitType]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || hasAnimated.current) return;

    const targets = container.querySelectorAll(
      `.text-animation-${splitType === 'chars' ? 'char' : splitType === 'words' ? 'word' : 'line'}`
    );

    // Set initial state
    gsap.set(targets, from);

    // Create intersection observer
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated.current) {
            hasAnimated.current = true;

            gsap.to(targets, {
              ...to,
              duration,
              delay,
              ease,
              stagger,
              onComplete: onAnimationComplete,
            });

            observer.disconnect();
          }
        });
      },
      { threshold, rootMargin }
    );

    observer.observe(container);

    return () => observer.disconnect();
  }, [splitType, from, to, duration, delay, ease, stagger, threshold, rootMargin, onAnimationComplete]);

  return (
    <Tag
      ref={containerRef as any}
      className={`text-animation-container ${className}`}
      style={{ textAlign }}
    >
      {elements}
    </Tag>
  );
}

// Usage Example:
// <TextAnimation
//   text="Hello World"
//   tag="h1"
//   splitType="chars"
//   duration={0.8}
//   stagger={0.03}
//   from={{ opacity: 0, y: 50, rotateX: -90 }}
//   to={{ opacity: 1, y: 0, rotateX: 0 }}
// />
