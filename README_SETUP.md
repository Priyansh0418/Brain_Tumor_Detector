# Setup & run (Windows PowerShell)

This file shows recommended steps to create a Python virtual environment, install backend dependencies, and run the frontend dev server for the Vite React app. Use PowerShell (the commands below are PowerShell-friendly).

1. Create & activate a venv (recommended Python 3.10 or 3.11 on Windows)

```powershell
cd 'D:\Git Going\Brain_Tumor_Detector'
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install backend Python dependencies

```powershell
# from repo root (venv activated)
python -m pip install --upgrade pip setuptools wheel
pip install -r backend\requirements.txt
```

Notes on TensorFlow

- On Windows, TensorFlow wheels are available for Python 3.10 and 3.11. If `pip install tensorflow` fails,
  use the CPU build `tensorflow-cpu` as included in `backend/requirements.txt`.
- For GPU support, follow the official TensorFlow guide matching CUDA/cuDNN versions.

3. Start the backend

```powershell
cd backend
python app.py
```

4. Frontend: install node deps and run Vite dev server

Open a separate terminal (PowerShell). If you haven't installed Node.js, install Node 18+.

```powershell
cd 'D:\Git Going\Brain_Tumor_Detector\frontend-vite'
npm install
npm run dev
```

5. Smoke tests

- Use the provided validation script to check the model file (optional):

```powershell
# From repo root, will default to models/bt_model.h5
python tools\validate_model.py models\Brain_Tumor_Model.h5
```

- Use the test client to POST a small image to the running backend:

```powershell
python tools\test_infer.py
```

If you hit issues installing TensorFlow locally, consider running training and validation in Google Colab (see `tools/colab_train.ipynb`).
