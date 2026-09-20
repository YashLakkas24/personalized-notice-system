import { useCallback, useEffect, useRef, useState } from "react";
import {
  uploadNoticeBatch,
  uploadTextNotice,
  createStudent,
  getAllNotices,
} from "../api/notifications";
import "./AdminDashboard.css";

export default function AdminDashboard() {
  const fileInputRef = useRef(null);

  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [noticeText, setNoticeText] = useState("");
  const [textLoading, setTextLoading] = useState(false);
  const [showStudentForm, setShowStudentForm] = useState(false);
  const [noticeHistory, setNoticeHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const [student, setStudent] = useState({
    id: "",
    name: "",
    year: "",
    branch: "",
  });

  const [studentLoading, setStudentLoading] = useState(false);
  const [studentMessage, setStudentMessage] = useState("");

  function handleFiles(selectedFiles) {
    const validFiles = Array.from(selectedFiles).filter((file) => {
      const name = file.name.toLowerCase();

      return (
        name.endsWith(".pdf") ||
        name.endsWith(".png") ||
        name.endsWith(".jpg") ||
        name.endsWith(".jpeg") ||
        name.endsWith(".webp") ||
        name.endsWith(".txt")
      );
    });

    if (validFiles.length === 0) {
      setError("Please select PDF, image or TXT notice files.");
      return;
    }

    setError("");
    setResult(null);

    setFiles((current) => {
      const existing = new Set(current.map((file) => file.name));

      return [
        ...current,
        ...validFiles.filter((file) => !existing.has(file.name)),
      ];
    });
  }

  function handleFileChange(event) {
    handleFiles(event.target.files);
    event.target.value = "";
  }

  function handleDrop(event) {
    event.preventDefault();

    setDragActive(false);

    handleFiles(event.dataTransfer.files);
  }

  function removeFile(fileName) {
    setFiles((current) => current.filter((file) => file.name !== fileName));
  }

  async function handleCreateStudent(event) {
    event.preventDefault();

    setStudentLoading(true);
    setStudentMessage("");
    setError("");

    try {
      await createStudent({
        id: student.id.trim(),
        name: student.name.trim(),
        year: Number(student.year),
        branch: student.branch.trim(),
      });

      setStudentMessage(`${student.name} was added successfully.`);

      setStudent({
        id: "",
        name: "",
        year: "",
        branch: "",
      });
    } catch (err) {
      setError(err.message || "Failed to create student.");
    } finally {
      setStudentLoading(false);
    }
  }

  function formatPostedDate(date) {
    if (!date) return "Date unavailable";

    return new Date(date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }

  const loadNoticeHistory = useCallback(async () => {
    try {
      setHistoryLoading(true);

      const data = await getAllNotices();

      setNoticeHistory(data.notices || []);
    } catch (err) {
      console.error("Failed to load notice history:", err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadNoticeHistory();
  }, [loadNoticeHistory]);

  async function handleTextSubmit() {
    if (!noticeText.trim()) {
      setError("Please enter a notice.");
      return;
    }

    setTextLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await uploadTextNotice(noticeText);

      setResult({
        total_files: 1,
        successful: 1,
        failed: 0,
        results: [
          {
            filename: "Text Notice",
            status: "success",
            title: data.notice?.title || "Notice accepted for processing",
          },
        ],
      });
      setNoticeText("");

      setTimeout(() => {
        loadNoticeHistory();
      }, 1500);
    } catch (err) {
      setError(err.message || "Text notice processing failed.");
    } finally {
      setTextLoading(false);
    }
  }
  async function handleUpload() {
    if (files.length === 0) {
      setError("Please select at least one notice.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await uploadNoticeBatch(files);

      setResult(data);
      setFiles([]);

      await loadNoticeHistory();
    } catch (err) {
      setError(err.message || "Notice processing failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="admin-dashboard">
      <div className="admin-shell">
        {/* HEADER */}
        <header className="admin-header">
          <div>
            <a href="/" className="admin-brand">
              🤖 CampusNotice<span>.AI</span>
            </a>

            <div className="admin-title-row">
              <div className="admin-title-icon">🏛️</div>

              <div>
                <h1>Admin Broadcast Center</h1>

                <p>
                  Upload campus notices. AI handles extraction, understanding
                  and personalization.
                </p>
              </div>
            </div>
          </div>

          <a href="/" className="admin-back">
            ← Home
          </a>
        </header>
        {/* STUDENT MANAGEMENT */}

        <section className="student-management-panel">
          <div className="student-management-copy">
            <div className="student-management-icon">👤</div>

            <div>
              <span className="section-kicker">STUDENT MANAGEMENT</span>

              <h2>Add a student</h2>

              <p>Create the academic profile used for notice eligibility.</p>
            </div>
          </div>

          <button
            type="button"
            className="student-toggle-button"
            onClick={() => {
              setShowStudentForm((current) => !current);
              setStudentMessage("");
              setError("");
            }}
          >
            {showStudentForm ? "× Close" : "＋ Create Student"}
          </button>
        </section>

        {showStudentForm && (
          <section className="student-create-card">
            <div className="student-create-heading">
              <div>
                <h3>Create Student Profile</h3>

                <p>Enter identity and academic information.</p>
              </div>

              <span className="student-step">ACADEMIC PROFILE</span>
            </div>

            <form
              onSubmit={handleCreateStudent}
              className="student-create-form"
            >
              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="student-id">Student ID</label>

                  <input
                    id="student-id"
                    type="text"
                    placeholder="e.g. student_7"
                    value={student.id}
                    onChange={(e) =>
                      setStudent({
                        ...student,
                        id: e.target.value,
                      })
                    }
                    required
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="student-name">Full Name</label>

                  <input
                    id="student-name"
                    type="text"
                    placeholder="e.g. Rahul Patil"
                    value={student.name}
                    onChange={(e) =>
                      setStudent({
                        ...student,
                        name: e.target.value,
                      })
                    }
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="student-year">Academic Year</label>

                  <select
                    id="student-year"
                    value={student.year}
                    onChange={(e) =>
                      setStudent({
                        ...student,
                        year: e.target.value,
                      })
                    }
                    required
                  >
                    <option value="">Select year</option>

                    <option value="1">1st Year</option>

                    <option value="2">2nd Year</option>

                    <option value="3">3rd Year</option>

                    <option value="4">4th Year</option>
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="student-branch">Branch</label>

                  <input
                    id="student-branch"
                    type="text"
                    placeholder="e.g. CSE / AI-ML"
                    value={student.branch}
                    onChange={(e) =>
                      setStudent({
                        ...student,
                        branch: e.target.value,
                      })
                    }
                    required
                  />
                </div>
              </div>

              <div className="student-form-note">
                <span>🔒</span>

                <div>
                  <strong>Personalization is student-controlled</strong>

                  <p>
                    The student will enter their own requirements and
                    preferences from the Student Portal.
                  </p>
                </div>
              </div>

              <button
                type="submit"
                className="student-create-button"
                disabled={studentLoading}
              >
                {studentLoading ? (
                  <>
                    <span className="spinner" />
                    Creating student...
                  </>
                ) : (
                  <>✓ Create Student Profile</>
                )}
              </button>

              {studentMessage && (
                <div className="student-success">✓ {studentMessage}</div>
              )}
            </form>
          </section>
        )}
        {/* UPLOAD */}
        <section className="upload-panel">
          <div className="text-notice-panel">
            <div className="text-notice-header">
              <div>
                <strong>Paste a Notice</strong>
                <span>
                  Quickly process raw notice text without uploading a file.
                </span>
              </div>
            </div>

            <textarea
              value={noticeText}
              onChange={(event) => setNoticeText(event.target.value)}
              placeholder="Paste the raw college notice here..."
              rows={7}
            />

            <button
              type="button"
              className="text-process-button"
              onClick={handleTextSubmit}
              disabled={textLoading || !noticeText.trim()}
            >
              {textLoading ? (
                <>
                  <span className="spinner" />
                  Processing text...
                </>
              ) : (
                <>✨ Process Text Notice</>
              )}
            </button>
          </div>

          <div className="upload-divider">
            <span>OR UPLOAD FILES</span>
          </div>
          <div
            className={`dropzone ${dragActive ? "drag-active" : ""}`}
            onDragEnter={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragOver={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={(event) => {
              event.preventDefault();
              setDragActive(false);
            }}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              className="file-input"
              type="file"
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.webp,.txt"
              onChange={handleFileChange}
            />

            <div className="dropzone-icon">{dragActive ? "📂" : "📥"}</div>

            <strong>
              {dragActive
                ? "Drop your notices here"
                : "Drop notices or click to browse"}
            </strong>

            <span>PDF, PNG, JPG, WEBP or TXT · Multiple files supported</span>
          </div>

          {/* SELECTED FILES */}
          {files.length > 0 && (
            <div className="selected-files">
              <div className="selected-files-header">
                <div>
                  <strong>{files.length}</strong>{" "}
                  {files.length === 1 ? "notice" : "notices"} ready
                </div>

                <button type="button" onClick={() => setFiles([])}>
                  Clear all
                </button>
              </div>

              <div className="file-list">
                {files.map((file) => (
                  <div className="file-item" key={file.name}>
                    <div className="file-info">
                      <span className="file-icon">📄</span>

                      <div>
                        <strong>{file.name}</strong>

                        <span>{(file.size / 1024).toFixed(0)} KB</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => removeFile(file.name)}
                      aria-label={`Remove ${file.name}`}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PROCESS */}
          <button
            className="process-button"
            onClick={handleUpload}
            disabled={loading || files.length === 0}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Processing notices...
              </>
            ) : (
              <>✨ Process & Personalize Notices</>
            )}
          </button>

          {error && (
            <div className="admin-error">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}
        </section>

        {/* HOW IT WORKS */}
        {!result && (
          <section className="admin-process">
            <div>
              <span>01</span>
              <strong>Upload</strong>
              <p>Dump raw notices in any supported format.</p>
            </div>

            <div>
              <span>02</span>
              <strong>Understand</strong>
              <p>AI extracts and structures the notice information.</p>
            </div>

            <div>
              <span>03</span>
              <strong>Personalize</strong>
              <p>Relevant notices are routed to matching students.</p>
            </div>
          </section>
        )}

        {/* RESULT */}
        {result && (
          <section className="result-panel">
            <div className="result-header">
              <div>
                <span className="success-mark">✓</span>

                <div>
                  <h2>Notices accepted</h2>
                  <p>
                    Your notices have been accepted and are being analyzed.
                    Personalized feeds will update shortly.
                  </p>
                </div>
              </div>

              <button
                onClick={() => setResult(null)}
                className="secondary-button"
              >
                Process more
              </button>
            </div>

            <div className="result-summary">
              <div className="result-stat">
                <strong>{result.total_files}</strong>
                <span>Total files</span>
              </div>

              <div className="result-stat success">
                <strong>{result.successful}</strong>
                <span>Accepted</span>
              </div>

              <div className="result-stat failed">
                <strong>{result.failed}</strong>
                <span>Failed</span>
              </div>
            </div>

            <div className="result-list">
              {result.results.map((item) => (
                <div className="result-item" key={item.filename}>
                  <span>
                    {item.status === "success" || item.status === "queued"
                      ? "✓"
                      : "×"}
                  </span>

                  <div>
                    <strong>{item.filename}</strong>

                    {item.title && <p>{item.title}</p>}

                    {item.error && <p className="result-error">{item.error}</p>}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
        {/* NOTICE HISTORY */}
        <section className="notice-history-panel">
          <div className="history-header">
            <div>
              <span className="section-kicker">NOTICE HISTORY</span>

              <h2>Previously published notices</h2>

              <p>
                Every notice processed by the administration, ordered by posting
                date.
              </p>
            </div>

            <div className="history-count">
              {noticeHistory.length}{" "}
              {noticeHistory.length === 1 ? "notice" : "notices"}
            </div>
          </div>

          {historyLoading ? (
            <div className="history-empty">
              <span className="spinner" />
              Loading notice history...
            </div>
          ) : noticeHistory.length === 0 ? (
            <div className="history-empty">
              <span>📭</span>
              <p>No notices have been published yet.</p>
            </div>
          ) : (
            <div className="history-list">
              {noticeHistory.map((notice) => (
                <div className="history-item" key={notice.id}>
                  <div className="history-item-main">
                    <div className="history-file-icon">📄</div>

                    <div>
                      <h3>{notice.title}</h3>

                      <div className="history-meta">
                        <span>{notice.category}</span>
                        <span>
                          Posted {formatPostedDate(notice.created_at)}
                        </span>

                        {notice.is_mandatory && (
                          <span className="history-mandatory">Mandatory</span>
                        )}
                      </div>

                      {notice.summary && (
                        <p className="history-summary">{notice.summary}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
