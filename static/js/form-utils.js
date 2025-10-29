// Утилиты для работы с формой

function checkWorkType(value) {
    const otherWorkTypeDiv = document.getElementById('otherWorkType');
    const otherWorkTypeInput = document.getElementById('otherWorkTypeInput');
    if (value === 'другие') {
        otherWorkTypeDiv.style.opacity = '1';
    } else {
        otherWorkTypeDiv.style.opacity = '0';
        otherWorkTypeInput.value = ''; // Очищаем поле
    }
}

function handleCheckbox(checkbox) {
    const checkboxes = document.querySelectorAll('input[name="les_type"]');
    checkboxes.forEach((cb) => {
        if (cb !== checkbox) {
            cb.checked = false;
        }
    });
}

function addWorker() {
    const container = document.getElementById('workers-container');
    const newWorker = document.createElement('div');
    newWorker.className = 'worker-entry';
    const newIndex = container.children.length + 1;
    newWorker.innerHTML = `
        <span class="worker-index">${newIndex}.</span>
        <input type="text" name="worker_name[]" placeholder="ФИО работника" required onchange="updateBrigadir(this)">
        <input type="number" name="worker_hour[]" placeholder="Часы" required>
        <button type="button" class="remove-worker-btn" onclick="removeWorker(this)">Удалить</button>
    `;
    container.appendChild(newWorker);
    
    // Если это первый работник, автоматически заполняем поле бригадира
    if (newIndex === 1) {
        const brigadirField = document.getElementById('actBrigadir');
        if (brigadirField && brigadirField.value === '') {
            // Добавляем обработчик события для автозаполнения после ввода имени
            const nameInput = newWorker.querySelector('input[name="worker_name[]"]');
            nameInput.addEventListener('input', function() {
                if (this.value.trim() !== '') {
                    brigadirField.value = this.value;
                }
            });
        }
    }
}

// Функция для автоматического заполнения поля Бригадир
function updateBrigadir(input) {
    const brigadirField = document.getElementById('actBrigadir');
    // Если это первый работник в списке и поле ФИО заполнено
    const workerInputs = document.querySelectorAll('input[name="worker_name[]"]');
    if (workerInputs.length > 0 && workerInputs[0] === input && input.value.trim() !== '') {
        brigadirField.value = input.value;
    }
}

function removeWorker(button) {
    const workerEntry = button.parentElement;
    const allWorkers = document.querySelectorAll('.worker-entry');
    
    if (allWorkers.length > 1) {
        // Проверяем, является ли удаляемый работник первым
        const isFirstWorker = Array.from(allWorkers).indexOf(workerEntry) === 0;
        const workerName = workerEntry.querySelector('input[name="worker_name[]"]').value;
        const brigadirField = document.getElementById('actBrigadir');
        
        // Удаляем работника
        workerEntry.remove();
        updateWorkerIndexes();
        
        // Если удаляем первого работника и его имя совпадает с именем бригадира,
        // обновляем поле бригадира на имя нового первого работника
        if (isFirstWorker && brigadirField.value === workerName) {
            const newFirstWorker = document.querySelector('input[name="worker_name[]"]');
            if (newFirstWorker && newFirstWorker.value.trim() !== '') {
                brigadirField.value = newFirstWorker.value;
            }
        }
    } else {
        alert("Должен быть хотя бы один работник.");
    }
}

function updateWorkerIndexes() {
    const container = document.getElementById('workers-container');
    // Use Array.from for better performance and modern approach
    Array.from(container.children).forEach((worker, index) => {
        worker.querySelector('.worker-index').textContent = `${index + 1}.`;
    });
}

function clearAllWorkers() {
    if (confirm('Вы уверены, что хотите очистить весь состав бригады?')) {
        const container = document.getElementById('workers-container');
        // More efficient: clear all at once
        container.innerHTML = '';
    }
}

function addBulkWorkers() {
    const bulkText = document.getElementById('bulk-workers').value.trim();
    if (!bulkText) {
        alert('Пожалуйста, введите список работников');
        return;
    }
    
    const workerLines = bulkText.split('\n').filter(line => line.trim() !== '');
    const container = document.getElementById('workers-container');
    
    // Очищаем контейнер, если в нем есть работники
    container.innerHTML = '';
    
    // Если список не пустой, добавляем работников
    if (workerLines.length > 0) {
        // Use document fragment for better performance
        const fragment = document.createDocumentFragment();
        
        for (let i = 0; i < workerLines.length; i++) {
            const workerLine = workerLines[i].trim();
            if (workerLine) {
                // Находим все числа в строке
                const numbers = workerLine.match(/\d+/g) || [];
                let workerHours = 8; // По умолчанию 8 часов
                
                // Если есть числа, берем последнее
                if (numbers.length > 0) {
                    workerHours = parseInt(numbers[numbers.length - 1]);
                }
                
                // Удаляем все числа из строки для получения имени
                let workerName = workerLine.replace(/\d+/g, '').trim();
                // Удаляем лишние пробелы
                workerName = workerName.replace(/\s+/g, ' ');
                
                const newWorker = document.createElement('div');
                newWorker.className = 'worker-entry';
                const newIndex = i + 1;
                
                newWorker.innerHTML = `
                    <span class="worker-index">${newIndex}.</span>
                    <input type="text" name="worker_name[]" placeholder="ФИО работника" value="${workerName}" required onchange="updateBrigadir(this)">
                    <input type="number" name="worker_hour[]" placeholder="Часы" value="${workerHours}" required>
                    <button type="button" class="remove-worker-btn" onclick="removeWorker(this)">Удалить</button>
                `;
                
                fragment.appendChild(newWorker);
                
                // Автоматически заполняем поле бригадира, если это первый работник
                if (i === 0) {
                    const brigadirField = document.getElementById('actBrigadir');
                    if (brigadirField) {
                        brigadirField.value = workerName;
                    }
                }
            }
        }
        
        container.appendChild(fragment);
        
        // Очищаем поле ввода после добавления
        document.getElementById('bulk-workers').value = '';
    }
}

function formatNumber(num) {
    // Если число целое, возвращаем как есть
    if (Number.isInteger(num)) {
        return num.toString();
    }
    
    // Преобразуем число в строку с максимальной точностью
    let str = num.toString();
    
    // Если число не содержит десятичную точку, возвращаем как есть
    if (!str.includes('.')) {
        return str;
    }
    
    // Убираем нули в конце после десятичной точки
    // Но сохраняем все значащие цифры
    str = str.replace(/\.?0+$/, '');
    
    // Если после удаления нулей строка заканчивается точкой, убираем её
    if (str.endsWith('.')) {
        str = str.slice(0, -1);
    }
    
    return str;
}

function updateCalculations() {
    const type = document.querySelector('input[name="les_type"]:checked');
    const a = parseFloat(document.getElementById('actDlina').value) || 0;
    const b = parseFloat(document.getElementById('actWirina').value) || 0;
    const h = parseFloat(document.getElementById('actHeight').value) || 0;
    const v_field = document.getElementById('actV');
    const s_field = document.getElementById('actSumma');
    const vem_field = document.getElementById('actVem');

    v_field.value = '';
    s_field.value = '';
    vem_field.value = '';
    v_field.required = false;
    s_field.required = false;
    vem_field.required = false;

    if (!type) return;

    let result;
    if (type.value === '1.1') {
        result = a * b * h;
        v_field.value = formatNumber(result);
        v_field.required = true;
        vem_field.value = formatNumber(result);
    } else if (type.value === '2.1') {
        result = a * h;
        s_field.value = formatNumber(result);
        s_field.required = true;
        vem_field.value = formatNumber(result);
    } else if (type.value === '4') {
        result = a * b;
        s_field.value = formatNumber(result);
        s_field.required = true;
        vem_field.value = formatNumber(result);
    }
}
