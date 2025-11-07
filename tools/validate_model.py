"""Validate a Keras .h5 model file.

Usage:
  python tools\validate_model.py [path/to/model.h5]

This script attempts to:
- confirm the file exists and print its size
- import TensorFlow/Keras and load the model
- print model input shape and a brief summary

If TensorFlow is not installed in your environment, the script will print instructions
for how to install a compatible TensorFlow build (or suggest using Colab).
"""
import sys
import os
import math


def human_size(nbytes):
    if nbytes == 0:
        return '0B'
    sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    i = int(math.floor(math.log(nbytes, 1024)))
    p = math.pow(1024, i)
    s = round(nbytes / p, 2)
    return f"{s} {sizes[i]}"


def main():
    model_path = sys.argv[1] if len(sys.argv) > 1 else 'models/bt_model.h5'

    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("Make sure you placed your .h5 file into the repository 'models/' folder and retry.")
        sys.exit(2)

    st = os.stat(model_path)
    print(f"Found model: {model_path} ({human_size(st.st_size)})")

    try:
        import tensorflow as tf
        from tensorflow import keras
    except Exception as e:
        print("Could not import TensorFlow in this environment:")
        print(" ", e)
        print()
        print("Common fixes:")
        print(" - Make sure you're using Python 3.10 or 3.11 on Windows for TensorFlow wheels.")
        print(" - Create a fresh venv and run: python -m pip install --upgrade pip setuptools wheel")
        print(" - Then install: python -m pip install tensorflow-cpu")
        print("Alternatively, run validation in Google Colab where TensorFlow is preinstalled.")
        sys.exit(3)

    print('TensorFlow version:', tf.__version__)
    try:
        print('Loading model (this may take a moment)...')
        model = keras.models.load_model(model_path)
    except Exception as e:
        print('Failed to load model:', e)
        print('If this fails due to custom objects or a mismatched TF version, try loading in Colab or with the TF version used for training.')
        sys.exit(4)

    try:
        # Print a compact input/output shape summary
        input_shapes = [layer.input_shape for layer in model.layers if hasattr(layer, 'input_shape')]
        print('\nSample input shapes found (first few):')
        for s in input_shapes[:5]:
            print(' ', s)
    except Exception:
        pass

    print('\nModel summary:')
    try:
        model.summary()
    except Exception as e:
        print('Could not print full summary:', e)

    # Print top-level metadata if available
    try:
        # for Sequential/Functional models, try to infer input shape
        if hasattr(model, 'inputs') and model.inputs:
            print('\nModel input tensor(s):')
            for t in model.inputs:
                print(' ', t.shape)
        if hasattr(model, 'outputs') and model.outputs:
            print('\nModel output tensor(s):')
            for t in model.outputs:
                print(' ', t.shape)
    except Exception:
        pass

    print('\nValidation complete — if the model loaded successfully you can use it for inference.')


if __name__ == '__main__':
    main()
