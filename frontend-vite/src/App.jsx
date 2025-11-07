import React, { useState, useCallback } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import UploadCard from "./components/UploadCard";
import ResultCard from "./components/ResultCard";
import ModelInfoCard from "./components/ModelInfoCard";
import inferImage from "./services/api";
import "./styles.css";
import Home from "./pages/Home";

function UploadPage() {
  const [result, setResult] = useState(null);
  const [uploadKey, setUploadKey] = useState(0);

  const handleSubmit = useCallback(async (file) => {
    // call backend service and set result
    const res = await inferImage(file);
    // normalise returned keys to label/probability
    const label = res.label ?? res.result?.label ?? null;
    const probability =
      res.probability ??
      res.result?.confidence ??
      res.result?.confidence ??
      res.confidence ??
      null;
    setResult({ label, probability });
  }, []);

  const handleRetry = useCallback(() => {
    setResult(null);
    // bump key so UploadCard remounts and clears internal state
    setUploadKey((k) => k + 1);
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Upload MRI</h2>
      <div className="layout-grid">
        <div>
          <UploadCard key={uploadKey} onSubmit={handleSubmit} />
        </div>

        <aside>
          <ModelInfoCard />
          <ResultCard
            label={result?.label}
            probability={result?.probability}
            onRetry={handleRetry}
          />
        </aside>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <div>
        <Header />
        <main>
          <div className="app-container">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/upload" element={<UploadPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}
