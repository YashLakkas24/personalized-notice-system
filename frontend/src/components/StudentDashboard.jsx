import { useEffect, useState } from "react";
import {
  getAllNotices,
  getStudentNotifications,
  markNotificationRead,
} from "../api/notifications";

export default function StudentDashboard() {
  const studentId = "student_1";

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [activeTab, setActiveTab] = useState("relevant");
  const [relevantNotices, setRelevantNotices] = useState([]);
  const [allNotices, setAllNotices] = useState([]);

  async function loadNotices() {
    try {
      setLoading(true);
      setError("");

      const [relevant, all] = await Promise.all([
        getStudentNotifications(studentId),
        getAllNotices(),
      ]);

      const priority = {
        CRITICAL: 4,
        HIGH: 3,
        NORMAL: 2,
        EXPIRED: 1,
      };

      const sortedRelevant = (relevant.notifications || []).sort(
        (a, b) => (priority[b.priority] || 0) - (priority[a.priority] || 0),
      );

      setRelevantNotices(sortedRelevant);
      setAllNotices(all.notices || []);
    } catch (err) {
      console.error(err);
      setError("Unable to load your notices.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadNotices();
  }, []);

  async function handleNotificationOpen(notification) {
    if (notification.status === "READ") {
      return;
    }

    try {
      await markNotificationRead(studentId, notification.notification_id);

      setRelevantNotices((current) =>
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

        <button onClick={loadNotices}>Retry</button>
      </div>
    );
  }

  const displayedCount =
    activeTab === "relevant" ? relevantNotices.length : allNotices.length;

  return (
    <div className="student-dashboard">
      {/* TABS */}
      <div className="notice-tabs">
        <button
          onClick={() => setActiveTab("relevant")}
          className={activeTab === "relevant" ? "active" : ""}
        >
          Relevant to You
        </button>

        <button
          onClick={() => setActiveTab("all")}
          className={activeTab === "all" ? "active" : ""}
        >
          All Notices
        </button>
      </div>

      {/* HEADER */}
      <div className="dashboard-header">
        <div>
          <h1>
            {activeTab === "relevant" ? "Relevant Notices" : "All Notices"}
          </h1>

          <p>
            {activeTab === "relevant"
              ? "Important information selected specifically for you."
              : "All notices published by the administration."}
          </p>
        </div>

        <div>
          <strong>{displayedCount}</strong>{" "}
          {activeTab === "relevant" ? "relevant notices" : "total notices"}
        </div>
      </div>

      {/* ========================= */}
      {/* RELEVANT NOTICES */}
      {/* ========================= */}

      {activeTab === "relevant" &&
        (relevantNotices.length === 0 ? (
          <div className="empty-state">
            <h2>No relevant notices</h2>

            <p>
              You're all caught up. We'll surface something when there's
              something relevant to you.
            </p>
          </div>
        ) : (
          <div className="notification-list">
            {relevantNotices.map((notification) => (
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
        ))}

      {/* ========================= */}
      {/* ALL NOTICES */}
      {/* ========================= */}

      {activeTab === "all" &&
        (allNotices.length === 0 ? (
          <div className="empty-state">
            <h2>No notices available</h2>

            <p>There are currently no notices.</p>
          </div>
        ) : (
          <div className="notification-list">
            {allNotices.map((notice) => (
              <div key={notice.id} className="notification-card">
                <div className="notification-top">
                  <span>{notice.category}</span>

                  {notice.deadline && <span>Deadline: {notice.deadline}</span>}
                </div>

                <h2>{notice.title}</h2>

                <p>{notice.summary}</p>

                {notice.required_action && (
                  <div className="why-section">
                    <strong>Required Action</strong>

                    <p>{notice.required_action}</p>
                  </div>
                )}

                {notice.registration_link && (
                  <div className="notification-actions">
                    <a
                      href={notice.registration_link}
                      target="_blank"
                      rel="noreferrer"
                    >
                      View / Register →
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}
