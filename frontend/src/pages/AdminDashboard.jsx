import { useRef, useState } from "react";
import { uploadNoticeBatch, uploadTextNotice } from "../api/notifications";
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
            title: data.notice?.title || "Notice processed successfully",
          },
        ],
      });

      setNoticeText("");
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
                  <h2>Processing complete</h2>
                  <p>Your notices have been processed successfully.</p>
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
                <span>Successful</span>
              </div>

              <div className="result-stat failed">
                <strong>{result.failed}</strong>
                <span>Failed</span>
              </div>
            </div>

            <div className="result-list">
              {result.results.map((item) => (
                <div className="result-item" key={item.filename}>
                  <span>{item.status === "success" ? "✓" : "×"}</span>

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
      </div>
    </main>
  );
}
