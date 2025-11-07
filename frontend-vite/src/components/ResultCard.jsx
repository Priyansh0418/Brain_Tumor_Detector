import React from "react";

export default function ResultCard({
  label = null,
  probability = null,
  onRetry = () => {},
}) {
  const normalized = (p) => {
    if (p == null) return null;
    const n = Number(p);
    if (Number.isNaN(n)) return null;
    return n > 1 ? n : n * 100;
  };

  const pct = normalized(probability);
  const pctClamped = pct == null ? 0 : Math.min(100, Math.max(0, pct));
  const pctText = pct == null ? "—" : `${Math.round(pct * 10) / 10}%`;

  const isTumor = label && String(label).toLowerCase().includes("tumor");
  const displayLabel = label ? (isTumor ? "Tumor" : "Normal") : "No result";

  return (
    <div className="card result-card" aria-live="polite">
      <div className="result-header">
        <div>
          <div className="muted">Result</div>
          <div style={{ marginTop: 6 }}>
            <span className="result-label">{displayLabel}</span>
            <span style={{ marginLeft: 12 }} className="muted">
              {pctText}
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div className={`label-chip ${isTumor ? "tumor" : "normal"}`}>
            {isTumor ? "Tumor" : "Normal"}
          </div>
          <button type="button" className="btn" onClick={onRetry}>
            Try again
          </button>
        </div>
      </div>

      <div>
        <div
          className="progress-track"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(pctClamped)}
        >
          <div
            className="progress-fill"
            style={{
              width: `${pctClamped}%`,
              background: isTumor
                ? "linear-gradient(90deg,#ff7b7b,#ef4444)"
                : "linear-gradient(90deg,#34d399,#10b981)",
            }}
          />
        </div>
      </div>

      {probability == null && (
        <div className="muted" style={{ marginTop: 8 }}>
          No prediction available. Upload an image to classify.
        </div>
      )}
    </div>
  );
}
