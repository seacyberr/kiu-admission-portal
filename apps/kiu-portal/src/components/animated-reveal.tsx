import React, { useEffect, useRef } from 'react';
import { motion, useAnimation, useInView } from 'framer-motion';

interface AnimatedRevealProps {
  children: React.ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  delay?: number;
  duration?: number;
  className?: string;
}

export const AnimatedReveal: React.FC<AnimatedRevealProps> = ({
  children,
  direction = 'up',
  delay = 0,
  duration = 0.6,
  className = ''
}) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const controls = useAnimation();

  const getInitialVariant = () => {
    switch (direction) {
      case 'up':
        return { opacity: 0, y: 50 };
      case 'down':
        return { opacity: 0, y: -50 };
      case 'left':
        return { opacity: 0, x: 50 };
      case 'right':
        return { opacity: 0, x: -50 };
      default:
        return { opacity: 0, y: 50 };
    }
  };

  const getAnimateVariant = () => {
    switch (direction) {
      case 'up':
      case 'down':
        return { opacity: 1, y: 0 };
      case 'left':
      case 'right':
        return { opacity: 1, x: 0 };
      default:
        return { opacity: 1, y: 0 };
    }
  };

  useEffect(() => {
    if (isInView) {
      controls.start(getAnimateVariant());
    }
  }, [isInView, controls]);

  return (
    <motion.div
      ref={ref}
      initial={getInitialVariant()}
      animate={controls}
      transition={{
        duration,
        delay,
        ease: [0.25, 0.46, 0.45, 0.94] // easeOutQuart
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// Staggered animation for multiple children
interface StaggeredRevealProps {
  children: React.ReactNode[];
  staggerDelay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  className?: string;
}

export const StaggeredReveal: React.FC<StaggeredRevealProps> = ({
  children,
  staggerDelay = 0.1,
  direction = 'up',
  className = ''
}) => {
  return (
    <div className={className}>
      {children.map((child, index) => (
        <AnimatedReveal
          key={index}
          direction={direction}
          delay={index * staggerDelay}
        >
          {child}
        </AnimatedReveal>
      ))}
    </div>
  );
};