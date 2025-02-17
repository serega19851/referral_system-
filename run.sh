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

echo "Проверка инициализации Alembic..."
if [ ! -d "alembic" ]; then
    echo "Alembic не инициализирован. Инициализирую..."
    alembic init alembic
fi

echo "Настройка alembic.ini..."
sed -i 's|^sqlalchemy.url =.*|sqlalchemy.url = sqlite:///./sqlite.db|' alembic.ini

echo "Редактирование alembic/env.py..."
sed -i 's|import sys|import sys\nimport os\nsys.path.append(os.getcwd())|' alembic/env.py
sed -i 's|# add your model.*|from database import Base\nfrom models import User, ReferralCode|' alembic/env.py
sed -i 's|target_metadata = .*|target_metadata = Base.metadata|' alembic/env.py


echo "Проверка папки версий Alembic..."
if [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
    echo "Создание первой миграции..."
    alembic revision --autogenerate -m "initial migration"
fi

echo "Применение миграций..."
alembic upgrade head

echo "Скрипт выполнен успешно."
echo "Запуск проекта..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

