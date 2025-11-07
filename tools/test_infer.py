"""
Simple test script to POST a small generated image to the backend /api/infer

Usage:
  cd tools
  python test_infer.py

This will create an in-memory PNG and send it to http://localhost:5000/api/infer
"""
import io
import sys
from PIL import Image
import requests

API = 'http://127.0.0.1:5000/api/infer'

def make_test_image():
    img = Image.new('RGB', (64, 64), color=(200, 40, 40))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def main():
    buf = make_test_image()
    files = {'image': ('test.png', buf, 'image/png')}
    try:
        resp = requests.post(API, files=files, timeout=10)
    except Exception as e:
        print('Request failed:', e)
        sys.exit(2)

    print('HTTP', resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

if __name__ == '__main__':
    main()
