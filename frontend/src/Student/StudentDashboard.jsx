import { useEffect, useState } from "react";
import { getStudentNotifications } from "../api/notifications";

export default function StudentDashboard() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const studentId = "student_1";

  useEffect(() => {
    async function loadNotifications() {
      try {
        const data = await getStudentNotifications(studentId);
        setNotifications(data.notifications || []);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }

    loadNotifications();
  }, []);

  if (loading) {
    return <div>Loading your notices...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h1>My Notices</h1>

      {notifications.length === 0 ? (
        <p>No relevant notices right now.</p>
      ) : (
        notifications.map((notification) => (
          <div key={notification.notification_id}>
            <h2>{notification.title}</h2>

            <p>{notification.summary}</p>

            <p>Priority: {notification.priority}</p>

            <p>
              {notification.days_left !== null &&
                `${notification.days_left} days remaining`}
            </p>

            <p>Why you're seeing this: {notification.reason}</p>

            {notification.registration_link && (
              <a
                href={notification.registration_link}
                target="_blank"
                rel="noreferrer"
              >
                Register / Take Action
              </a>
            )}
          </div>
        ))
      )}
    </div>
  );
}
