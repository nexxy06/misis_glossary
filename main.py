from bs4 import BeautifulSoup
import re

def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')

    # Second row has actual column names
    headers_row = rows[1]
    # headers = [cell.get_text(strip=True) for cell in headers_row.find_all(['td', 'th'])[1:]]


    raw_headers = headers_row.find_all(['td', 'th'])[1:]  # skip index cell
    headers = []
    for cell in raw_headers:
        text = cell.get_text(strip=True)
        # Remove leading number/space/dash (e.g., "1- ", "2 -", "0 - ")
        cleaned = re.sub(r'^\d+\s*[-–—]\s*', '', text)
        headers.append(cleaned)


    data = []
    for row in rows[2:]:  # skip top header rows
        cells = row.find_all(['td', 'th'])
        if len(cells) <= 1:
            continue

        row_data = []
        for i, cell in enumerate(cells[1:]):  # skip row index
            # Preserve inner HTML for image cell
            if i < len(headers) and headers[i] == "Изображение":
                img_tag = cell.find('img')
                if img_tag and img_tag.has_attr('src'):
                    img_html = f'<img src="{img_tag["src"]}" style="max-width:70%; height:auto; border:1px solid #ccc; padding:4px;" />'
                    row_data.append(img_html)
                else:
                    row_data.append('')  # No image

            else:
                raw_text = cell.get_text()  # preserve newlines
                row_data.append(raw_text.strip())

        if any(row_data):
            data.append(row_data)

    return headers, data

def generate_glossary_html(headers, data):
    glossary = {}
    for row in data:
        term = row[0]
        if not term:
            continue
        letter = term[0].upper()
        glossary.setdefault(letter, []).append(row)

    sorted_letters = sorted(glossary.keys())

    html = ['<!DOCTYPE html>', '<html lang="ru">', '<head>',
            '<meta charset="UTF-8">', '<title>Glossary</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; padding: 20px; }',
            '.toc { margin-bottom: 40px; }',
            '.toc a { margin-right: 10px; font-size: 18px; text-decoration: none; color: #0056b3; }',
            '.toc a:hover { text-decoration: underline; }',
            '.letter-section { margin-top: 40px; }',
            '.letter-title { font-size: 28px; font-weight: bold; border-bottom: 2px solid #333; margin-bottom: 20px; }',
            '.term-entry { margin-bottom: 30px; }',
            '.term-title { font-size: 20px; font-weight: bold; margin-bottom: 10px; }',
            '.field { margin-left: 20px; margin-bottom: 10px; }',
            '.field-title { font-weight: bold; display: block; margin-bottom: 3px; }',
            'img { max-width: 70%; height: auto; border: 1px solid #ccc; padding: 4px; }',
            '</style>',
            '</head><body>',
            '<h1>Глоссарий к лекции 19: Основы IPv6 </h1>',
            '<small>Выполнено студентами группы БИВТ-23-6:<br></small>',
            '<small>Панов Н. В.,<br></small>',
            '<small>Пешков М.Е.,<br></small>',
            '<small>Сазонов А. К.<br></small>']

    # Add Table of Contents
    html.append('<div class="toc"><br><strong>Навигация:</strong><br>')
    for letter in sorted_letters:
        html.append(f'<a href="#{letter}">{letter}</a>')
    html.append('</div>')

    for letter in sorted_letters:
        html.append(f'<div class="letter-section" id="{letter}">')
        html.append(f'<div class="letter-title">{letter}</div>')
        for entry in sorted(glossary[letter], key=lambda x: x[0]):
            html.append('<div class="term-entry">')
            html.append(f'<div class="term-title">{entry[0]}</div>')
            for i, content in enumerate(entry[1:], start=1):
                if i < len(headers):
                    title = headers[i]
                    if content.strip():
                        if title == "Изображение":
                            html.append(f'<div class="field"><span class="field-title">{title}:</span>{content}</div>')
                        else:
                            content_html = content.replace('\n', '<br/>')
                            html.append(f'<div class="field"><span class="field-title">{title}:</span> {content_html}</div>')

            html.append('</div>')
        html.append('</div>')

    html.append('</body></html>')
    return '\n'.join(html)


def convert_google_sheet_html_to_glossary(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    headers, data = extract_table_data(html_content)
    print(data[0][1])
    glossary_html = generate_glossary_html(headers, data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(glossary_html)

    print(f"Glossary saved to: {output_path}")

# Example usage
convert_google_sheet_html_to_glossary("old.html", "new.html")
