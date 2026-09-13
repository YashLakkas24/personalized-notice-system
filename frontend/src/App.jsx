// filepath: frontend/src/App.jsx
import { useState, useEffect } from "react";
import { markNotificationRead } from "./api/notifications";

export default function App() {
  // Application State
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState("");
  const [feed, setFeed] = useState([]);
  const [noticeText, setNoticeText] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE = "http://127.0.0.1:8000";

  const loadNotifications = async (studentId) => {
    if (!studentId) return;

    try {
      const response = await fetch(
        `${API_BASE}/api/student/${studentId}/notifications`,
      );

      if (!response.ok) {
        throw new Error("Failed to load notifications");
      }

      const data = await response.json();

      setFeed(data.notifications || []);
    } catch (err) {
      console.error("Error loading notifications:", err);
      setFeed([]);
    }
  };
  // Fetch demo students on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/students`)
      .then((res) => res.json())
      .then((data) => {
        setStudents(data);
        if (data.length > 0) setSelectedStudentId(data[0].id);
      })
      .catch((err) => console.error("Error loading student accounts:", err));
  }, []);

  // Fetch personalized feed whenever the active student changes
  useEffect(() => {
    loadNotifications(selectedStudentId);
  }, [selectedStudentId]);
  // Handle Form Submission (Text-based Notice Ingestion)
  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!noticeText.trim()) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append("text", noticeText);

    try {
      const response = await fetch(`${API_BASE}/api/admin/notice/text`, {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        alert("Notice successfully processed and dispatched by Strands Agent!");
        setNoticeText("");
        await loadNotifications(selectedStudentId);
      } else {
        alert("Agent routing error encountered.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to reach server.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Top Banner Navigation */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-blue-600 flex items-center gap-2">
            🤖 CampusNotice.AI
          </h1>
          <p className="text-xs text-gray-500">Powered by Strands Agents SDK</p>
        </div>
        <div className="bg-blue-50 text-blue-700 text-xs font-semibold px-3 py-1.5 rounded-full border border-blue-100">
          Hackathon Showcase Environment
        </div>
      </header>

      {/* Main Split Layout Grid */}
      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: ADMIN CONTROL HUB (4 Cols) */}
        <section className="lg:col-span-5 bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-fit">
          <div className="mb-4">
            <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
              🏛️ Administrative Broadcast Portal
            </h2>
            <p className="text-sm text-gray-500">
              Dump raw unstructured notices or flyers here.
            </p>
          </div>

          <form onSubmit={handleTextSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                Unstructured Notice Input Text
              </label>
              <textarea
                value={noticeText}
                onChange={(e) => setNoticeText(e.target.value)}
                placeholder="e.g., Applications open for Inter-College Cricket Tournament. Students from 2nd–4th year are eligible. Trials on September 5. Mandatory exams for final years start next week..."
                className="w-full h-64 p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !noticeText.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm py-2.5 px-4 rounded-lg shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
            >
              {isLoading ? (
                <>⏳ Strands Agent Orchestrating...</>
              ) : (
                <>⚡ Parse & Dispatch Notice</>
              )}
            </button>
          </form>
        </section>

        {/* RIGHT COLUMN: INTERACTIVE STUDENT FEED PERSPECTIVE (7 Cols) */}
        <section className="lg:col-span-7 space-y-6">
          {/* Identity Matrix Component */}
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-3">
              👤 Select Student Persona Perspective
            </label>
            <div className="grid grid-cols-2 gap-3">
              {students.map((student) => (
                <button
                  key={student.id}
                  onClick={() => setSelectedStudentId(student.id)}
                  className={`p-3 text-left rounded-xl border transition-all ${
                    selectedStudentId === student.id
                      ? "border-blue-600 bg-blue-50/50 ring-1 ring-blue-500"
                      : "border-gray-200 hover:border-gray-300 bg-white"
                  }`}
                >
                  <div className="font-bold text-sm text-gray-800">
                    {student.name}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    Year {student.year} • {student.branch} Engineering
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {student.interests.map((interest, i) => (
                      <span
                        key={i}
                        className="text-[10px] bg-gray-100 border border-gray-200 px-1.5 py-0.5 rounded text-gray-600"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Live Personalized Pipeline Feed Container */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-gray-800 flex items-center justify-between">
              <span>📭 Personalized Intelligence Feed</span>

              <span className="text-xs font-normal text-gray-500">
                Showing {feed.length} matched entries
              </span>
            </h3>

            {feed.length === 0 ? (
              <div className="text-center py-12 text-sm text-gray-500 bg-white rounded-xl border border-dashed border-gray-300 px-6">
                No matching opportunities found for this profile.
              </div>
            ) : (
              <div className="space-y-3">
                {feed.map((item) => (
                  <div
                    key={item.notification_id}
                    onClick={() =>
                      markNotificationRead(
                        selectedStudentId,
                        item.notification_id,
                      )
                    }
                    className={`bg-white p-5 rounded-xl border shadow-sm transition-all relative cursor-pointer ${
                      item.priority === "CRITICAL"
                        ? "border-l-4 border-l-red-500 border-gray-200"
                        : item.priority === "HIGH"
                          ? "border-l-4 border-l-orange-400 border-gray-200"
                          : "border-gray-200"
                    }`}
                  >
                    {/* Priority */}
                    <div className="absolute top-4 right-4 flex items-center gap-2">
                      <span
                        className={`text-[10px] font-bold tracking-wider px-2 py-0.5 rounded border uppercase ${
                          item.priority === "CRITICAL"
                            ? "bg-red-100 text-red-800 border-red-200"
                            : item.priority === "HIGH"
                              ? "bg-orange-100 text-orange-800 border-orange-200"
                              : "bg-blue-100 text-blue-800 border-blue-200"
                        }`}
                      >
                        {item.priority}
                      </span>

                      <span className="text-xs font-mono font-bold bg-gray-50 border border-gray-200 px-1.5 py-0.5 rounded text-gray-700">
                        {Number(item.relevance_score).toFixed(2)}
                      </span>
                    </div>

                    {item.status === "UNREAD" && (
                      <span className="text-[10px] font-bold bg-green-100 text-green-700 px-2 py-0.5 rounded border border-green-200">
                        UNREAD
                      </span>
                    )}

                    {/* Content */}
                    <div className="pr-32">
                      <span className="inline-block text-[11px] font-semibold bg-blue-50 text-blue-700 px-2 py-0.5 rounded mb-1.5">
                        {item.category}
                      </span>

                      <h4 className="font-bold text-gray-900 text-sm leading-snug">
                        {item.title}
                      </h4>

                      <p className="text-xs text-gray-600 mt-1.5 leading-relaxed">
                        {item.summary}
                      </p>
                    </div>

                    {/* Why this notice */}
                    <div className="mt-4 bg-gray-50 border border-gray-100 rounded-lg p-3">
                      <p className="text-[11px] font-bold text-gray-700 mb-1">
                        💡 Why you're seeing this
                      </p>

                      <p className="text-xs text-gray-600">{item.reason}</p>
                    </div>

                    {/* Footer */}
                    <div className="mt-4 pt-3 border-t border-gray-100 flex justify-between items-center text-xs">
                      <div className="text-gray-500">
                        🗓️ Deadline:{" "}
                        <span className="font-medium text-gray-700">
                          {item.deadline || "Not specified"}
                        </span>
                      </div>

                      <div>
                        {item.urgency === "URGENT" && (
                          <span className="font-bold text-red-600">
                            ⚠️ Act now
                          </span>
                        )}

                        {item.urgency === "SOON" && (
                          <span className="font-semibold text-orange-600">
                            ⏳ Due soon
                          </span>
                        )}

                        {item.urgency === "NORMAL" && (
                          <span className="text-gray-500">
                            No immediate action
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Action */}
                    {item.registration_link && (
                      <div className="mt-4">
                        <a
                          href={item.registration_link}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition"
                        >
                          {item.required_action || "Take Action"} →
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
