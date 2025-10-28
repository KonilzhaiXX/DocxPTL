#!/bin/bash

# Скрипт для автоматической выкладки изменений
echo "=== Начинаем выкладку изменений ==="

# Переходим в директорию проекта
cd /var/www/act

# Обновляем код из git (если используется)
echo "Обновляем код из репозитория..."
git pull origin main 2>/dev/null || echo "Git pull пропущен (возможно, не настроен)"

# Активируем виртуальное окружение
echo "Активируем виртуальное окружение..."
source venv/bin/activate

# Обновляем зависимости (если нужно)
echo "Проверяем зависимости..."
pip install -r requirements.txt --quiet

# Останавливаем старые процессы Gunicorn
echo "Останавливаем старые процессы Gunicorn..."
pkill -f gunicorn || echo "Процессы Gunicorn не найдены"

# Ждем немного для корректного завершения процессов
sleep 2

# Запускаем новые процессы Gunicorn
echo "Запускаем Gunicorn..."
gunicorn --bind 127.0.0.1:5000 --workers 3 --daemon app:app

# Проверяем, что процессы запустились
sleep 2
if pgrep -f gunicorn > /dev/null; then
    echo "✅ Gunicorn успешно запущен"
    echo "Количество процессов: $(pgrep -f gunicorn | wc -l)"
else
    echo "❌ Ошибка запуска Gunicorn"
    exit 1
fi

# Перезагружаем Nginx (если нужно)
echo "Перезагружаем Nginx..."
systemctl reload nginx

echo "=== Выкладка завершена успешно! ==="
echo "Приложение доступно по адресу: http://46.19.65.232"