# LikeStore — Интернет-магазин техники Apple

## Описание проекта

**LikeStore** — полнофункциональный интернет-магазин техники Apple и сопутствующих товаров. Копия интернет-магазина https://hm.lstore.ru (г. Ханты-Мансийск).

---

## Архитектура проекта

```
likestore/
├── backend/           # Django REST Framework API
├── frontend/          # Next.js 14 веб-приложение
├── parser/            # Playwright парсер товаров
├── docs/              # Дополнительная документация
├── Документация/      # Основная документация проекта
└── docker-compose.yml # Docker-конфигурация для всех сервисов
```

---

## Стек технологий

### Backend
| Компонент | Технология | Версия |
|-----------|------------|--------|
| Framework | Django + DRF | 5.x |
| Язык | Python | 3.11+ |
| База данных | PostgreSQL | 15 |
| Кэширование | Redis | 7 |
| Асинхронные задачи | Celery | 5.3 |
| Аутентификация | JWT (SimpleJWT) | 5.3 |
| WSGI-сервер | Gunicorn | 21+ |

### Frontend
| Компонент | Технология | Версия |
|-----------|------------|--------|
| Framework | Next.js | 14+ |
| Язык | TypeScript | 5.x |
| Стилизация | Tailwind CSS | 3.x |
| Состояние | Zustand | 4.x |
| State persistence | localStorage |

### Parser
| Компонент | Технология |
|-----------|------------|
| Framework | Playwright |
| Язык | Python |

---

## Структура Backend (`/backend`)

```
backend/
├── config/              # Django настройки
│   ├── __init__.py
│   ├── settings.py      # Основные настройки
│   ├── urls.py          # Главные URL
│   ├── wsgi.py          # WSGI application
│   └── asgi.py          # ASGI application
├── products/            # Приложение товаров
│   ├── models.py        # Product, Category, Brand
│   ├── serializers.py   # DRF serializers
│   ├── views.py        # ViewSets
│   └── urls.py
├── orders/              # Приложение заказов
│   ├── models.py        # Order, OrderItem
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── users/               # Приложение пользователей
│   ├── models.py        # Custom User model
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── cart/                # Корзина и wishlist
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── static/              # Статические файлы
├── media/               # Загруженные медиафайлы
├── requirements.txt     # Python зависимости
├── Dockerfile
├── manage.py
└── db.sqlite3           # Локальная БД (dev)
```

### Django Apps

#### Products App
- `Product` — товары с вариациями
- `Category` — категории с иерархией
- `Brand` — бренды
- `ProductImage` — изображения товаров
- `ProductSpecification` — характеристики

#### Orders App
- `Order` — заказы
- `OrderItem` — позиции заказа

#### Users App
- `User` — кастомная модель пользователя
- `Address` — адреса доставки

#### Cart App
- `Cart` — корзина
- `CartItem` — позиции корзины
- `WishlistItem` — избранное

---

## Структура Frontend (`/frontend`)

```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # Корневой layout
│   │   ├── page.tsx      # Главная страница
│   │   ├── globals.css   # Глобальные стили
│   │   ├── catalog/      # Страницы каталога
│   │   ├── product/      # Страницы товаров
│   │   └── checkout/     # Оформление заказа
│   ├── components/       # React компоненты
│   │   ├── layout/       # Header, Footer, etc.
│   │   ├── product/      # ProductCard, etc.
│   │   ├── cart/         # CartWidget, etc.
│   │   └── ui/           # UI-kit
│   └── lib/              # Утилиты
│       ├── api.ts        # API клиент
│       ├── store.ts      # Zustand stores
│       └── utils.ts      # Утилиты
├── public/               # Статические файлы
├── package.json
├── next.config.ts
├── tailwind.config.ts
└── Dockerfile
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1/
```

### Products API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/products/` | Список товаров (пагинация, фильтры) |
| GET | `/products/{slug}/` | Детали товара |
| GET | `/products/featured/` | Рекомендуемые товары |
| GET | `/products/bestsellers/` | Бестселлеры |
| GET | `/products/new/` | Новинки |
| GET | `/products/search/?q=` | Поиск |
| GET | `/products/{slug}/related/` | Связанные товары |

**Query Parameters:**
- `page` — номер страницы
- `page_size` — размер страницы
- `category` — slug категории
- `brand` — slug бренда
- `min_price` / `max_price` — ценовой диапазон
- `search` — поиск по названию
- `ordering` — сортировка (`price`, `-price`, `name`, `-name`)

### Categories API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/products/categories/` | Все категории |
| GET | `/products/categories/tree/` | Иерархия категорий |
| GET | `/products/categories/{slug}/` | Детали категории |
| GET | `/products/categories/{slug}/products/` | Товары категории |

### Brands API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/products/brands/` | Все бренды |
| GET | `/products/brands/{slug}/` | Детали бренда |
| GET | `/products/brands/{slug}/products/` | Товары бренда |

### Cart API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/cart/` | Получить корзину |
| POST | `/cart/add_item/` | Добавить товар |
| POST | `/cart/update_item/` | Изменить количество |
| POST | `/cart/remove_item/` | Удалить товар |
| POST | `/cart/clear/` | Очистить корзину |

**Add Item Request:**
```json
{
  "product_id": 123,
  "variant_id": 456,  // optional
  "quantity": 1
}
```

### Wishlist API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/cart/wishlist/` | Список избранного |
| POST | `/cart/wishlist/add/` | Добавить в избранное |
| POST | `/cart/wishlist/remove/` | Удалить из избранного |

### Orders API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/orders/` | Список заказов (авторизованный) |
| POST | `/orders/` | Создать заказ |
| GET | `/orders/{id}/` | Детали заказа |
| POST | `/orders/{id}/cancel/` | Отменить заказ |
| GET | `/orders/by_email/?email=` | Заказы по email |

**Create Order Request:**
```json
{
  "first_name": "Иван",
  "last_name": "Петров",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "city": "Москва",
  "address": "ул. Примерная, д. 1",
  "postal_code": "123456",
  "payment_method": "card",
  "delivery_type": "courier",
  "comment": "Позвонить перед доставкой"
}
```

### Auth API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/users/auth/register/` | Регистрация |
| POST | `/users/auth/login/` | Вход |
| POST | `/users/auth/logout/` | Выход |
| POST | `/users/auth/refresh/` | Обновить токен |
| POST | `/users/auth/password_reset_request/` | Запрос сброса пароля |
| POST | `/users/auth/password_reset_confirm/` | Подтверждение сброса |

---

## Категории товаров (11)

1. iPhone — смартфоны Apple
2. Samsung — смартфоны Samsung
3. iPad — планшеты Apple
4. Watch — умные часы
5. AirPods — наушники
6. MacBook — ноутбуки Apple
7. Приставки — игровые консоли
8. Dyson — пылесосы и техника
9. Аксессуары — чехлы, зарядки и т.д.
10. Canon — фотоаппараты
11. TradeIn — обмен старой техники

---

## SEO-возможности

### Файлы
- ✅ `robots.txt` — инструкции для поисковых роботов
- ✅ `sitemap.xml` — карта сайта
- ✅ Canonical URLs — предотвращение дублирования

### Meta Tags
- ✅ Open Graph (Facebook, VK, Telegram)
- ✅ Twitter Cards
- ✅ Meta description, keywords, authors
- ✅ Yandex/Webmaster verification

### Schema.org (JSON-LD)
- ✅ Organization — информация о магазине
- ✅ Product — разметка товаров
- ✅ BreadcrumbList — хлебные крошки
- ✅ ItemList — списки товаров

### Технические
- ✅ SSR/SSG рендеринг
- ✅ Семантический HTML
- ✅ Адаптивный дизайн

---

## Переменные окружения

### Backend (`.env`)

```env
# Безопасность
DEBUG=False
SECRET_KEY=your-secure-secret-key-here

# База данных
DATABASE_URL=postgres://likestore:password@db:5432/likestore
# Или отдельно:
POSTGRES_DB=likestore
POSTGRES_USER=likestore
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1,host.docker.internal
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Celery
CELERY_BROKER_URL=redis://redis:6379/0

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Команды запуска

### Docker (рекомендуется)

```bash
# Все сервисы
docker-compose up -d

# С конкретным сервисом
docker-compose up -d backend
docker-compose up -d frontend

# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f frontend

# Остановка
docker-compose down
```

### Backend отдельно

```bash
cd backend

# Установка зависимостей
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Запуск сервера разработки
python manage.py runserver 0.0.0.0:8000

# Или с Gunicorn
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
```

### Frontend отдельно

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev

# Сборка для продакшена
npm run build

# Линтинг
npm run lint
```

### Parser

```bash
cd parser

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Установка Playwright
playwright install chromium

# Запуск парсера
python src/parser.py
```

---

## Docker-сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| `db` | 5432 | PostgreSQL 15 |
| `redis` | 6379 | Redis 7 |
| `backend` | 8000 | Django + Gunicorn |
| `celery` | — | Celery worker (опционально) |
| `frontend` | 3000 | Next.js |

---

## Состояние проекта

### ✅ Выполнено

- [x] Django REST Framework API (Products, Orders, Users, Cart)
- [x] Next.js 14 Frontend (SSR/SSG)
- [x] Docker + Docker Compose конфигурация
- [x] SEO (robots.txt, sitemap.xml, Schema.org, OG tags)
- [x] Playwright парсер (60+ товаров)
- [x] JWT аутентификация
- [x] Zustand store для корзины и избранного
- [x] Фильтрация и поиск товаров

### 🔄 В процессе

- [ ] Интеграция парсера с БД
- [ ] Платежная система

### 📋 Запланировано

- [ ] Полный парсинг всех категорий
- [ ] Интеграция с Яндекс.Метрикой
- [ ] Push-уведомления
- [ ] CI/CD

---

## Разработка

### Полезные команды Django

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Загрузка данных
python manage.py loaddata fixtures.json

# Сбор статики
python manage.py collectstatic
```

### Полезные команды Celery

```bash
# Запуск worker
celery -A config worker -l info

# Запуск beat (scheduler)
celery -A config beat -l info

# Запуск flower (мониторинг)
celery -A config flower
```

---

## Лицензия

Проект создан в образовательных целях.
