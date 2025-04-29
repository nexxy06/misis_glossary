import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import mimetypes
import time
import re
import openpyxl  # библиотека для работы с Excel

HTML_FILE = 'new.html'
OUTPUT_HTML_FILE = 'updated_' + HTML_FILE
IMAGE_DIR = 'src'
EXCEL_FILE = 'images.xlsx'  # ваш Excel-файл
COLUMN_NUMBER = 4  # пятый столбец (E)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Referer': '',
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

def extract_url_from_excel_formula(formula):
    """Extract URL from Excel formula like =image("http://example.com/image.jpg")"""
    match = re.search(r'=image\("([^"]+)"\)', formula, re.IGNORECASE)
    return match.group(1) if match else None

def get_image_urls_from_excel(file_path, column_num):
    """Get all image URLs from specified column in Excel file"""
    urls = []
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        
        for row in sheet.iter_rows(min_col=column_num, max_col=column_num):
            for cell in row:
                if cell.value and isinstance(cell.value, str) and cell.value.startswith('=image('):
                    url = extract_url_from_excel_formula(cell.value)
                    if url:
                        urls.append(url)
        
        return urls
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # Получаем URL из Excel
    image_urls = get_image_urls_from_excel(EXCEL_FILE, COLUMN_NUMBER)
    print()
    if not image_urls:
        print("No image URLs found in Excel file")
        return

    # Загружаем HTML
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Скачиваем изображения и заменяем URL в HTML
    for i, img in enumerate(soup.find_all('img')):
        if i >= len(image_urls):
            break
            
        url = image_urls[i]
        filename = download_image(url, IMAGE_DIR)
        if filename:
            img['src'] = f'{IMAGE_DIR}/{filename}'

    # Сохраняем обновленный HTML
    with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f'Done! Updated HTML saved as: {OUTPUT_HTML_FILE}')
    print(f'Downloaded {len(image_urls)} images from Excel file')

if __name__ == '__main__':
    main()