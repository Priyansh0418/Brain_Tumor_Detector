const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

export async function inferImage(file) {
  if (!file) throw new Error("No file provided to inferImage");

  const url = `${API_BASE}/api/infer`;
  const form = new FormData();
  form.append("file", file);

  let res;
  try {
    res = await fetch(url, {
      method: "POST",
      body: form,
    });
  } catch (err) {
    throw new Error(`Network error when calling inference API: ${err.message}`);
  }

  let bodyText;
  try {
    bodyText = await res.text();
  } catch (err) {
    throw new Error(`Failed to read response from server: ${err.message}`);
  }

  if (!res.ok) {
    // try to parse JSON message if present
    try {
      const parsed = JSON.parse(bodyText);
      const msg = parsed.error || parsed.message || bodyText;
      throw new Error(`Server error (${res.status}): ${msg}`);
    } catch {
      throw new Error(
        `Server error (${res.status}): ${bodyText || res.statusText}`
      );
    }
  }

  // parse successful JSON
  try {
    const json = JSON.parse(bodyText);
    // normalize keys
    const label = json.result?.label ?? json.label ?? null;
    const probability =
      json.result?.confidence ?? json.probability ?? json.confidence ?? null;

    if (!label || probability == null) {
      // return full json if shape unexpected
      return json;
    }

    return { label, probability };
  } catch (err) {
    throw new Error(`Failed to parse JSON response: ${err.message}`);
  }
}

export default inferImage;

export async function getModelInfo() {
  const url = `${API_BASE}/api/model-info`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch model info: ${res.status}`);
  }
  return res.json();
}
