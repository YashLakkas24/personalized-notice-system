const API_BASE = "http://127.0.0.1:8000";

export async function getStudentProfile(studentId) {
  const response = await fetch(`${API_BASE}/api/student/${studentId}/profile`);

  if (!response.ok) {
    throw new Error("Failed to load student profile");
  }

  return response.json();
}

export async function updateStudentPreferences(studentId, preferences) {
  const response = await fetch(`${API_BASE}/api/student/${studentId}/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      preferences,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to save preferences");
  }

  return data;
}
