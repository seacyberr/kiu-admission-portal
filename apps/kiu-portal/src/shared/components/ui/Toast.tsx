/**
 * Toast Component - Notification system
 */
import React, { createContext, useContext, useState, useCallback } from 'react';

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success';
}

interface ToastContextType {
  toasts: Toast[];
  toast: (toast: Omit<Toast, 'id'>) => void;
  dismiss: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback(({ title, description, variant = 'default' }: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, title, description, variant }]);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, toast, dismiss }}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`rounded-lg p-4 shadow-lg min-w-[300px] animate-in slide-in-from-right ${
              t.variant === 'destructive'
                ? 'bg-red-50 border border-red-200 text-red-800'
                : t.variant === 'success'
                  ? 'bg-green-50 border border-green-200 text-green-800'
                  : 'bg-white border border-slate-200 text-slate-800'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-1">
                <p className="font-medium text-sm">{t.title}</p>
                {t.description && (
                  <p className="text-xs mt-1 opacity-80">{t.description}</p>
                )}
              </div>
              <button
                onClick={() => dismiss(t.id)}
                className="text-sm opacity-60 hover:opacity-100"
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextType => {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
