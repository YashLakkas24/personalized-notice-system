import { useState } from "react";
import "./StudentLogin.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function StudentLogin() {
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/student/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          student_id: studentId.trim(),
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const message =
          typeof data.detail === "string" ? data.detail : "Login failed";

        throw new Error(message);
      }

      window.location.href = `/student/${data.student.id}`;
    } catch (err) {
      console.error("LOGIN ERROR:", err);
      setError(err.message || "Unable to connect to server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="student-login-page">
      <div className="student-login-shell">
        <a href="/" className="login-brand">
          🤖 CampusNotice<span>.AI</span>
        </a>

        <form className="student-login-card" onSubmit={handleLogin}>
          <div className="login-icon">🎓</div>

          <h1>Student Login</h1>

          <p>Sign in to access notices personalized for you.</p>

          <label htmlFor="student-id" className="login-field-label">
            <span>Student ID</span>
            <strong>Demo: student_1-student_4</strong>
          </label>

          <input
            id="student-id"
            type="text"
            placeholder="e.g. student_1"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            required
          />

          <label htmlFor="password" className="login-field-label">
            <span>Password</span>
            <strong>Demo: student123</strong>
          </label>

          <input
            id="password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <div className="login-error">⚠️ {error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In →"}
          </button>

          <a href="/" className="login-back">
            ← Back to portal selection
          </a>
        </form>
      </div>
    </main>
  );
}
