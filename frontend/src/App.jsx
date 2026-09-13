import { useEffect, useState } from "react";

import AdminDashboard from "./pages/AdminDashboard";
import StudentDashboard from "./pages/StudentDashboard";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [students, setStudents] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/students`)
      .then((res) => res.json())
      .then((data) => setStudents(data))
      .catch((err) => console.error("Failed to load students:", err));
  }, []);

  const path = window.location.pathname;

  // -----------------------------
  // ADMIN
  // -----------------------------
  if (path === "/admin") {
    return <AdminDashboard />;
  }

  // -----------------------------
  // STUDENT
  // -----------------------------
  if (path.startsWith("/student/")) {
    const studentId = path.split("/student/")[1];

    return <StudentDashboard studentId={studentId} />;
  }

  // -----------------------------
  // HOME
  // -----------------------------
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-2xl shadow-sm border text-center">
        <h1 className="text-2xl font-bold mb-2">🤖 CampusNotice.AI</h1>

        <p className="text-gray-500 mb-6">
          Personalized College Notice Intelligence
        </p>

        <div className="flex gap-3 justify-center">
          <a
            href="/admin"
            className="px-5 py-2.5 bg-blue-600 text-white rounded-lg"
          >
            Admin Portal
          </a>

          {students.length > 0 && (
            <a
              href={`/student/${students[0].id}`}
              className="px-5 py-2.5 bg-gray-900 text-white rounded-lg"
            >
              Student Portal
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
