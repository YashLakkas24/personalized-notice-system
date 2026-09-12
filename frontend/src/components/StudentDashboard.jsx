import { useEffect, useState } from "react";
import {
  getStudentNotifications,
  markNotificationRead,
} from "../api/notifications";

export default function StudentDashboard() {
  const studentId = "student_1";

  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadNotifications();
  }, []);

  async function loadNotifications() {
    try {
      setLoading(true);

      const data = await getStudentNotifications(studentId);

      const priority = {
        CRITICAL: 4,
        HIGH: 3,
        NORMAL: 2,
        EXPIRED: 1,
      };

      const sorted = (data.notifications || []).sort(
        (a, b) => (priority[b.priority] || 0) - (priority[a.priority] || 0),
      );

      setNotifications(sorted);
    } catch (err) {
      console.error(err);
      setError("Unable to load your notices.");
    } finally {
      setLoading(false);
    }
  }

  async function handleNotificationOpen(notification) {
    if (notification.status === "READ") {
      return;
    }

    try {
      await markNotificationRead(studentId, notification.notification_id);

      setNotifications((current) =>
        current.map((item) =>
          item.notification_id === notification.notification_id
            ? {
                ...item,
                status: "READ",
              }
            : item,
        ),
      );
    } catch (err) {
      console.error(err);
    }
  }

  function getPriorityClass(priority) {
    switch (priority) {
      case "CRITICAL":
        return "critical";

      case "HIGH":
        return "high";

      default:
        return "normal";
    }
  }

  if (loading) {
    return (
      <div>
        <h1>My Notices</h1>
        <p>Loading your personalized notices...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1>My Notices</h1>
        <p>{error}</p>
        <button onClick={loadNotifications}>Retry</button>
      </div>
    );
  }

  return (
    <div className="student-dashboard">
      <div className="dashboard-header">
        <div>
          <h1>My Notices</h1>
          <p>Important information selected specifically for you.</p>
        </div>

        <div>
          <strong>{notifications.length}</strong> relevant notices
        </div>
      </div>

      {notifications.length === 0 ? (
        <div className="empty-state">
          <h2>No relevant notices</h2>
          <p>
            You're all caught up. We'll surface something when there's something
            relevant to you.
          </p>
        </div>
      ) : (
        <div className="notification-list">
          {notifications.map((notification) => (
            <div
              key={notification.notification_id}
              className={`notification-card ${getPriorityClass(
                notification.priority,
              )} ${notification.status === "UNREAD" ? "unread" : ""}`}
              onClick={() => handleNotificationOpen(notification)}
            >
              <div className="notification-top">
                <span>
                  {notification.priority === "CRITICAL"
                    ? "🔴"
                    : notification.priority === "HIGH"
                      ? "🟠"
                      : "🔵"}{" "}
                  {notification.priority}
                </span>

                {notification.days_left !== null &&
                  notification.days_left !== undefined && (
                    <span>
                      {notification.days_left === 0
                        ? "Due today"
                        : notification.days_left === 1
                          ? "1 day left"
                          : `${notification.days_left} days left`}
                    </span>
                  )}
              </div>

              <h2>{notification.title}</h2>

              <p>{notification.summary}</p>

              <div className="why-section">
                <strong>Why you're seeing this</strong>

                <p>{notification.reason}</p>
              </div>

              <div className="notification-actions">
                {notification.registration_link && (
                  <a
                    href={notification.registration_link}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleNotificationOpen(notification);
                    }}
                  >
                    Take Action →
                  </a>
                )}

                {notification.status === "UNREAD" && <span>● Unread</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
