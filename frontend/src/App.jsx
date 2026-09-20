import "./App.css";

import StudentLogin from "./pages/StudentLogin";
import AdminDashboard from "./pages/AdminDashboard";
import StudentDashboard from "./pages/StudentDashboard";

export default function App() {
  const path = window.location.pathname;

  // -----------------------------
  // ADMIN PORTAL
  // -----------------------------
  if (path === "/admin") {
    return <AdminDashboard />;
  }

  // -----------------------------
  // STUDENT PORTAL
  // -----------------------------

  if (path === "/student-login") {
    return <StudentLogin />;
  }

  if (path.startsWith("/student/")) {
    const studentId = path.split("/student/")[1];

    let auth = null;

    try {
      auth = JSON.parse(sessionStorage.getItem("studentAuth"));
    } catch {
      auth = null;
    }

    if (!auth || auth.studentId !== studentId || !auth.token) {
      window.location.replace("/student-login");
      return null;
    }

    return <StudentDashboard studentId={studentId} />;
  }

  return (
    <main className="portal-page">
      <div className="portal-container">
        <div className="portal-brand">
          <div className="portal-logo">🤖</div>

          <h1>
            CampusNotice<span>.AI</span>
          </h1>

          <p>AI-powered personalized college notice intelligence</p>
        </div>

        <div className="portal-options">
          {/* ADMIN */}
          <a href="/admin" className="portal-card">
            <div className="portal-card-icon">🏛️</div>

            <div>
              <h2>Admin Portal</h2>

              <p>Upload and process college notices using AI.</p>
            </div>

            <span className="portal-arrow"></span>
          </a>

          {/* STUDENT */}
          <a href="/student-login" className="portal-card student-card">
            <div className="portal-card-icon">🎓</div>

            <div>
              <h2>Student Portal</h2>

              <p>Login to view your personalized notices.</p>
            </div>
          </a>
        </div>

        <div className="portal-footer">
          <span>AI understands.</span>
          <span>Students discover.</span>
          <span>Nothing gets missed.</span>
        </div>
      </div>
    </main>
  );
}
