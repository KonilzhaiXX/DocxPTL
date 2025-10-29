import io
from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate, RichText
import os
from datetime import datetime
from functools import lru_cache

app = Flask(__name__)

# Cache for DocxTemplate objects to avoid repeated disk I/O
_template_cache = {}

# --- Словари для видов работ ---
WORK_TYPE_TO_NUMBER = {
    "Сварка трубы": 1,
    "Сварка м/к": 2,
    "Сварка резервуара": 3,
    "Монтаж М/К": 4,
    "Проведение испытаний": 5,
    "Монтаж изоляции": 6,
    "Монтаж кабеля": 7,
    "Монтаж лотков": 8,
    "Монтаж оборудования": 9,
    "Монтаж под армирование": 10,
    "Монтаж вентиляции": 11,
    "Окраска м/к": 12,
    "Окраска резервуара": 13,
    "Окраска оборудования": 14,
    "Абразивная обработка": 15,
    "Монтаж панелей": 16,
    "Нанесение ОГЗ": 17,
    "Окраска трубы": 18,
    "Окраска болтовых соединений": 19
}

CIRCLED_NUMBERS = {
    1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤',
    6: '⑥', 7: '⑦', 8: '⑧', 9: '⑨', 10: '⑩',
    11: '⑪', 12: '⑫', 13: '⑬', 14: '⑭', 15: '⑮',
    16: '⑯', 17: '⑰', 18: '⑱', 19: '⑲', 20: '⑳'
}
# --------------------------------

def get_template(template_path):
    """Get a DocxTemplate object with caching to avoid repeated disk I/O."""
    if template_path not in _template_cache:
        _template_cache[template_path] = DocxTemplate(template_path)
    # Create a new instance from the cached template to avoid state issues
    return DocxTemplate(template_path)

def pad_list(lst, target_length, fill_value=None):
    """Efficiently pad a list to target_length with fill_value."""
    if fill_value is None:
        fill_value = {'FullName': '', 'hour': ''}
    current_length = len(lst)
    if current_length < target_length:
        lst.extend([fill_value.copy() if isinstance(fill_value, dict) else fill_value 
                    for _ in range(target_length - current_length)])
    return lst

def pair_workers(left_workers, right_workers):
    """Efficiently pair workers from left and right lists."""
    return [{'left': l, 'right': r} for l, r in zip(left_workers, right_workers)]

@app.route('/')
def index():
    return render_template('actdoc.html')


@app.route('/generate_tabel', methods=['POST'])
def generate_tabel():
    doc = get_template("tabel.docx")
    act_date = request.form.get('actDate')
    # Format date to dd.MM.yyyy
    act_date = datetime.strptime(act_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    
    worker_names = request.form.getlist('worker_name[]')
    worker_hours = request.form.getlist('worker_hour[]')

    all_workers = [{'FullName': name, 'hour': hour} 
                   for name, hour in zip(worker_names, worker_hours) 
                   if name and hour]

    # Создаем структуру данных для табеля
    # Распределяем работников по массивам (по 20 в каждом)
    workers_top_left = pad_list(all_workers[0:20], 20)
    workers_top_right = pad_list(all_workers[20:40], 20)
    workers_bottom_left = pad_list(all_workers[40:60], 20)
    workers_bottom_right = pad_list(all_workers[60:80], 20)
    
    # Создаем пары работников для верхней и нижней части
    top_paired_workers = pair_workers(workers_top_left, workers_top_right)
    bottom_paired_workers = pair_workers(workers_bottom_left, workers_bottom_right)

    # Формируем контекст для шаблона
    context = {
        'actDate': act_date if act_date else '',
        'actNumber': request.form.get('actNumber') or '',
        'actBrigadir': request.form.get('actBrigadir') or '',
        'actDlina': request.form.get('actDlina') or '',
        'actWirina': request.form.get('actWirina') or '',
        'actHeight': request.form.get('actHeight') or '',
        'actSumma': request.form.get('actSumma') or '',
        'actV': request.form.get('actV') or '',
        'actMaster': request.form.get('actMaster') or '',
        'checkMontazh': '✓' if request.form.get('work_type_choice') == 'montaj' else ' ',
        'checkDeMontazh': '✓' if request.form.get('work_type_choice') == 'demontaj' else ' ',
        'workers_top': top_paired_workers,
        'workers_bottom': bottom_paired_workers
    }
    
    doc.render(context)
    
    # Создаем поток для сгенерированного файла
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)  # Переходим в начало потока
    
    return send_file(file_stream, as_attachment=True, download_name='generated_tabel.docx')


@app.route('/generate_actdoc', methods=['POST'])
def generate_actdoc():
    doc = get_template("docact.docx")
    act_date = request.form.get('actDate')
    # Format date to dd.MM.yyyy
    act_date = datetime.strptime(act_date, '%Y-%m-%d').strftime('%d.%m.%Y')

    worker_names = request.form.getlist('worker_name[]')
    worker_hours = request.form.getlist('worker_hour[]')

    all_workers = [{'FullName': name, 'hour': hour} 
                   for name, hour in zip(worker_names, worker_hours) 
                   if name and hour]

    total_workers = len(all_workers)

    # Split workers into four groups and pad to 16
    left_workers = pad_list(all_workers[0:16], 16)
    right_workers = pad_list(all_workers[16:32], 16)
    downleft_workers = pad_list(all_workers[32:48], 16)
    downright_workers = pad_list(all_workers[48:64], 16)

    # Create top and bottom pairs
    top_paired_workers = pair_workers(left_workers, right_workers)
    bottom_paired_workers = pair_workers(downleft_workers, downright_workers)
 
    # --- Логика для видов работ ---
    work_type_selection = request.form.get('workType')
    custom_work_text = ''

    if work_type_selection == 'другие':
        custom_work_text = request.form.get('otherWorkTypeInput') or ''
        selected_work_number = 20 # Обводить номер 20, если выбрано "другие"
    else:
        selected_work_number = WORK_TYPE_TO_NUMBER.get(work_type_selection)

    work_type_circles = {}
    for i in range(1, 21):
        if i == selected_work_number:
            rt = RichText()
            rt.add(CIRCLED_NUMBERS.get(i, str(i)), bold=True)
            work_type_circles[i] = rt
        else:
            work_type_circles[i] = str(i)
    # --------------------------------

    work_type_choice = request.form.get('work_type_choice')
    les_type = request.form.get('les_type')

    context = {
        'actDate': act_date if act_date else '',
        'actNumber': request.form.get('actNumber') or '',
        'actObject': request.form.get('actObject') or '',
        'actPosition': request.form.get('actPosition') or '',
        'actDlina': request.form.get('actDlina') or '',
        'actWirina': request.form.get('actWirina') or '',
        'actHeight': request.form.get('actHeight') or '',
        'actSumma': request.form.get('actSumma') or '',
        'actV': request.form.get('actV') or '',
        'actVem': request.form.get('actVem') or '',
        'actH': request.form.get('actH') or '',
        'actHour': request.form.get('actHour') or '',
        'actMaster': request.form.get('actMaster') or '',
        'actLes': request.form.get('actLes') or '',
        'actBrigadir': request.form.get('actBrigadir') or '',
        'workType': work_type_selection or '',
        'custom_work_type_text': custom_work_text or '',
        'work_type_circles': work_type_circles,
        'workers_top': top_paired_workers,
        'workers_bottom': bottom_paired_workers,
        'checkMontazh': '✓' if work_type_choice == 'montaj' else ' ',
        'checkDemontazh': '✓' if work_type_choice == 'demontaj' else ' ',
        'check_modifikaciya': '✓' if work_type_choice == 'modifikaciya' else ' ',
        'type11': '✓' if les_type == '1.1' else ' ',
        'type21': '✓' if les_type == '2.1' else ' ',
        'type4': '✓' if les_type == '4' else ' ',
        'type5': '✓',
        'wrkCount': total_workers,
    }

    doc.render(context)
    
    # Create a file-like stream for the generated docx
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0) # Go to the beginning of the stream

    return send_file(file_stream, as_attachment=True, download_name='generated_actdoc.docx')

if __name__ == '__main__':
    app.run(debug=True)