import React from 'react';
import { cn } from '@/shared/utils/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> & {
  Header: React.FC<CardHeaderProps>;
  Body: React.FC<CardBodyProps>;
  Footer: React.FC<CardFooterProps>;
} = ({ 
  children, 
  padding = 'md',
  shadow = 'md',
  className,
  ...props 
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg'
  };

  return (
    <div
      className={cn(
        'bg-white rounded-xl border border-slate-200',
        shadowClasses[shadow],
        paddingClasses[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

const CardHeader: React.FC<CardHeaderProps> = ({ 
  children, 
  title, 
  subtitle, 
  action,
  className,
  ...props 
}) => (
  <div
    className={cn(
      'flex items-start justify-between mb-4',
      className
    )}
    {...props}
  >
    <div className="flex-1">
      {title && (
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      )}
      {subtitle && (
        <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
      )}
      {children}
    </div>
    {action && <div className="ml-4">{action}</div>}
  </div>
);

interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardBody: React.FC<CardBodyProps> = ({ 
  children, 
  className,
  ...props 
}) => (
  <div className={cn('', className)} {...props}>
    {children}
  </div>
);

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

const CardFooter: React.FC<CardFooterProps> = ({ 
  children, 
  align = 'left',
  className,
  ...props 
}) => {
  const alignClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end'
  };

  return (
    <div
      className={cn(
        'flex items-center gap-3 mt-6 pt-4 border-t border-slate-100',
        alignClasses[align],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;
