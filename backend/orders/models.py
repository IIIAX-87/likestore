"""
Orders app - models for orders and related entities.
"""
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product


User = get_user_model()


class Order(models.Model):
    """Order model."""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждён'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличными при получении'),
        ('card', 'Картой при получении'),
        ('online', 'Онлайн оплата'),
    ]

    DELIVERY_TYPE_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('courier', 'Курьер'),
        ('cdek', 'СДЭК'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Пользователь'
    )

    # Contact info
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    # Address
    city = models.CharField(max_length=200, blank=True, verbose_name='Город')
    address = models.TextField(blank=True, verbose_name='Адрес')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='Почтовый индекс')

    # Order details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        verbose_name='Способ оплаты'
    )
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        default='pickup',
        verbose_name='Тип доставки'
    )

    # Totals
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Подытог'
    )
    delivery_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Стоимость доставки'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Итого'
    )
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Скидка'
    )

    # Notes
    comment = models.TextField(blank=True, verbose_name='Комментарий к заказу')
    admin_comment = models.TextField(blank=True, verbose_name='Комментарий администратора')

    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='Трек-номер')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Подтверждён')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='Отправлен')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Доставлен')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'Заказ #{self.id}'

    def calculate_totals(self):
        """Calculate order totals from items."""
        self.subtotal = sum(item.total for item in self.items.all())
        self.total = self.subtotal + self.delivery_cost - self.discount
        self.save()


class OrderItem(models.Model):
    """Order item model."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Товар'
    )
    product_name = models.CharField(max_length=500, verbose_name='Название товара')
    product_sku = models.CharField(max_length=100, blank=True, verbose_name='Артикул')
    variant_name = models.CharField(max_length=255, blank=True, verbose_name='Вариант')

    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Итого')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Order status change history."""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Заказ'
    )
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, verbose_name='Статус')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Кем изменён'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        verbose_name = 'История статусов'
        verbose_name_plural = 'Истории статусов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order} - {self.status}'
