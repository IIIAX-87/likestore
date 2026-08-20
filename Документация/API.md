# API LikeStore — Полная документация

## Базовый URL

```
http://localhost:8000/api/v1/
```

---

## Аутентификация

API поддерживает JWT-аутентификацию. Для авторизованных запросов добавьте заголовок:

```
Authorization: Bearer <access_token>
```

### Flow аутентификации

1. **Регистрация** → получение токенов
2. **Логин** → получение токенов
3. **Использование access_token** в заголовках
4. **Обновление** через `/auth/refresh/` когда истекает

---

## Products API

### GET /products/

Список всех товаров с пагинацией.

**Query Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `page` | int | Номер страницы (по умолчанию: 1) |
| `page_size` | int | Элементов на странице (по умолчанию: 20) |
| `category` | string | Slug категории |
| `brand` | string | Slug бренда |
| `min_price` | decimal | Минимальная цена |
| `max_price` | decimal | Максимальная цена |
| `search` | string | Поисковый запрос |
| `ordering` | string | Сортировка: `price`, `-price`, `name`, `-name`, `created_at`, `-created_at` |
| `is_featured` | bool | Только рекомендуемые |
| `is_bestseller` | bool | Только бестселлеры |
| `is_new` | bool | Только новинки |

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "iPhone 15 Pro Max",
      "slug": "iphone-15-pro-max",
      "article": "IP15PM256",
      "brand": {"id": 1, "name": "Apple", "slug": "apple"},
      "brand_name": "Apple",
      "category": {"id": 1, "name": "iPhone", "slug": "iphone"},
      "category_name": "iPhone",
      "description": "Полное описание товара...",
      "short_description": "Краткое описание",
      "price": "159990.00",
      "old_price": "179990.00",
      "discount_percent": 11,
      "stock": 15,
      "in_stock": true,
      "is_featured": true,
      "is_bestseller": true,
      "is_new": true,
      "main_image": "/media/products/iphone15.jpg",
      "images": [...],
      "specifications": [...],
      "variants": [...]
    }
  ]
}
```

### GET /products/{slug}/

Детали товара.

**Response:** Объект Product (без пагинации)

### GET /products/featured/

Рекомендуемые товары.

**Response:** Список Product (массив, не объект с pagination)

### GET /products/bestsellers/

Бестселлеры.

**Response:** Список Product

### GET /products/new/

Новинки.

**Response:** Список Product

### GET /products/search/?q={query}

Поиск товаров.

**Query Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `q` | string | Поисковый запрос (обязательно) |
| `page` | int | Страница |

### GET /products/{slug}/related/

Товары, связанные с данным.

**Response:** Список Product

---

## Categories API

### GET /products/categories/

Все категории (плоский список).

**Response:**
```json
[
  {"id": 1, "name": "iPhone", "slug": "iphone", "image": "/media/cat/iphone.jpg", "product_count": 25},
  {"id": 2, "name": "Samsung", "slug": "samsung", "image": "/media/cat/samsung.jpg", "product_count": 18}
]
```

### GET /products/categories/tree/

Иерархия категорий (древовидная структура).

**Response:**
```json
[
  {
    "id": 1,
    "name": "iPhone",
    "slug": "iphone",
    "image": "/media/cat/iphone.jpg",
    "product_count": 25,
    "children": [
      {"id": 5, "name": "iPhone 15", "slug": "iphone-15", "children": []},
      {"id": 6, "name": "iPhone 14", "slug": "iphone-14", "children": []}
    ]
  }
]
```

### GET /products/categories/{slug}/

Детали категории.

### GET /products/categories/{slug}/products/

Товары в категории (с фильтрами и пагинацией).

---

## Brands API

### GET /products/brands/

Все бренды.

### GET /products/brands/{slug}/

Детали бренда.

### GET /products/brands/{slug}/products/

Товары бренда.

---

## Cart API

### GET /cart/

Текущая корзина.

**Response:**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {...},
      "variant": {...},
      "variant_name": "256GB Space Gray",
      "quantity": 2,
      "price": "159990.00",
      "total": "319980.00"
    }
  ],
  "items_count": 2,
  "subtotal": "319980.00",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### POST /cart/add_item/

Добавить товар в корзину.

**Request:**
```json
{
  "product_id": 1,
  "variant_id": 5,
  "quantity": 1
}
```

**Response:** Обновлённая корзина

### POST /cart/update_item/

Изменить количество.

**Request:**
```json
{
  "item_id": 1,
  "quantity": 3
}
```

### POST /cart/remove_item/

Удалить товар.

**Request:**
```json
{
  "item_id": 1
}
```

### POST /cart/clear/

Очистить корзину.

---

## Wishlist API

### GET /cart/wishlist/

Список избранного.

**Response:**
```json
{
  "items": [
    {"id": 1, "product": {...}, "added_at": "2024-01-15T10:30:00Z"}
  ]
}
```

### POST /cart/wishlist/add/

Добавить в избранное.

**Request:**
```json
{
  "product_id": 1
}
```

### POST /cart/wishlist/remove/

Удалить из избранного.

**Request:**
```json
{
  "product_id": 1
}
```

---

## Orders API

### POST /orders/

Создать заказ.

**Request:**
```json
{
  "first_name": "Иван",
  "last_name": "Петров",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "city": "Москва",
  "address": "ул. Примерная, д. 1, кв. 10",
  "postal_code": "123456",
  "payment_method": "card",
  "delivery_type": "courier",
  "comment": "Позвонить перед доставкой"
}
```

**Варианты payment_method:**
- `card` — карта онлайн
- `cash` — наличными при получении
- `installment` — рассрочка

**Варианты delivery_type:**
- `pickup` — самовывоз
- `courier` — курьер
- `post` — почта
- `cdek` — СДЭК

### GET /orders/

Список заказов (требует авторизации).

### GET /orders/{id}/

Детали заказа.

### POST /orders/{id}/cancel/

Отменить заказ.

### GET /orders/by_email/?email={email}

Заказы по email (для гостей).

---

## Auth API

### POST /users/auth/register/

Регистрация нового пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "Иван",
  "last_name": "Петров",
  "phone": "+79001234567"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Петров"
  }
}
```

### POST /users/auth/login/

Вход.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Аналогично register

### POST /users/auth/logout/

Выход.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST /users/auth/refresh/

Обновить access token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST /users/auth/password_reset_request/

Запрос на сброс пароля.

**Request:**
```json
{
  "email": "user@example.com"
}
```

### POST /users/auth/password_reset_confirm/

Подтверждение сброса пароля.

**Request:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "newsecurepassword123"
}
```

---

## User Profile API

### GET /users/profile/

Профиль текущего пользователя.

**Requires:** Authorization header

### PATCH /users/profile/

Обновить профиль.

**Request:**
```json
{
  "first_name": "Иван",
  "last_name": "Петров",
  "phone": "+79001234567"
}
```

---

## Коды ошибок

| Код | Значение |
|-----|----------|
| 400 | Bad Request — неверные данные |
| 401 | Unauthorized — требуется авторизация |
| 403 | Forbidden — нет прав |
| 404 | Not Found — ресурс не найден |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |

**Формат ошибки:**
```json
{
  "detail": "Товар не найден",
  "code": "not_found"
}
```

---

## Rate Limiting

На данный момент не установлено.

---

## Версионирование

API использует версию в URL: `/api/v1/`

При изменениях создаётся новая версия: `/api/v2/`
