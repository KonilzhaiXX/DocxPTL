import io
from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate, RichText
import os
from datetime import datetime

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('actdoc.html')


@app.route('/generate_actdoc', methods=['POST'])
def generate_actdoc():
    doc = DocxTemplate("docact.docx")
    act_date = request.form.get('actDate')
    # Format date to dd.MM.yyyy
    from datetime import datetime
    act_date = datetime.strptime(act_date, '%Y-%m-%d').strftime('%d.%m.%Y')

    worker_names = request.form.getlist('worker_name[]')
    worker_hours = request.form.getlist('worker_hour[]')

    all_workers = []
    for name, hour in zip(worker_names, worker_hours):
        if name and hour:
            all_workers.append({'FullName': name, 'hour': hour})

    total_workers = len(all_workers)

    # Split workers into four groups
    left_workers = all_workers[0:16]
    right_workers = all_workers[16:32]
    downleft_workers = all_workers[32:48]
    downright_workers = all_workers[48:64]

    # Pad each list to 16
    while len(left_workers) < 16:
        left_workers.append({'FullName': '', 'hour': ''})
    while len(right_workers) < 16:
        right_workers.append({'FullName': '', 'hour': ''})
    while len(downleft_workers) < 16:
        downleft_workers.append({'FullName': '', 'hour': ''})
    while len(downright_workers) < 16:
        downright_workers.append({'FullName': '', 'hour': ''})

    # Create top and bottom pairs
    top_paired_workers = []
    for l, r in zip(left_workers, right_workers):
        top_paired_workers.append({'left': l, 'right': r})

    bottom_paired_workers = []
    for dl, dr in zip(downleft_workers, downright_workers):
        bottom_paired_workers.append({'left': dl, 'right': dr})
 
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