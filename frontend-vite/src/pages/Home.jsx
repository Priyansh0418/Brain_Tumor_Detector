import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="relative min-h-screen w-full overflow-x-hidden">
      <div className="app-container">
        {/* Hero */}
        <section
          className="card hero-vignette"
          style={{
            padding: 28,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",
          }}
        >
          <h1
            style={{
              fontSize: 36,
              margin: 0,
              lineHeight: 1.05,
              fontWeight: 800,
            }}
          >
            Brain Tumor Detector
          </h1>
          <p className="muted" style={{ marginTop: 8, fontSize: 16 }}>
            Upload an MRI scan and get a quick, research-grade classification.
          </p>

          <p style={{ marginTop: 12, maxWidth: 720, color: "#dff6f4" }}>
            This demo uses a convolutional model to evaluate MRI images and
            estimate the probability of a brain tumor. Please use anonymized
            images and consult a specialist for medical decisions.
          </p>

          <div style={{ marginTop: 18, width: "100%", maxWidth: 540 }}>
            <Link
              to="/upload"
              className="btn-primary cta-large"
              aria-label="Upload an MRI image"
            >
              <span
                className="material-symbols-outlined"
                aria-hidden
                style={{ fontSize: 20 }}
              >
                upload_file
              </span>
              <strong>Upload Image</strong>
            </Link>

            <div style={{ marginTop: 10, textAlign: "center" }}>
              <div className="muted" style={{ fontSize: 13 }}>
                Supports .jpg, .png — recommended ≤ 10MB
              </div>
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <a href="#how-it-works" className="muted" style={{ fontSize: 14 }}>
              How it works
            </a>
          </div>
        </section>

        {/* Samples removed as requested */}

        {/* How it works section (one paragraph guidelines) */}
        <section id="how-it-works" style={{ marginTop: 22 }} className="card">
          <h3 style={{ marginTop: 0 }}>How it works</h3>
          <p className="muted" style={{ marginTop: 8 }}>
            Upload a single axial MRI slice (or a clear cross-section). The
            model preprocesses the image and returns a probability score between
            0–100%. This demo uses a mock/fallback model when a production model
            is not present — results should be treated as educational only.
          </p>
        </section>
      </div>
    </div>
  );
}
