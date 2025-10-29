// Система кэширования данных формы
const FormCache = {
    CACHE_KEY: 'actdoc_form_cache',
    CACHE_EXPIRY: 24 * 60 * 60 * 1000, // 24 часа в миллисекундах
    
    // Сохранение данных в localStorage
    saveFormData: function() {
        try {
            const formData = this.collectFormData();
            const cacheData = {
                data: formData,
                timestamp: Date.now()
            };
            localStorage.setItem(this.CACHE_KEY, JSON.stringify(cacheData));
            console.log('Данные формы сохранены в кэш');
        } catch (error) {
            console.error('Ошибка при сохранении данных в кэш:', error);
        }
    },
    
    // Загрузка данных из localStorage
    loadFormData: function() {
        try {
            const cachedData = localStorage.getItem(this.CACHE_KEY);
            if (!cachedData) return null;
            
            const parsedData = JSON.parse(cachedData);
            
            // Проверка срока действия кэша
            if (Date.now() - parsedData.timestamp > this.CACHE_EXPIRY) {
                this.clearCache();
                return null;
            }
            
            return parsedData.data;
        } catch (error) {
            console.error('Ошибка при загрузке данных из кэша:', error);
            return null;
        }
    },
    
    // Сбор данных из формы
    collectFormData: function() {
        const formData = {};
        
        // Основные поля формы
        const fields = [
            'actDate', 'actNumber', 'actObject', 'actPosition',
            'actDlina', 'actWirina', 'actHeight', 'actV', 'actSumma', 'actVem',
            'actHour', 'actMaster', 'actH', 'actLes', 'actBrigadir',
            'workType', 'otherWorkTypeInput'
        ];
        
        fields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                formData[fieldId] = element.value;
            }
        });
        
        // Радиокнопки для типа лесов
        const lesTypeRadio = document.querySelector('input[name="les_type"]:checked');
        if (lesTypeRadio) {
            formData.les_type = lesTypeRadio.value;
        }
        
        // Радиокнопки для вида работ
        const workTypeRadio = document.querySelector('input[name="work_type_choice"]:checked');
        if (workTypeRadio) {
            formData.work_type_choice = workTypeRadio.value;
        }
        
        // Состав бригады
        const workerNames = document.querySelectorAll('input[name="worker_name[]"]');
        const workerHours = document.querySelectorAll('input[name="worker_hour[]"]');
        const workers = [];
        
        for (let i = 0; i < workerNames.length; i++) {
            if (workerNames[i] && workerHours[i]) {
                workers.push({
                    name: workerNames[i].value,
                    hours: workerHours[i].value
                });
            }
        }
        formData.workers = workers;
        
        return formData;
    },
    
    // Восстановление данных в форму
    restoreFormData: function(data) {
        if (!data) return;
        
        try {
            // Восстановление основных полей
            const fields = [
                'actDate', 'actNumber', 'actObject', 'actPosition',
                'actDlina', 'actWirina', 'actHeight', 'actV', 'actSumma', 'actVem',
                'actHour', 'actMaster', 'actH', 'actLes', 'actBrigadir',
                'workType', 'otherWorkTypeInput'
            ];
            
            fields.forEach(fieldId => {
                const element = document.getElementById(fieldId);
                if (element && data[fieldId] !== undefined) {
                    element.value = data[fieldId];
                }
            });
            
            // Восстановление радиокнопок для типа лесов
            if (data.les_type) {
                const lesTypeRadio = document.querySelector(`input[name="les_type"][value="${data.les_type}"]`);
                if (lesTypeRadio) {
                    lesTypeRadio.checked = true;
                }
            }
            
            // Восстановление радиокнопок для вида работ
            if (data.work_type_choice) {
                const workTypeRadio = document.querySelector(`input[name="work_type_choice"][value="${data.work_type_choice}"]`);
                if (workTypeRadio) {
                    workTypeRadio.checked = true;
                }
            }
            
            // Восстановление состава бригады
            if (data.workers && data.workers.length > 0) {
                // Очищаем текущий состав бригады
                const container = document.getElementById('workers-container');
                container.innerHTML = '';
                
                // Добавляем работников из кэша
                data.workers.forEach((worker, index) => {
                    const workerDiv = document.createElement('div');
                    workerDiv.className = 'worker-entry';
                    workerDiv.innerHTML = `
                        <span class="worker-index">${index + 1}.</span>
                        <input type="text" name="worker_name[]" placeholder="ФИО работника" value="${worker.name || ''}" required>
                        <input type="number" name="worker_hour[]" placeholder="Часы" value="${worker.hours || ''}" required>
                        <button type="button" class="remove-worker-btn" onclick="removeWorker(this)">Удалить</button>
                    `;
                    container.appendChild(workerDiv);
                });
            }
            
            // Проверяем отображение поля "другие работы"
            if (data.workType === 'другие') {
                checkWorkType('другие');
            }
            
            // Обновляем расчеты
            updateCalculations();
            
            // Показываем уведомление о восстановлении данных
            this.showRestoreNotification();
            
            console.log('Данные формы восстановлены из кэша');
        } catch (error) {
            console.error('Ошибка при восстановлении данных из кэша:', error);
        }
    },
    
    // Очистка кэша
    clearCache: function() {
        try {
            localStorage.removeItem(this.CACHE_KEY);
            console.log('Кэш очищен');
        } catch (error) {
            console.error('Ошибка при очистке кэша:', error);
        }
    },
    
    // Показать уведомление о восстановлении данных
    showRestoreNotification: function() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #2ecc71;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span>✓</span>
                <span>Данные восстановлены из кэша</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; cursor: pointer; font-size: 16px; margin-left: auto;">×</button>
            </div>
        `;
        
        // Добавляем стили анимации
        if (!document.getElementById('cache-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'cache-notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        // Автоматически скрыть через 5 секунд
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    },
    
    // Инициализируем систему кэширования
    init: function() {
        // Восстанавливаем данные при загрузке страницы
        const cachedData = this.loadFormData();
        if (cachedData) {
            this.restoreFormData(cachedData);
        }
        
        // Добавляем автосохранение при изменении полей
        this.setupAutoSave();
        
        // Добавляем кнопку очистки кэша
        this.addClearCacheButton();
    },
    
    // Настройка автосохранения
    setupAutoSave: function() {
        const form = document.querySelector('form');
        if (!form) return;
        
        // Debounce функция для ограничения частоты сохранения
        let saveTimeout;
        const debouncedSave = () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                this.saveFormData();
            }, 1000); // Сохраняем через 1 секунду после последнего изменения
        };
        
        // Добавляем обработчики событий для всех полей формы
        form.addEventListener('input', debouncedSave);
        form.addEventListener('change', debouncedSave);
        
        // Специальный обработчик для динамически добавляемых работников
        const workersContainer = document.getElementById('workers-container');
        if (workersContainer) {
            const observer = new MutationObserver(debouncedSave);
            observer.observe(workersContainer, { childList: true, subtree: true });
        }
    },
    
    // Добавление кнопки очистки кэша
    addClearCacheButton: function() {
        const container = document.querySelector('.container');
        if (!container) return;
        
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.innerHTML = '🗑️ Очистить сохраненные данные';
        clearButton.style.cssText = `
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            transition: background-color 0.3s;
        `;
        
        clearButton.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#c0392b';
        });
        
        clearButton.addEventListener('mouseout', function() {
            this.style.backgroundColor = '#e74c3c';
        });
        
        clearButton.addEventListener('click', () => {
            if (confirm('Вы уверены, что хотите очистить все сохраненные данные?')) {
                this.clearCache();
                location.reload(); // Перезагружаем страницу для очистки формы
            }
        });
        
        // Вставляем кнопку перед формой
        const form = document.querySelector('form');
        if (form) {
            container.insertBefore(clearButton, form);
        }
    }
};
