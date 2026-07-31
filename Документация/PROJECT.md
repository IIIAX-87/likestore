# LikeStore — Копия интернет-магазина техники Apple

## Описание
Полнофункциональная копия интернет-магазина https://hm.lstore.ru с каталогом техники Apple и сопутствующих товаров.

**Источник данных:** https://hm.lstore.ru (Ханты-Мансийск)

## Архитектура

### Backend (Django REST Framework)
- Python 3.11+
- Django 5.x + Django REST Framework
- PostgreSQL
- Docker + Docker Compose
- JWT Authentication
- API Endpoints: /api/v1/

### Frontend (Next.js 14)
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- SSG + SSR для SEO
- React Server Components

### Parser (Playwright)
- Python + Playwright
- Асинхронный парсинг
- Сохранение в JSON

## Категории (11 шт.)
1. iPhone
2. Samsung
3. iPad
4. Watch
5. AirPods
6. MacBook
7. Приставки
8. Dyson
9. Аксессуары
10. Canon
11. TradeIn/Обмен

## SEO-фичи ✅

### Файлы
- ✅ `robots.txt` — инструкции для поисковых роботов
- ✅ `sitemap.xml` — карта сайта для индексации
- ✅ Canonical URLs — предотвращение дублирования страниц

### Meta tags
- ✅ Open Graph (Facebook, VK, Telegram)
- ✅ Twitter Cards
- ✅ Meta description, keywords, authors

### Schema.org (JSON-LD)
- ✅ Organization — информация о магазине
- ✅ Product — разметка товаров
- ✅ BreadcrumbList — хлебные крошки
- ✅ ItemList — списки товаров

### Технические
- ✅ SSR/SSG рендеринг
- ✅ Семантический HTML
- ✅ Адаптивный дизайн
- ✅ Yandex/Webmaster verification

## Функционал

### Фронтенд
- ✅ Каталог с фильтрацией
- ✅ Карточка товара
- ✅ Корзина (Zustand store)
- ✅ Оформление заказа
- ✅ Поиск
- ✅ Избранное
- 🔄 Фильтрация по ценам/брендам
- 🔄 Сортировка

### Backend
- ✅ Товары (CRUD)
- ✅ Категории
- ✅ Корзина (сессии/anonymous)
- ✅ Заказы
- ✅ Пользователи (JWT)
- ✅ Email восстановление

## Структура проекта
```
likestore/
├── backend/           # Django REST Framework
│   ├── config/       # Django settings
│   ├── products/      # Товары, категории
│   ├── orders/       # Заказы
│   ├── users/        # Пользователи
│   └── cart/         # Корзина
├── frontend/         # Next.js 14
│   ├── src/
│   │   ├── app/      # App Router
│   │   ├── components/
│   │   └── lib/      # API, store
│   ├── robots.ts      # robots.txt
│   └── sitemap.ts    # sitemap.xml
├── parser/           # Playwright парсер
│   └── src/
│       └── parser.py
└── docker-compose.yml
```

## Команды запуска

### Backend (Docker)
```bash
cd backend
docker-compose up -d
python manage.py migrate
```

### Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```

### Parser
```bash
cd parser
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python src/parser.py
```

### Docker (все сервисы)
```bash
docker-compose up -d
```

## Переменные окружения (backend)
```
DEBUG=False
SECRET_KEY=<generate-secure-key>
DATABASE_URL=postgres://likestore:pass@db:5432/likestore
REDIS_URL=redis://redis:6379/1
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Переменные окружения (frontend)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Статус проекта
🚧 В разработке

### Выполнено ✅
- [x] Backend DRF (Products, Orders, Users, Cart)
- [x] Frontend Next.js (SSR/SSG)
- [x] Docker конфигурация
- [x] SEO (robots.txt, sitemap.xml, Schema.org, OG tags)
- [x] Playwright парсер (собрано 60+ товаров)

### В процессе 🔄
- [ ] Интеграция парсера с БД
- [ ] Платежная система
- [ ] CI/CD

### Запланировано 📋
- [ ] Полный парсинг всех категорий
- [ ] Интеграция с Яндекс.Метрикой
- [ ] Push-уведомления
