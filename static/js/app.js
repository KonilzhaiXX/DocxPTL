// Главный файл приложения

document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем систему кэширования
    FormCache.init();
    
    const form = document.querySelector('form');
    const spinnerOverlay = document.getElementById('spinner-overlay');
    
    // Обработчик для кнопки "Сгенерировать табель"
    const generateTabelBtn = document.getElementById('generate-tabel-btn');
    generateTabelBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Показываем спиннер загрузки
        spinnerOverlay.style.display = 'flex';
        
        // Собираем данные формы
        const formData = new FormData(form);
        
        // Отправляем запрос на сервер
        fetch('/generate_tabel', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при генерации табеля');
            }
            return response.blob();
        })
        .then(blob => {
            // Создаем ссылку для скачивания файла
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'generated_tabel.docx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            // Скрываем спиннер загрузки
            spinnerOverlay.style.display = 'none';
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при генерации табеля: ' + error.message);
            spinnerOverlay.style.display = 'none';
        });
    });
    

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        spinnerOverlay.style.display = 'flex';

        const formData = new FormData(form);

        fetch('/generate_actdoc', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети или сервера');
            }
            const disposition = response.headers.get('Content-Disposition');
            let filename = 'act.docx';
            if (disposition && disposition.includes('attachment')) {
                const filenameMatch = disposition.match(/filename="(.+?)"/);
                if (filenameMatch && filenameMatch.length > 1) {
                    filename = filenameMatch[1];
                }
            }
            return response.blob().then(blob => ({ blob, filename }));
        })
        .then(({ blob, filename }) => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            spinnerOverlay.style.display = 'none';
        })
        .catch(error => {
            console.error('Ошибка при генерации документа:', error);
            spinnerOverlay.style.display = 'none';
            alert('Не удалось сгенерировать документ. Пожалуйста, проверьте консоль для получения дополнительной информации.');
        });
    });
});
