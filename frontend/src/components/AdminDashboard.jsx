import { useState } from "react";
import { uploadNoticeBatch } from "../api/notifications";

export default function AdminDashboard() {
  const [files, setFiles] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>

      <p>
        Upload a college notice. The AI will automatically understand and
        distribute it to relevant students.
      </p>

      <input
        type="file"
        multiple
        accept=".pdf,.png,.jpg,.jpeg,.webp,.txt"
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />

      {files.length > 0 && (
        <div>
          <p>
            <strong>{files.length}</strong> notices selected
          </p>

          {files.map((file) => (
            <p key={file.name}>📄 {file.name}</p>
          ))}
        </div>
      )}

      <button onClick={handleUpload} disabled={loading || files.length === 0}>
        {loading ? "Processing Notices..." : "Process Notices"}
      </button>

      {error && <p>{error}</p>}

      {result && (
        <div>
          <h2>Processing Complete ✓</h2>

          <p>
            Total: <strong>{result.total_files}</strong>
          </p>

          <p>
            Successful: <strong>{result.successful}</strong>
          </p>

          <p>
            Failed: <strong>{result.failed}</strong>
          </p>

          <div>
            {result.results.map((item) => (
              <div key={item.filename}>
                {item.status === "success" ? "✅" : "❌"}{" "}
                <strong>{item.filename}</strong>
                {item.title && <span> — {item.title}</span>}
                {item.error && <span> — {item.error}</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
