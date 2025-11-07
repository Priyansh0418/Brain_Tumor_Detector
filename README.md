# Brain Tumor Detector

Small demo that shows a simple web UI to upload brain MRI images and a minimal Flask backend that runs a Keras model to detect tumors. This project is intended for educational purposes only.

Quick start

1. Create and activate a Python virtualenv, then install backend dependencies:

```powershell
cd "D:/Git Going/Brain_Tumor_Detector"
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

2. Put your trained Keras model file at `models/bt_model.h5`.

3. Run the backend:

```powershell
python backend/app.py
```

4. Run the frontend (the Vite project is in `frontend-vite`). If you have a different `frontend/` folder use that instead:

```powershell
cd frontend-vite
npm install
npm run dev
```

Notes

- This is a demo / educational project and not a clinical diagnostic tool. Do not use it for medical decisions.
- If you don't want to install TensorFlow locally, you can mock the model or run the backend without a model (it will return a placeholder response).
