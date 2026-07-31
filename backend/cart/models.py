"""
Cart app - models for shopping cart.
"""
from django.db import models
from products.models import Product, ProductVariant


class Cart(models.Model):
    """Shopping cart model."""
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name='User'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        indexes = [
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f'Cart {self.id}'

    @property
    def items_count(self):
        """Total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Cart subtotal."""
        return sum(item.total for item in self.items.all())


class CartItem(models.Model):
    """Cart item model."""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Cart'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Variant'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Price')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart item'
        verbose_name_plural = 'Cart items'
        unique_together = ['cart', 'product', 'variant']
        indexes = [
            models.Index(fields=['cart', 'product', 'variant']),
        ]

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    @property
    def total(self):
        """Item total."""
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """User wishlist."""
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='wishlists',
        verbose_name='User'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wishlist item'
        verbose_name_plural = 'Wishlist'
        unique_together = ['session_key', 'user', 'product']

    def __str__(self):
        return f'{self.product.name} in wishlist'
