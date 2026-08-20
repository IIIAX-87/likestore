#!/bin/bash
# Скрипт для запуска парсинга товаров с hm.lstore.ru

cd "$(dirname "$0")"

echo "🕷️  Запуск парсера LikeStore..."
echo ""

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация venv
source venv/bin/activate

# Проверка зависимостей
if ! pip show playwright > /dev/null 2>&1; then
    echo "📥 Установка зависимостей..."
    pip install -r requirements.txt
    playwright install chromium
fi

# Запуск парсера
echo "🚀 Запуск парсинга..."
python src/parser.py

echo ""
echo "✅ Парсинг завершён!"
echo "📁 Файл с данными: src/parsed_data.json"
