"""Post a real image file to the backend /api/infer endpoint and print JSON result.

Usage:
  python tools\run_file_infer.py path\to\image.jpg

Make sure the backend is running (python backend/app.py).
"""
import sys
import requests

API_URL = 'http://127.0.0.1:5000/api/infer'


def main(image_path: str):
    with open(image_path, 'rb') as f:
        files = {'image': (image_path, f, 'application/octet-stream')}
        try:
            resp = requests.post(API_URL, files=files, timeout=60)
        except Exception as e:
            print('Request failed:', e)
            return
    print('HTTP', resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python tools\\run_file_infer.py path\\to\\image.jpg')
        sys.exit(1)
    main(sys.argv[1])
