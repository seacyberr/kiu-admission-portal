import React from 'react';
import { CheckCircle2, Clock, Eye, XCircle, AlertCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: 'pending' | 'applied' | 'reviewed' | 'interviewed' | 'placed' | 'rejected' | 'approved' | 'in_progress';
  variant?: 'default' | 'compact';
  className?: string;
}

export function StatusBadge({ status, variant = 'default', className = '' }: StatusBadgeProps) {
  const statusConfig = {
    pending: {
      label: 'Pending',
      color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      icon: Clock,
      darkColor: 'dark:bg-yellow-900 dark:text-yellow-200 dark:border-yellow-700',
    },
    applied: {
      label: 'Applied',
      color: 'bg-blue-100 text-blue-800 border-blue-300',
      icon: Clock,
      darkColor: 'dark:bg-blue-900 dark:text-blue-200 dark:border-blue-700',
    },
    reviewed: {
      label: 'Reviewed',
      color: 'bg-purple-100 text-purple-800 border-purple-300',
      icon: Eye,
      darkColor: 'dark:bg-purple-900 dark:text-purple-200 dark:border-purple-700',
    },
    interviewed: {
      label: 'Interviewed',
      color: 'bg-indigo-100 text-indigo-800 border-indigo-300',
      icon: AlertCircle,
      darkColor: 'dark:bg-indigo-900 dark:text-indigo-200 dark:border-indigo-700',
    },
    placed: {
      label: 'Placed',
      color: 'bg-green-100 text-green-800 border-green-300',
      icon: CheckCircle2,
      darkColor: 'dark:bg-green-900 dark:text-green-200 dark:border-green-700',
    },
    rejected: {
      label: 'Rejected',
      color: 'bg-red-100 text-red-800 border-red-300',
      icon: XCircle,
      darkColor: 'dark:bg-red-900 dark:text-red-200 dark:border-red-700',
    },
    approved: {
      label: 'Approved',
      color: 'bg-green-100 text-green-800 border-green-300',
      icon: CheckCircle2,
      darkColor: 'dark:bg-green-900 dark:text-green-200 dark:border-green-700',
    },
    in_progress: {
      label: 'In Progress',
      color: 'bg-cyan-100 text-cyan-800 border-cyan-300',
      icon: Clock,
      darkColor: 'dark:bg-cyan-900 dark:text-cyan-200 dark:border-cyan-700',
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  if (variant === 'compact') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${config.color} ${config.darkColor} ${className}`}
      >
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  }

  return (
    <div
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold border ${config.color} ${config.darkColor} ${className}`}
    >
      <Icon className="w-4 h-4" />
      {config.label}
    </div>
  );
}
