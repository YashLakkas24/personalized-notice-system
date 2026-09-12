const API_BASE = "http://127.0.0.1:8000";

export async function getStudentNotifications(studentId) {
  const response = await fetch(
    `${API_BASE}/api/student/${studentId}/notifications`,
  );

  if (!response.ok) {
    throw new Error("Failed to fetch notifications");
  }

  return response.json();
}
