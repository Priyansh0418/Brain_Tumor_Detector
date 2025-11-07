import React, { useEffect, useState } from "react";
import { getModelInfo } from "../services/api";

export default function ModelInfoCard() {
  const [info, setInfo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    getModelInfo()
      .then((j) => {
        if (!mounted) return;
        setInfo(j);
      })
      .catch((e) => {
        if (!mounted) return;
        setError(e.message || String(e));
      });
    return () => (mounted = false);
  }, []);

  return (
    <div className="card model-info-card">
      <h4 style={{ marginTop: 0 }}>Model</h4>
      {error && <div className="muted">Error: {error}</div>}
      {!error && !info && <div className="muted">Loading model info…</div>}
      {info && (
        <div style={{ fontSize: 14 }}>
          <div>
            <strong>Path:</strong>{" "}
            {info.model_path ? (
              <span style={{ color: "#0b7285" }}>{info.model_path}</span>
            ) : (
              <em className="muted">(none — running fallback)</em>
            )}
          </div>
          <div style={{ marginTop: 6 }}>
            <strong>Input size:</strong> {info.input_size?.join(" × ")}
          </div>
        </div>
      )}
    </div>
  );
}
