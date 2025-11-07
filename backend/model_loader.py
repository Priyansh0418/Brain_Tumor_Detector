"""
Model loader helpers.

This loader will attempt to find and load a Keras .h5 model from the `models/` folder.
If a model is found it sets `MODEL_INPUT_SIZE` to the model's expected spatial input
shape (width, height) so `preprocess_image` can resize inputs correctly.

If loading fails (for example TensorFlow is not installed) a DummyModel is returned
so the server can continue to function during development.
"""

import os
import glob

# Module-level value populated when a model is successfully loaded. Format: (width, height)
MODEL_INPUT_SIZE = (224, 224)
# Path to the model file that was successfully loaded (None if using DummyModel)
LOADED_MODEL_PATH = None


def get_model_info():
  """Return a small dict describing the loaded model (path and input size)."""
  return {'model_path': LOADED_MODEL_PATH, 'input_size': MODEL_INPUT_SIZE}


def _make_dummy_model():
  class DummyModel:
    def predict(self, x):
      import numpy as _np
      batch = _np.zeros((x.shape[0], 2), dtype=float)
      batch[:, 0] = 0.1
      batch[:, 1] = 0.9
      return batch

  return DummyModel()


def load_model(path: str = None):
  """Try to load a Keras model.

  If `path` is provided we try that first. Otherwise we scan for any `models/*.h5`
  files and try to load the first working model. On success we update
  `MODEL_INPUT_SIZE` to the spatial input shape inferred from the model.
  """
  global MODEL_INPUT_SIZE

  # Helper to try loading a specific path
  def try_load(p):
    try:
      from tensorflow.keras.models import load_model as keras_load_model
      model = keras_load_model(p)
      print(f"Model loaded from: {p}")
      # record loaded path

      # Ensure we update the module-level MODEL_INPUT_SIZE when inferring shape
      global MODEL_INPUT_SIZE

      # Set module-level LOADED_MODEL_PATH
      try:
        globals()['LOADED_MODEL_PATH'] = p
      except Exception:
        pass

      # Try to infer input size (Keras tensors usually have shape (None,H,W,C))
      try:
        inp = model.inputs[0]
        print('Model inputs:', inp)
        # Try the normal Keras/TensorShape API first
        try:
          raw_shape = inp.shape.as_list()
        except Exception:
          # Fallback: parse the string representation (e.g. '(None, 128, 128, 3)')
          s = str(inp.shape)
          import re
          nums = re.findall(r"\d+", s)
          raw_shape = [None] + [int(x) for x in nums]
        print('Raw input shape list:', raw_shape)
        shape = tuple(int(d) if d is not None else None for d in raw_shape)
        # shape is (None, H, W, C) or (None, W, H, C) depending on layout, but most models use (None,H,W,C)
        if len(shape) >= 3:
          # prefer (width, height) as used by our preprocessing
          # many models have (None, H, W, C)
          H = shape[1]
          W = shape[2]
          print(f'Parsed H={H}, W={W}')
          if W and H:
            MODEL_INPUT_SIZE = (W, H)
            print(f"Inferred model input size: {MODEL_INPUT_SIZE}")
      except Exception:
        pass

      return model
    except Exception as e:
      raise

  # If a specific path provided, try that first
  candidates = []
  if path:
    candidates.append(path)

  # Add common filenames and any .h5 in models/
  # Candidate relative locations to check (backend may be started with cwd=backend)
  module_dir = os.path.dirname(os.path.abspath(__file__))
  repo_root = os.path.abspath(os.path.join(module_dir, '..'))

  # Prefer .keras files and SavedModel directories first (so these newer formats
  # are selected before older or corrupted .h5 files).
  candidates.extend([
    os.path.join('models', 'bt_model.keras'),
    os.path.join('models', 'brain_tumor_model.keras'),
    os.path.join('models', 'Brain_Tumor_Model.keras'),
    os.path.join(repo_root, 'models', 'bt_model.keras'),
    os.path.join(repo_root, 'models', 'brain_tumor_model.keras'),
    os.path.join(repo_root, 'models', 'Brain_Tumor_Model.keras'),
  ])

  # Also consider SavedModel directories inside models/ (look for saved_model.pb)
  def add_savedmodel_dirs(root):
    try:
      for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, 'saved_model.pb')):
          candidates.append(p)
    except Exception:
      pass

  add_savedmodel_dirs(os.path.join(module_dir, 'models'))
  add_savedmodel_dirs(os.path.join(repo_root, 'models'))

  # Then fall back to .h5 files (explicit names and any found in models/)
  candidates.extend([
    os.path.join('models', 'bt_model.h5'),
    os.path.join('models', 'Brain_Tumor_Model.h5'),
    os.path.join(repo_root, 'models', 'bt_model.h5'),
    os.path.join(repo_root, 'models', 'Brain_Tumor_Model.h5'),
  ])

  candidates.extend(sorted(glob.glob(os.path.join('models', '*.h5'))))
  candidates.extend(sorted(glob.glob(os.path.join(repo_root, 'models', '*.h5'))))

  tried = set()
  for cand in candidates:
    if not cand or cand in tried:
      continue
    tried.add(cand)
    if not os.path.exists(cand):
      continue
    try:
      return try_load(cand)
    except Exception as e:
      print(f"Failed to load model at {cand}: {e}")
      continue

  # If we reach here, loading failed or TensorFlow unavailable
  try:
    # Provide a helpful message if TF isn't present
    import tensorflow  # noqa: F401
    print("Model files found but none could be loaded due to an error.")
  except Exception as e:
    print("Warning: could not load model (will use mock model for dev):", e)

  print("Using DummyModel for development (predicts tumor with 90% confidence).")
  return _make_dummy_model()


def preprocess_image(file_stream, target_size=None):
    """Read image from a file-like object and preprocess for Keras.

    Args:
      file_stream: file-like object (supports read/open) containing image data.
      target_size: optional (width, height) tuple to resize the image to. If None,
        the loader's inferred `MODEL_INPUT_SIZE` will be used.

    Returns:
      A numpy array shaped (1, H, W, 3) with float32 values in [0,1].
    """
    from PIL import Image
    import numpy as np

    # If no explicit target provided, use inferred model input size
    if target_size is None:
        target_size = MODEL_INPUT_SIZE

    # Open image (Pillow accepts file-like objects) and ensure RGB
    img = Image.open(file_stream).convert('RGB')

    # Resize to target size (width, height)
    img = img.resize(target_size)

    # Convert to numpy array and normalize to [0,1]
    arr = np.asarray(img).astype('float32') / 255.0

    # Add batch dimension (1, H, W, 3)
    arr = np.expand_dims(arr, axis=0)
    return arr

