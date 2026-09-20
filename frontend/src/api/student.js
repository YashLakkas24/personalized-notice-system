const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function getStudentToken() {
  const auth = sessionStorage.getItem("studentAuth");

  if (!auth) return null;

  try {
    return JSON.parse(auth).token;
  } catch {
    return null;
  }
}

function studentHeaders(extra = {}) {
  const token = getStudentToken();

  return {
    ...extra,
    ...(token ? { "X-Student-Token": token } : {}),
  };
}

export async function getStudentProfile(studentId) {
  const response = await fetch(`${API_BASE}/api/student/${studentId}/profile`, {
    headers: studentHeaders(),
  });

  if (!response.ok) {
    throw new Error("Failed to load student profile");
  }

  return response.json();
}

export async function getAllStudents() {
  const response = await fetch(`${API_BASE}/api/students`);

  if (!response.ok) {
    throw new Error("Failed to load students");
  }

  return response.json();
}

export async function updateStudentPreferences(studentId, preferences) {
  const response = await fetch(`${API_BASE}/api/student/${studentId}/profile`, {
    method: "PUT",
    headers: studentHeaders({
      "Content-Type": "application/json",
    }),
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
