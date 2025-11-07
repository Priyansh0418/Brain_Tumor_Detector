Training in Google Colab (recommended)

This document explains how to train a binary Brain Tumor detector using Google Colab and the provided training script `tools/train_colab.py`.

Prerequisites

- A Google account to use Colab
- Dataset prepared as folders with `train/` and `val/` subfolders and class folders inside (e.g., `train/tumor`, `train/normal`)

Quick steps (Colab):

1. Open a new Colab notebook and set the runtime to GPU (Runtime -> Change runtime type -> GPU).
2. Upload the repository to the Colab session or mount your Google Drive and clone this repo there.

   Example (in a notebook cell):

   ```python
   !git clone https://github.com/Priyansh0418/Brain_Tumor_Detector.git
   %cd Brain_Tumor_Detector
   ```

3. Upload or fetch the dataset. Options:

   - Upload a ZIP and unzip it into `/content/data`.
   - Use Kaggle API to download a dataset: upload your `kaggle.json` and run `!kaggle datasets download -d <dataset>` then unzip.

4. Run the training script. Example command (in a notebook cell):

   ```bash
   !python tools/train_colab.py --data_dir /content/data --output /content/bt_model.h5 --epochs 12 --batch_size 16
   ```

5. Download the trained `bt_model.h5` from Colab to your machine, then copy it into the repo `models/` folder locally.

6. Restart the backend server (on your machine) so it detects and loads the real model:
   ```powershell
   cd "D:/Git Going/Brain_Tumor_Detector/backend"
   python app.py
   ```

Notes and tips

- If your dataset is multi-class (e.g., glioma/meningioma/pituitary/normal), convert to binary by grouping all tumor classes into `tumor/` and the healthy class into `normal/` for the demo. Or adapt the script for multi-class training.
- For better results, increase epochs, use a larger base model, or fine-tune the base (set `base_trainable=True` in the script).
- The script uses EfficientNetB0 and saves the best model to the `--output` path.

If you'd like, I can also:

- Add a Colab notebook pre-filled with these steps and help you run it.
- Add a small eval script to run a test MRI through the model and print predicted probability.
