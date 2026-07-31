"""
Products app - models for catalog items.
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Product category."""
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent category')
    )
    description = models.TextField(blank=True, verbose_name=_('Description'))
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name=_('Image'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_('Meta title'))
    meta_description = models.TextField(blank=True, verbose_name=_('Meta description'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """Product brand/manufacturer."""
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'))
    logo = models.ImageField(upload_to='brands/', null=True, blank=True, verbose_name=_('Logo'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    website = models.URLField(blank=True, verbose_name=_('Website'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model."""
    name = models.CharField(max_length=500, verbose_name=_('Name'))
    slug = models.SlugField(max_length=500, verbose_name=_('Slug'))
    article = models.CharField(max_length=100, blank=True, verbose_name=_('Article'))
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Brand')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name=_('Category')
    )
    description = models.TextField(blank=True, verbose_name=_('Description'))
    short_description = models.TextField(max_length=500, blank=True, verbose_name=_('Short description'))
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Price'))
    old_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Old price')
    )
    stock = models.PositiveIntegerField(default=0, verbose_name=_('Stock'))
    sku = models.CharField(max_length=100, blank=True, verbose_name=_('SKU'))
    barcode = models.CharField(max_length=100, blank=True, verbose_name=_('Barcode'))
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name=_('Weight'))
    dimensions = models.CharField(max_length=100, blank=True, verbose_name=_('Dimensions'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is featured'))
    is_bestseller = models.BooleanField(default=False, verbose_name=_('Is bestseller'))
    is_new = models.BooleanField(default=False, verbose_name=_('Is new'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_('Meta title'))
    meta_description = models.TextField(blank=True, verbose_name=_('Meta description'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['price']),
            models.Index(fields=['article']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        """Calculate discount percentage."""
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    @property
    def in_stock(self):
        """Check if product is in stock."""
        return self.stock > 0


class ProductImage(models.Model):
    """Product image."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Product')
    )
    image = models.ImageField(upload_to='products/', verbose_name=_('Image'))
    alt_text = models.CharField(max_length=255, blank=True, verbose_name=_('Alt text'))
    is_main = models.BooleanField(default=False, verbose_name=_('Is main image'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))

    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.id}"


class ProductSpecification(models.Model):
    """Product specification/characteristic."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name=_('Product')
    )
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    value = models.CharField(max_length=500, verbose_name=_('Value'))

    class Meta:
        verbose_name = _('Specification')
        verbose_name_plural = _('Specifications')

    def __str__(self):
        return f"{self.name}: {self.value}"


class ProductVariant(models.Model):
    """Product variant (size, color, etc.)."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('Product')
    )
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    sku = models.CharField(max_length=100, blank=True, verbose_name=_('SKU'))
    price_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Price modifier')
    )
    stock = models.PositiveIntegerField(default=0, verbose_name=_('Stock'))
    attributes = models.JSONField(default=dict, blank=True, verbose_name=_('Attributes'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    class Meta:
        verbose_name = _('Product variant')
        verbose_name_plural = _('Product variants')

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def final_price(self):
        """Calculate final price with modifier."""
        return self.product.price + self.price_modifier
