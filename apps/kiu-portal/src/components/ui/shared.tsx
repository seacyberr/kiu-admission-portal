import React from 'react';
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { Loader2 } from "lucide-react";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function Button({ 
  className, variant = 'primary', size = 'default', isLoading, children, ...props 
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { 
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'ghost' | 'destructive',
  size?: 'sm' | 'default' | 'lg' | 'icon',
  isLoading?: boolean 
}) {
  const baseStyles = "inline-flex items-center justify-center rounded-xl text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]";
  
  const variants = {
    primary: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-md hover:shadow-lg",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
    accent: "bg-accent text-accent-foreground hover:bg-accent/90 shadow-md shadow-accent/20",
    outline: "border-2 border-primary/20 bg-transparent hover:bg-primary/5 text-primary",
    ghost: "hover:bg-accent/10 hover:text-primary text-muted-foreground",
    destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-sm"
  };

  const sizes = {
    sm: "h-9 px-4 text-xs",
    default: "h-11 px-6",
    lg: "h-14 px-8 text-base",
    icon: "h-11 w-11"
  };

  return (
    <button className={cn(baseStyles, variants[variant], sizes[size], className)} disabled={isLoading || props.disabled} {...props}>
      {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
}

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("rounded-2xl border border-border/50 bg-card text-card-foreground shadow-sm overflow-hidden", className)} {...props} />
  );
}

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "flex h-12 w-full rounded-xl border-2 border-border/60 bg-background px-4 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:border-primary focus-visible:ring-4 focus-visible:ring-primary/10 disabled:cursor-not-allowed disabled:opacity-50 transition-all",
        className
      )}
      {...props}
    />
  );
}

export function Textarea({ className, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "flex min-h-[120px] w-full rounded-xl border-2 border-border/60 bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:border-primary focus-visible:ring-4 focus-visible:ring-primary/10 disabled:cursor-not-allowed disabled:opacity-50 transition-all resize-y",
        className
      )}
      {...props}
    />
  );
}

export function Badge({ className, variant = 'default', children, ...props }: React.HTMLAttributes<HTMLDivElement> & { variant?: 'default'|'success'|'warning'|'danger'|'outline' }) {
  const variants = {
    default: "bg-primary/10 text-primary",
    success: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    warning: "bg-accent/20 text-accent-foreground",
    danger: "bg-destructive/10 text-destructive",
    outline: "border border-border text-foreground"
  };
  return (
    <div className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors", variants[variant], className)} {...props}>
      {children}
    </div>
  );
}

export function Label({ className, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={cn("text-sm font-semibold leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-foreground/90", className)} {...props} />;
}
