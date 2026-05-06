import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import { Button } from './ui/shared';
import { motion, AnimatePresence } from 'framer-motion';

interface Notification {
  id: number;
  message: string;
  isRead: boolean;
  createdAt: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  link?: string;
}

interface NotificationsDropdownProps {
  notifications: Notification[];
  unreadCount: number;
  onMarkAsRead?: (id: number) => void;
  onMarkAllAsRead?: () => void;
}

export function NotificationsDropdown({
  notifications = [],
  unreadCount = 0,
  onMarkAsRead,
  onMarkAllAsRead,
}: NotificationsDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleNotificationClick = (notif: Notification) => {
    if (!notif.isRead && onMarkAsRead) {
      onMarkAsRead(notif.id);
    }
    if (notif.link) {
      window.location.href = notif.link;
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-muted-foreground hover:text-foreground transition-colors"
        title="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 w-5 h-5 bg-destructive text-white text-xs rounded-full flex items-center justify-center font-semibold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />
            {/* Dropdown */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute right-0 mt-2 w-80 bg-background border border-border rounded-lg shadow-2xl z-50 max-h-96 overflow-y-auto"
            >
              {/* Header */}
              <div className="sticky top-0 bg-background border-b border-border p-4 flex justify-between items-center">
                <h3 className="font-semibold text-sm">Notifications</h3>
                {unreadCount > 0 && onMarkAllAsRead && (
                  <button
                    onClick={onMarkAllAsRead}
                    className="text-xs text-primary hover:underline"
                  >
                    Mark all as read
                  </button>
                )}
              </div>

              {/* Notifications List */}
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground text-sm">
                  No notifications yet
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {notifications.slice(0, 6).map((notif) => (
                    <motion.div
                      key={notif.id}
                      whileHover={{ backgroundColor: 'rgba(0,0,0,0.02)' }}
                      onClick={() => handleNotificationClick(notif)}
                      className={`p-4 cursor-pointer transition-colors ${
                        !notif.isRead ? 'bg-primary/5' : ''
                      } ${notif.link ? 'hover:bg-primary/10' : ''}`}
                    >
                      <div className="flex items-start gap-2">
                        {notif.type && (
                          <div
                            className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                              notif.type === 'success'
                                ? 'bg-green-500'
                                : notif.type === 'warning'
                                  ? 'bg-yellow-500'
                                  : notif.type === 'error'
                                    ? 'bg-red-500'
                                    : 'bg-blue-500'
                            }`}
                          />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm ${notif.isRead ? 'text-muted-foreground' : 'font-semibold text-foreground'}`}>
                            {notif.message}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {formatTime(notif.createdAt)}
                          </p>
                        </div>
                        {!notif.isRead && (
                          <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0 mt-1.5" />
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* Footer */}
              {notifications.length > 0 && (
                <div className="border-t border-border p-3 text-center">
                  <Button
                    variant="ghost"
                    className="text-xs w-full justify-center"
                    onClick={() => {
                      setIsOpen(false);
                      // Navigate to notifications page
                      window.location.href = '/notifications';
                    }}
                  >
                    View all notifications
                  </Button>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
