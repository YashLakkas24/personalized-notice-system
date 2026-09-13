const API_BASE = "http://127.0.0.1:8000";

export async function getAllNotices() {
  const response = await fetch(`{API_BASE}/api/notices`);

  if (!response.ok) {
    throw new Error("Failed to fetch notices");
  }
  return response.json();
}

export async function getStudentNotifications(studentId) {
  const response = await fetch(
    `${API_BASE}/api/student/${studentId}/notifications`,
  );

  if (!response.ok) {
    throw new Error("Failed to fetch notifications");
  }

  return response.json();
}

export async function markNotificationRead(studentId, notificationId) {
  const response = await fetch(
    `${API_BASE}/api/student/${studentId}/notifications/${notificationId}/read`,
    {
      method: "PATCH",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to mark notification as read");
  }

  return response.json();
}

export async function uploadNotice(file) {
  const formData = new FormData();

  formData.append("file", file);

  let endpoint;

  if (file.type === "application/pdf") {
    endpoint = "/api/admin/notice/pdf";
  } else {
    endpoint = "/api/admin/notice/image";
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();

    throw new Error(error.detail || "Upload failed");
  }

  return response.json();
}

export async function uploadNoticeBatch(files) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_BASE}/api/admin/notices/batch`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Batch upload failed");
  }

  return response.json();
}
