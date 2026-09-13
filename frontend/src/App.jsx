import { useEffect, useState } from "react";
import "./App.css";

import AdminDashboard from "./pages/AdminDashboard";
import StudentDashboard from "./pages/StudentDashboard";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [students, setStudents] = useState([]);
  const [studentId, setStudentId] = useState("");
  const [loadingStudents, setLoadingStudents] = useState(true);

  useEffect(() => {
    async function loadStudents() {
      try {
        const response = await fetch(`${API_BASE}/api/students`);

        if (!response.ok) {
          throw new Error("Failed to load students");
        }

        const data = await response.json();

        setStudents(data);

        if (data.length > 0) {
          setStudentId(data[0].id);
        }
      } catch (error) {
        console.error("Failed to load students:", error);
      } finally {
        setLoadingStudents(false);
      }
    }

    loadStudents();
  }, []);

  const path = window.location.pathname;

  if (path === "/admin") {
    return <AdminDashboard />;
  }

  if (path.startsWith("/student/")) {
    const currentStudentId = path.split("/student/")[1];

    return <StudentDashboard studentId={currentStudentId} />;
  }

  function openStudentPortal() {
    if (!studentId) return;

    window.location.href = `/student/${studentId}`;
  }

  return (
    <main className="landing">
      {/* NAVBAR */}
      <nav className="landing-nav">
        <a href="/" className="brand">
          <span className="brand-logo">🤖</span>

          <span>
            CampusNotice<span className="brand-accent">.AI</span>
          </span>
        </a>

        <div className="nav-links">
          <a href="/admin">Admin Portal</a>

          {students.length > 0 && (
            <button onClick={openStudentPortal}>Student Portal</button>
          )}
        </div>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="hero-badge">
          <span>✦</span>
          AI-powered campus intelligence
        </div>

        <h1>
          College notices,
          <br />
          <span>finally personalized.</span>
        </h1>

        <p className="hero-copy">
          CampusNotice.AI understands raw college notices and delivers the
          information that actually matters to each student.
        </p>

        <div className="hero-actions">
          <a href="/admin" className="primary-action">
            🏛️
            <span>Open Admin Portal</span>
            <span>→</span>
          </a>

          {students.length > 0 && (
            <div className="student-launcher">
              <select
                value={studentId}
                onChange={(event) => setStudentId(event.target.value)}
                aria-label="Select student"
                disabled={loadingStudents}
              >
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.name} · Year {student.year}
                  </option>
                ))}
              </select>

              <button onClick={openStudentPortal}>View My Notices →</button>
            </div>
          )}
        </div>

        {/* PIPELINE */}
        <div className="hero-flow">
          <div className="flow-step">
            <strong>01</strong>
            <span>Dump notices</span>
          </div>

          <div className="flow-line" />

          <div className="flow-step">
            <strong>02</strong>
            <span>AI understands</span>
          </div>

          <div className="flow-line" />

          <div className="flow-step">
            <strong>03</strong>
            <span>Personalized delivery</span>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="feature-section">
        <div className="section-heading">
          <span>WHY CAMPUSNOTICE.AI</span>
          <h2>From information overload to clarity.</h2>
        </div>

        <div className="feature-grid">
          <article className="feature-card">
            <div className="feature-icon">🎯</div>

            <h3>Personalized feed</h3>

            <p>
              Students see notices matched against their interests, branch, year
              and eligibility.
            </p>
          </article>

          <article className="feature-card">
            <div className="feature-icon">🧠</div>

            <h3>AI understands notices</h3>

            <p>
              Raw text, PDFs and images are transformed into structured,
              meaningful information.
            </p>
          </article>

          <article className="feature-card">
            <div className="feature-icon">📋</div>

            <h3>Nothing gets hidden</h3>

            <p>
              Relevant notices are personalized, while the All Notices view
              preserves the complete campus broadcast.
            </p>
          </article>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="landing-footer">
        <span>CampusNotice.AI</span>
        <span>AI-powered college notice intelligence</span>
      </footer>
    </main>
  );
}
