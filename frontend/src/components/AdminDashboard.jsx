import { useState } from "react";
import { uploadNotice } from "../api/notifications";

export default function AdminDashboard() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleUpload() {
    if (!file) {
      setError("Please select a PDF or image.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await uploadNotice(file);

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
        accept=".pdf,.png,.jpg,.jpeg,.webp"
        onChange={(e) => setFile(e.target.files[0])}
      />

      {file && (
        <p>
          Selected: <strong>{file.name}</strong>
        </p>
      )}

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Process Notice"}
      </button>

      {error && <p>{error}</p>}

      {result && (
        <div>
          <h2>Notice Processed ✓</h2>

          <p>
            <strong>{result.notice?.title}</strong>
          </p>

          <p>
            Notifications created:{" "}
            <strong>{result.notifications_created}</strong>
          </p>
        </div>
      )}
    </div>
  );
}
