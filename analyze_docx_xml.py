import zipfile

# docx-файлы - это zip-архивы
with zipfile.ZipFile('docact.docx', 'r') as zf:
    # Извлекаем основной XML-файл документа
    xml_content = zf.read('word/document.xml').decode('utf-8')

# Сохраняем XML в текстовый файл для анализа
with open('document_xml.txt', 'w', encoding='utf-8') as f:
    f.write(xml_content)

print("Содержимое word/document.xml было извлечено в document_xml.txt")