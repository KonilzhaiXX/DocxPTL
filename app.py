import io
from flask import Flask, render_template, request, send_file, session, redirect, url_for
from docxtpl import DocxTemplate, RichText
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "aaHdf@123456"  # Секретный ключ для сессий

users = {
    "erkebulan": "jkLdfvWE@234",
}

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
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template('actdoc.html', username=session["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("index"))

        error = "Неверный логин или пароль"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.clear()
    return redirect(url_for("login"))

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/generate_tabel', methods=['POST'])
def generate_tabel():
    if "username" not in session:
        return redirect(url_for("login"))
    doc = DocxTemplate("tabel.docx")
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

    # Создаем структуру данных для табеля
    workers_top_left = []
    workers_top_right = []
    workers_bottom_left = []
    workers_bottom_right = []
    
    # Распределяем работников по массивам (по 20 в каждом)
    for i, worker in enumerate(all_workers):
        if i < 20:
            workers_top_left.append(worker)
        elif i < 40:
            workers_top_right.append(worker)
        elif i < 60:
            workers_bottom_left.append(worker)
        elif i < 80:
            workers_bottom_right.append(worker)
    
    # Дополняем массивы пустыми значениями до 20 элементов
    while len(workers_top_left) < 20:
        workers_top_left.append({'FullName': '', 'hour': ''})
    while len(workers_top_right) < 20:
        workers_top_right.append({'FullName': '', 'hour': ''})
    while len(workers_bottom_left) < 20:
        workers_bottom_left.append({'FullName': '', 'hour': ''})
    while len(workers_bottom_right) < 20:
        workers_bottom_right.append({'FullName': '', 'hour': ''})
    
    # Создаем пары работников для верхней и нижней части
    top_paired_workers = []
    for i in range(20):
        top_paired_workers.append({
            'left': workers_top_left[i],
            'right': workers_top_right[i]
        })

    bottom_paired_workers = []
    for i in range(20):
        bottom_paired_workers.append({
            'left': workers_bottom_left[i],
            'right': workers_bottom_right[i]
        })

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
    if "username" not in session:
        return redirect(url_for("login"))
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
        'type5': '✓',
        'wrkCount': total_workers,
        'boss': request.form.get('boss') or ''
    }

    doc.render(context)
    
    # Create a file-like stream for the generated docx
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0) # Go to the beginning of the stream

    return send_file(file_stream, as_attachment=True, download_name='generated_actdoc.docx')

if __name__ == '__main__':
    app.run(debug=True)