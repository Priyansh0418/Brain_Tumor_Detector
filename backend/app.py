from flask import Flask, request, jsonify
from model_loader import load_model, preprocess_image, get_model_info
import numpy as np

app = Flask(__name__)

# Load model once at startup
model = load_model()


@app.after_request
def add_cors_headers(response):
    # Simple CORS headers for local development
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response


@app.route('/api/infer', methods=['POST', 'OPTIONS'])
def infer():
    # Accept file under key 'image' (or fall back to 'file')
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    file_key = 'image' if 'image' in request.files else 'file' if 'file' in request.files else None
    if not file_key:
        return jsonify({'error': "No file part found. Use form key 'image'"}), 400

    f = request.files[file_key]
    if f.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if model is None:
        return jsonify({'error': 'Model not loaded on server'}), 503

    try:
        # Preprocess using the helper which accepts a file-like object.
        # The loader infers the model input size and `preprocess_image` will
        # use that size by default when no target_size is provided.
        x = preprocess_image(f)

        preds = model.predict(x)
        preds = np.asarray(preds)

        # Interpret prediction output shapes:
        # - sigmoid/binary: single probability value
        # - [batch,1]: probability
        # - [batch,2] or [batch,N]: class probabilities
        prob = None
        label = 'normal'

        if preds.ndim == 0:
            prob = float(preds)
        elif preds.ndim == 1:
            if preds.size == 1:
                prob = float(preds[0])
            else:
                idx = int(np.argmax(preds))
                prob = float(preds[idx])
                label = 'tumor' if idx == 1 else 'normal'
        elif preds.ndim == 2:
            if preds.shape[1] == 1:
                prob = float(preds[0, 0])
            else:
                idx = int(np.argmax(preds[0]))
                prob = float(preds[0, idx])
                label = 'tumor' if idx == 1 else 'normal'
        else:
            # fallback: take max of first batch
            idx = int(np.argmax(preds.flatten()))
            prob = float(np.max(preds))
            label = 'tumor' if idx == 1 else 'normal'

        # If we only got a probability (e.g., sigmoid), decide label by threshold 0.5
        if prob is not None and (label == 'normal') and (preds.ndim <= 1 or preds.size == 1 or (preds.ndim == 2 and preds.shape[1] == 1)):
            label = 'tumor' if prob >= 0.5 else 'normal'

        return jsonify({'label': label, 'probability': float(prob)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Return which model was loaded and the inferred input size (for debugging)."""
    info = get_model_info()
    return jsonify(info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
