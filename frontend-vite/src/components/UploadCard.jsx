import React, { useCallback, useEffect, useRef, useState } from "react";

export default function UploadCard({
  onSubmit = async () => {},
  initialImage = null,
}) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(initialImage);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (initialImage) setPreview(initialImage);
  }, [initialImage]);

  useEffect(() => {
    let url;
    if (file) {
      url = URL.createObjectURL(file);
      setPreview(url);
    }
    return () => {
      if (url) URL.revokeObjectURL(url);
    };
  }, [file]);

  const validateFile = useCallback((f) => {
    if (!f) return "No file provided";
    if (!f.type || !f.type.startsWith("image/")) return "File must be an image";
    const max = 10 * 1024 * 1024; // allow slightly larger for high-res MRIs
    if (f.size > max) return "File must be smaller than 10 MB";
    return null;
  }, []);

  const handleFiles = useCallback(
    (f) => {
      setError(null);
      const v = validateFile(f);
      if (v) {
        setFile(null);
        setPreview(null);
        setError(v);
        return;
      }
      setFile(f);
    },
    [validateFile]
  );

  const onInputChange = (e) => handleFiles(e.target.files && e.target.files[0]);

  const onDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    handleFiles(f);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };
  const onDragLeave = () => setDragOver(false);

  const chooseFile = () => {
    setError(null);
    if (inputRef.current) inputRef.current.click();
  };

  const handleClassify = async () => {
    if (!file) {
      setError("No file selected");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await onSubmit(file);
    } catch (err) {
      setError(err && err.message ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card upload-area" aria-live="polite">
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="sr-only"
        onChange={onInputChange}
      />

      <div
        className={`dropzone ${dragOver ? "dragover" : ""}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={chooseFile}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") chooseFile();
        }}
      >
        {!preview && (
          <div>
            <div className="drop-lbl">
              Drag & drop an MRI image, or click to choose
            </div>
            <div className="drop-sub">
              Supported: .jpg, .png. Recommended: 224x224 - 1024x1024
            </div>
          </div>
        )}

        {preview && (
          <div>
            <img src={preview} alt="preview" className="thumb" />
          </div>
        )}
      </div>

      <div className="actions">
        <button
          type="button"
          className="btn btn-ghost"
          onClick={chooseFile}
          disabled={loading}
        >
          Choose file
        </button>

        <button
          type="button"
          className="btn btn-primary"
          onClick={handleClassify}
          disabled={loading || !file}
        >
          {loading ? (
            <span
              style={{ display: "inline-flex", gap: 8, alignItems: "center" }}
            >
              <span className="spinner" />
              Classifying...
            </span>
          ) : (
            "Classify"
          )}
        </button>
      </div>

      {error && (
        <div className="error-text" style={{ marginTop: 8 }}>
          {error}
        </div>
      )}
    </div>
  );
}
