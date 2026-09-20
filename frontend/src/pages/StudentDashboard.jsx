import { useEffect, useState } from "react";
import {
  getAllNotices,
  getStudentNotifications,
  markNotificationRead,
} from "../api/notifications";
import "./StudentDashboard.css";
import { getStudentProfile, updateStudentPreferences } from "../api/student";

export default function StudentDashboard({ studentId }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [activeTab, setActiveTab] = useState("relevant");
  const [relevantNotices, setRelevantNotices] = useState([]);
  const [allNotices, setAllNotices] = useState([]);

  const [preferences, setPreferences] = useState("");
  const [profile, setProfile] = useState(null);
  const [savingPreferences, setSavingPreferences] = useState(false);
  const [preferencesMessage, setPreferencesMessage] = useState("");

  const unreadCount = relevantNotices.filter(
    (notice) => notice.status === "UNREAD",
  ).length;

  const urgentCount = relevantNotices.filter(
    (notice) => notice.priority === "CRITICAL" || notice.priority === "HIGH",
  ).length;

  async function loadProfile() {
    try {
      const profileData = await getStudentProfile(studentId);

      setProfile(profileData);
      setPreferences(profileData.preferences || "");
    } catch (err) {
      console.error(err);
    }
  }

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
    (async () => {
      await Promise.all([loadNotices(), loadProfile()]);
    })();
  }, [studentId]);

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

  async function handleSavePreferences() {
    try {
      setSavingPreferences(true);
      setPreferencesMessage("");

      await updateStudentPreferences(studentId, preferences);

      setPreferencesMessage("✓ Preferences saved. Your feed has been updated.");

      await loadNotices();

      setActiveTab("relevant");
    } catch (err) {
      setPreferencesMessage(err.message);
    } finally {
      setSavingPreferences(false);
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

  function formatYear(year) {
    if (year === 1) return "1st Year";
    if (year === 2) return "2nd Year";
    if (year === 3) return "3rd Year";
    if (year === 4) return "4th Year";

    return `${year}th Year`;
  }

  function formatPostedDate(date) {
    if (!date) return "Date unavailable";

    return new Date(date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
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
    activeTab === "relevant"
      ? relevantNotices.length
      : activeTab === "all"
        ? allNotices.length
        : null;

  return (
    <div className="student-dashboard">
      {/* TOP NAVIGATION */}
      <div className="student-topbar">
        <div className="student-brand">
          🤖 CampusNotice<span>.AI</span>
        </div>

        <a href="/" className="student-home-link">
          ← Home
        </a>
      </div>

      {/* TABS */}
      <div className="notice-tabs">
        <button
          className={activeTab === "relevant" ? "active" : ""}
          onClick={() => setActiveTab("relevant")}
        >
          🎯 Relevant to You
          <span>{relevantNotices.length}</span>
        </button>

        <button
          className={activeTab === "all" ? "active" : ""}
          onClick={() => setActiveTab("all")}
        >
          📋 All Notices
          <span>{allNotices.length}</span>
        </button>

        <button
          className={activeTab === "profile" ? "active" : ""}
          onClick={() => setActiveTab("profile")}
        >
          👤 My Profile
        </button>

        <button
          className={activeTab === "preferences" ? "active" : ""}
          onClick={() => setActiveTab("preferences")}
        >
          ⚙️ My Preferences
        </button>
      </div>

      {/* HEADER */}
      <div className="dashboard-header">
        <div>
          <h1>
            {activeTab === "relevant"
              ? "Relevant Notices"
              : activeTab === "all"
                ? "All Notices"
                : activeTab === "profile"
                  ? "My Profile"
                  : "My Preferences"}
          </h1>

          <p>
            {activeTab === "relevant"
              ? "Important information selected specifically for you."
              : activeTab === "all"
                ? "All notices published by the administration."
                : activeTab === "profile"
                  ? "Your academic information used by CampusNotice.AI."
                  : "Tell us what you're looking for so we can personalize your notices."}
          </p>
        </div>

        {displayedCount !== null && (
          <div>
            <strong>{displayedCount}</strong>{" "}
            {activeTab === "relevant" ? "relevant notices" : "total notices"}
          </div>
        )}
      </div>
      {(activeTab === "relevant" || activeTab === "all") && (
        <div className="notice-stats">
          <div className="stat-card">
            <span className="stat-icon">🎯</span>
            <div>
              <strong>{relevantNotices.length}</strong>
              <span>Relevant</span>
            </div>
          </div>

          <div className="stat-card">
            <span className="stat-icon">🔴</span>
            <div>
              <strong>{urgentCount}</strong>
              <span>Urgent</span>
            </div>
          </div>

          <div className="stat-card">
            <span className="stat-icon">🔔</span>
            <div>
              <strong>{unreadCount}</strong>
              <span>Unread</span>
            </div>
          </div>

          <div className="stat-card">
            <span className="stat-icon">📋</span>
            <div>
              <strong>{allNotices.length}</strong>
              <span>Total Notices</span>
            </div>
          </div>
        </div>
      )}

      {activeTab === "profile" && profile && (
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-icon">👤</div>

            <div>
              <h2>My Profile</h2>
              <p>Your academic information used by CampusNotice.AI.</p>
            </div>
          </div>

          <div className="profile-grid">
            <div className="profile-field">
              <span>STUDENT ID</span>
              <strong>{profile.id}</strong>
            </div>

            <div className="profile-field">
              <span>FULL NAME</span>
              <strong>{profile.name}</strong>
            </div>

            <div className="profile-field">
              <span>ACADEMIC YEAR</span>
              <strong>{formatYear(profile.year)}</strong>
            </div>

            <div className="profile-field">
              <span>BRANCH</span>
              <strong>{profile.branch}</strong>
            </div>
          </div>

          <div className="profile-info">
            🎓 These academic details are used when determining eligibility for
            notices.
          </div>
        </div>
      )}

      {activeTab === "preferences" && (
        <div className="preferences-card">
          <div className="preferences-header">
            <div className="preferences-icon">⚙️</div>

            <div>
              <h2>My Preferences</h2>
              <p>
                Tell CampusNotice.AI what you're looking for. Your preferences
                help AI personalize your notice feed.
              </p>
            </div>
          </div>

          <div className="preferences-input-section">
            <label htmlFor="preferences">
              What notices are relevant to you?
            </label>

            <textarea
              id="preferences"
              value={preferences}
              onChange={(e) => setPreferences(e.target.value)}
              placeholder="Example: I am interested in football competitions, tournaments, team trials and football training programs."
              rows={6}
            />

            <div className="preferences-hint">
              💡 Be specific. Mention topics, activities, competitions,
              opportunities or events you want to see.
            </div>
          </div>

          <div className="preferences-footer">
            <span>🤖 AI will use this description to match notices.</span>

            <button
              onClick={handleSavePreferences}
              disabled={savingPreferences}
            >
              {savingPreferences ? "Updating Feed..." : "Save Preferences →"}
            </button>
          </div>

          {preferencesMessage && (
            <div className="preferences-message">{preferencesMessage}</div>
          )}
        </div>
      )}

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
                  <div className="notification-top-left">
                    <span
                      className={`priority-badge ${getPriorityClass(
                        notification.priority,
                      )}`}
                    >
                      {notification.priority === "CRITICAL"
                        ? "🔴 Critical"
                        : notification.priority === "HIGH"
                          ? "🟠 High Priority"
                          : "🔵 Normal"}
                    </span>

                    <span className="posted-date">
                      Posted {formatPostedDate(notification.created_at)}
                    </span>
                  </div>

                  <span className="category-badge">
                    {notification.category}
                  </span>
                </div>
                <h2>{notification.title}</h2>

                <p>{notification.summary}</p>
                <div className="notice-meta">
                  {notification.deadline && (
                    <span>📅 Deadline: {notification.deadline}</span>
                  )}

                  {notification.days_left !== null &&
                    notification.days_left !== undefined && (
                      <span>
                        ⏳{" "}
                        {notification.days_left === 0
                          ? "Due today"
                          : `${notification.days_left} days left`}
                      </span>
                    )}
                </div>
                <div className="why-section">
                  <strong>🤖 Why this was recommended</strong>
                  <p>{notification.reason}</p>
                </div>

                {notification.pdf_url && (
                  <a
                    href={`${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"}${notification.pdf_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="view-notice-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleNotificationOpen(notification);
                    }}
                  >
                    📄 View Original Notice
                  </a>
                )}

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
                  <div className="notification-top-left">
                    <span className="category-badge">{notice.category}</span>

                    <span className="posted-date">
                      Posted {formatPostedDate(notice.created_at)}
                    </span>
                  </div>

                  {notice.deadline && (
                    <span className="posted-date">
                      Deadline: {notice.deadline}
                    </span>
                  )}
                </div>

                <h2>{notice.title}</h2>

                <p>{notice.summary}</p>

                {notice.required_action && (
                  <div className="why-section">
                    <strong>Required Action</strong>

                    <p>{notice.required_action}</p>
                  </div>
                )}

                {notice.pdf_url && (
                  <a
                    href={`${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"}${notice.pdf_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="view-notice-btn"
                  >
                    📄 View Original Notice
                  </a>
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
