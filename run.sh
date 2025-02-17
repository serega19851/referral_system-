#!/bin/bash

echo "Проверка виртуального окружения..."
if [ ! -d "venv" ]; then
    echo "Виртуальное окружение не найдено. Создаю..."
    python -m venv venv
fi

echo "Активация виртуального окружения..."
source venv/bin/activate

echo "Установка зависимостей..."
pip install --no-cache-dir -r requirements.txt

echo "Применение миграций..."
alembic upgrade head

echo "Запуск проекта..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

