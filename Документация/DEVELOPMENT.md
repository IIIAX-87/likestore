# Руководство разработчика LikeStore

## Начало работы

### Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15 (или Docker)
- Redis 7 (или Docker)
- Git

### Клонирование репозитория

```bash
git clone <repository-url>
cd likestore
```

### Быстрый старт (Docker)

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### Ручная установка

#### Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env

# Миграции
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск
python manage.py runserver
```

#### Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Настройка переменных окружения
cp .env.local.example .env.local
# Отредактируйте .env.local

# Запуск dev-сервера
npm run dev
```

---

## Структура кода

### Backend (Django)

```
backend/
├── config/                 # Конфигурация Django
│   ├── settings.py         # Основные настройки
│   ├── urls.py             # Главные маршруты
│   └── wsgi.py / asgi.py   # WSGI/ASGI приложения
├── products/               # Товары
│   ├── models.py           # Product, Category, Brand
│   ├── serializers.py      # DRF serializers
│   ├── views.py           # ViewSets
│   ├── filters.py         # Django-filter
│   ├── pagination.py       # Пагинация
│   └── urls.py
├── orders/                # Заказы
├── users/                 # Пользователи
├── cart/                  # Корзина
└── manage.py
```

### Frontend (Next.js)

```
frontend/src/
├── app/                   # App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── catalog/
│   │   ├── page.tsx       # Catalog listing
│   │   └── [category]/
│   │       └── page.tsx   # Category page
│   ├── product/
│   │   └── [slug]/
│   │       └── page.tsx   # Product detail
│   └── checkout/
│       └── page.tsx       # Checkout page
├── components/            # React компоненты
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Navigation.tsx
│   ├── product/
│   │   ├── ProductCard.tsx
│   │   ├── ProductGrid.tsx
│   │   └── ProductImage.tsx
│   ├── cart/
│   │   ├── CartWidget.tsx
│   │   ├── CartDrawer.tsx
│   │   └── CartItem.tsx
│   └── ui/                # UI-kit
│       ├── Button.tsx
│       ├── Input.tsx
│       └── ...
└── lib/
    ├── api.ts            # API клиент
    ├── store.ts          # Zustand stores
    └── utils.ts          # Утилиты
```

---

## Работа с базой данных

### Создание миграций

```bash
cd backend
python manage.py makemigrations
```

### Применение миграций

```bash
python manage.py migrate
```

### Миграция для существующей БД

```bash
# Создание миграций без применения
python manage.py makemigrations --empty

# Или для initial миграции
python manage.py migrate --fake-initial
```

### Заполнение тестовыми данными

```bash
python manage.py loaddata fixtures/products.json
```

### Django Admin

http://localhost:8000/admin/

---

## API-разработка

### Добавление нового endpoint

#### 1. serializers.py

```python
from rest_framework import serializers
from .models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
```

#### 2. views.py

```python
from rest_framework import viewsets
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

#### 3. urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyModelViewSet

router = DefaultRouter()
router.register(r'my-models', MyModelViewSet, basename='mymodel')

urlpatterns = [
    path('', include(router.urls)),
]
```

#### 4. Подключение в config/urls.py

```python
path('api/v1/my-app/', include('my_app.urls')),
```

---

## Frontend-разработка

### Добавление новой страницы

```bash
# src/app/products/page.tsx
export default function ProductsPage() {
  return <h1>Товары</h1>
}
```

### Добавление компонента

```bash
# src/components/product/ProductCard.tsx
interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p>{product.price}</p>
    </div>
  )
}
```

### Использование API

```typescript
// В компоненте
import { productsAPI } from '@/lib/api';

async function loadProducts() {
  const data = await productsAPI.list({ category: 'iphone' });
  console.log(data.results);
}
```

### Zustand Store

```typescript
// В store.ts
interface MyState {
  items: Item[];
  addItem: (item: Item) => void;
}

// В компоненте
import { useMyStore } from '@/lib/store';

export function MyComponent() {
  const { items, addItem } = useMyStore();
  // ...
}
```

---

## Тестирование

### Backend

```bash
cd backend

# Запуск всех тестов
python manage.py test

# Тест конкретного приложения
python manage.py test products

# С покрытием
coverage run manage.py test
coverage report
```

### Frontend

```bash
cd frontend

# Запуск тестов
npm test

# Запуск с watch
npm run test:watch

# С покрытием
npm run test:coverage
```

---

## Код-стайл

### Backend (Python)

```bash
# Flake8
flake8 .

# Black formatter
black .

# isort
isort .
```

### Frontend (TypeScript/JS)

```bash
cd frontend

# ESLint
npm run lint

# Prettier check
npx prettier --check .

# Prettier fix
npx prettier --write .
```

---

## Полезные команды

### Git

```bash
# Создание ветки
git checkout -b feature/my-feature

# Коммит
git add .
git commit -m "feat: add my feature"

# Push
git push origin feature/my-feature
```

### Docker

```bash
# Пересборка образа
docker-compose build backend

# Restart сервиса
docker-compose restart backend

# Очистка volumes
docker-compose down -v

# Вход в контейнер
docker-compose exec backend bash
docker-compose exec db psql -U likestore
```

### Celery

```bash
# Запуск worker
celery -A config worker -l info

# Запуск beat
celery -A config beat -l info

# Мониторинг (flower)
celery -A config flower
```

---

## Отладка

### Django

```python
# settings.py - включить отладку
DEBUG = True

# Логи в views.py
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug(f"Request data: {request.data}")
```

### Next.js

```typescript
// console.log в серверных компонентах виден в терминале
// console.log в клиентских - в браузере

// Отладка в браузере
debugger;
```

---

## Деплой

### Docker Deploy

```bash
# Сборка production образов
docker-compose -f docker-compose.prod.yml build

# Запуск
docker-compose -f docker-compose.prod.yml up -d
```

### Переменные для прода

```env
DEBUG=False
ALLOWED_HOSTS=likestore.ru,www.likestore.ru
DATABASE_URL=postgres://user:pass@dbhost:5432/likestore
SECRET_KEY=<сгенерированный>
```

---

## Troubleshooting

### Проблемы с миграциями

```bash
# Сброс миграций
python manage.py migrate --fake products zero
python manage.py makemigrations products
python manage.py migrate products
```

### Проблемы с node_modules

```bash
rm -rf node_modules package-lock.json
npm install
```

### Проблемы с Docker

```bash
# Очистка всех данных
docker-compose down -v --rmi all
docker system prune -a
```
