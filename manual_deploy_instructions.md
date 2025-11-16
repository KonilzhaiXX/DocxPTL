# Инструкции для выкладки изменений на сервере

## Шаг 1: Подключение к серверу
```bash
ssh root@46.19.65.232
```

## Шаг 2: Переход в директорию проекта
```bash
cd /var/www/act
```

## Шаг 3: Обновление кода из Git
```bash
git pull origin main
```

## Шаг 4: Выполнение автоматической выкладки
```bash
chmod +x deploy.sh
./deploy.sh
```

## Альтернативный способ (пошагово):

### 1. Остановка старых процессов Gunicorn
```bash
pkill -f gunicorn
```

### 2. Активация виртуального окружения
```bash
source venv/bin/activate
```

### 3. Обновление зависимостей (если нужно)
```bash
pip install -r requirements.txt
```

### 4. Запуск нового Gunicorn
```bash
gunicorn --bind 127.0.0.1:5000 --workers 3 --daemon app:app
```

### 5. Проверка запуска
```bash
ps aux | grep gunicorn
```

### 6. Перезагрузка Nginx
```bash
systemctl reload nginx
```

## Проверка работы приложения
После выкладки проверьте работу приложения по адресу: http://46.19.65.232

## Быстрая команда для будущих выкладок
После первой настройки можно использовать одну команду:
```bash
ssh root@46.19.65.232 "cd /var/www/act && git pull origin main && ./deploy.sh"
```