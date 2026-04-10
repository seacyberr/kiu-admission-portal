/**
 * Avatar Component - User profile picture display
 */
import React from 'react';
import { cn } from '@/shared/utils/cn';

interface AvatarProps {
  src?: string;
  name?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  name = '?',
  className,
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
  };

  // Generate initials from name
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  // Generate consistent color from name
  const colors = [
    'bg-blue-500',
    'bg-indigo-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-rose-500',
    'bg-orange-500',
    'bg-amber-500',
    'bg-emerald-500',
    'bg-teal-500',
    'bg-cyan-500',
  ];
  const colorIndex = name.charCodeAt(0) % colors.length;
  const bgColor = colors[colorIndex];

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className={cn(
          'rounded-full object-cover border-2 border-white shadow-sm',
          sizeClasses[size],
          className
        )}
      />
    );
  }

  return (
    <div
      className={cn(
        'rounded-full flex items-center justify-center text-white font-medium border-2 border-white shadow-sm',
        bgColor,
        sizeClasses[size],
        className
      )}
    >
      {initials}
    </div>
  );
};
