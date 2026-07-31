# Parser for LikeStore

Парсер для сбора данных с сайта hm.lstore.ru

## Установка

```bash
cd parser
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
playwright install chromium
```

## Запуск

```bash
python src/parser.py
```

## Вывод

Результат сохраняется в `parsed_data.json` с товарами и категориями.
