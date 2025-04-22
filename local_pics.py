import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path
import mimetypes
import time

HTML_FILE = 'new.html'
OUTPUT_HTML_FILE = 'updated_' + HTML_FILE
IMAGE_DIR = 'src'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Referer': '',  # optional: can use original page URL if needed
}

def get_filename_from_url(url, content_type=None):
    """Try to guess filename from URL or content-type."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename or '.' not in filename:
        ext = mimetypes.guess_extension(content_type or '')
        filename = 'image_' + os.urandom(4).hex() + (ext or '.jpg')
    return filename

def download_image(url, save_dir):
    """Download image from URL with headers."""
    time.sleep(2)
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            filename = get_filename_from_url(url, content_type)
            local_path = os.path.join(save_dir, filename)

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            return filename
        else:
            print(f"Failed to download {url}")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    for img in soup.find_all('img'):
        src = img.get('src')
        if src and src.startswith(('http://', 'https://')):
            filename = download_image(src, IMAGE_DIR)
            if filename:
                img['src'] = f'{IMAGE_DIR}/{filename}'

    with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f'Done! Updated HTML saved as: {OUTPUT_HTML_FILE}')

if __name__ == '__main__':
    main()
