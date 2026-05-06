import { useEffect, useMemo, useState } from "react";
import { Card, Button, Badge } from "@/components/ui/shared";
import { Bell, CheckCheck, Clock } from "lucide-react";

type NotificationItem = {
  id: number;
  title: string;
  message: string;
  notificationType?: string;
  link?: string | null;
  isRead: boolean;
  createdAt?: string;
};

export default function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [markingAll, setMarkingAll] = useState(false);

  const unreadCount = useMemo(() => items.filter((n) => !n.isRead).length, [items]);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/notifications?perPage=50", {
        credentials: "include",
      });
      const json = await response.json();
      const notifications = json?.data?.notifications || json?.notifications || [];
      setItems(notifications);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const markRead = async (id: number) => {
    await fetch(`/api/notifications/${id}/read`, {
      method: "PATCH",
      credentials: "include",
    });
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, isRead: true } : n)));
  };

  const markAllRead = async () => {
    setMarkingAll(true);
    try {
      await fetch("/api/notifications/read-all", {
        method: "PATCH",
        credentials: "include",
      });
      setItems((prev) => prev.map((n) => ({ ...n, isRead: true })));
    } finally {
      setMarkingAll(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center gap-3">
        <Clock className="w-6 h-6 animate-spin text-primary" />
        <span className="text-muted-foreground">Loading notifications...</span>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-display font-bold text-primary">Notifications</h1>
          <p className="text-muted-foreground">Application, opportunity, and status updates.</p>
        </div>
        <Button onClick={markAllRead} disabled={markingAll || unreadCount === 0} className="gap-2">
          <CheckCheck className="w-4 h-4" />
          Mark all as read
        </Button>
      </div>

      <div className="mb-4">
        <Badge variant={unreadCount > 0 ? "warning" : "default"}>
          {unreadCount} unread
        </Badge>
      </div>

      <div className="space-y-3">
        {items.length === 0 ? (
          <Card className="p-8 text-center">
            <Bell className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">You do not have notifications yet.</p>
          </Card>
        ) : (
          items.map((n) => (
            <Card key={n.id} className={`p-5 ${n.isRead ? "opacity-80" : "border-primary/40 bg-primary/5"}`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold">{n.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1">{n.message}</p>
                </div>
                {!n.isRead && (
                  <Button variant="outline" size="sm" onClick={() => markRead(n.id)}>
                    Mark read
                  </Button>
                )}
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
