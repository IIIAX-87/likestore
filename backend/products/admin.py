"""
Admin configuration for Products app.
"""
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Category, Brand, Product, ProductImage, ProductSpecification, ProductVariant
import os
import json


# ============================================
# Inlines
# ============================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'image_url', 'alt_text', 'is_main', 'order']


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


# ============================================
# Admins
# ============================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'order', 'product_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Товаров'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Товаров'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'stock', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'is_bestseller', 'is_new', 'category', 'brand']
    search_fields = ['name', 'article', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline, ProductVariantInline]
    list_editable = ['price', 'stock', 'is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'article', 'sku')
        }),
        ('Связи', {
            'fields': ('brand', 'category')
        }),
        ('Цены', {
            'fields': ('price', 'old_price')
        }),
        ('Описание', {
            'fields': ('description', 'short_description')
        }),
        ('Наличие', {
            'fields': ('stock', 'barcode', 'weight', 'dimensions')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_featured', 'is_bestseller', 'is_new')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Системное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_main', 'order']
    list_filter = ['is_main']
    search_fields = ['product__name']


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'value']
    search_fields = ['name', 'value']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'sku', 'stock', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'sku']


# ============================================
# Parser Integration View
# ============================================

def run_parser_view(request):
    """
    View для загрузки данных из JSON файла в базу.
    Парсинг выполняется отдельно через parser/src/parser.py
    """
    from django.core.management import call_command
    
    # Путь к JSON файлу
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    likestore_dir = os.path.dirname(backend_dir)
    json_path = os.path.join(likestore_dir, 'parser', 'src', 'parsed_data.json')
    
    context = {
        'title': 'Импорт товаров',
        'parser_template': True,
        'json_path': json_path,
    }
    
    # Статистика базы
    context['stats'] = {
        'categories': Category.objects.count(),
        'brands': Brand.objects.count(),
        'products': Product.objects.count(),
    }
    
    # Проверка файла
    context['json_exists'] = os.path.exists(json_path)
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                context['json_stats'] = {
                    'products': len(data.get('products', [])),
                    'categories': len(data.get('categories', [])),
                }
        except Exception as e:
            context['json_error'] = str(e)
            context['json_stats'] = None
    else:
        context['json_stats'] = None
    
    # Обработка POST
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'load_data':
            if not os.path.exists(json_path):
                messages.error(request, f'Файл не найден: {json_path}')
            else:
                try:
                    call_command('load_products', '--file=' + json_path, verbosity=2)
                    messages.success(request, '✅ Данные загружены успешно!')
                    return redirect('admin:products_product_changelist')
                except Exception as e:
                    messages.error(request, f'Ошибка загрузки: {e}')
        
        elif action == 'clear_and_load':
            if not os.path.exists(json_path):
                messages.error(request, f'Файл не найден: {json_path}')
            else:
                try:
                    call_command('load_products', '--file=' + json_path, '--clear', verbosity=2)
                    messages.success(request, '✅ База очищена и данные загружены!')
                    return redirect('admin:products_product_changelist')
                except Exception as e:
                    messages.error(request, f'Ошибка: {e}')
        
        elif action == 'clear_all':
            try:
                Product.objects.all().delete()
                Category.objects.all().delete()
                messages.success(request, '✅ База очищена!')
                return redirect('admin:products_category_changelist')
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
    
    return render(request, 'admin/parser_action.html', context)


def get_parser_status(request):
    """API endpoint для проверки статуса парсера."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    likestore_dir = os.path.dirname(backend_dir)
    json_path = os.path.join(likestore_dir, 'parser', 'src', 'parsed_data.json')
    
    result = {
        'json_exists': os.path.exists(json_path),
        'db_stats': {
            'categories': Category.objects.count(),
            'products': Product.objects.count(),
        }
    }
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result['json_stats'] = {
                    'products': len(data.get('products', [])),
                    'categories': len(data.get('categories', [])),
                }
        except Exception:
            pass
    
    return JsonResponse(result)


# ============================================
# Custom Admin Site
# ============================================

class ParserAdminSite(admin.AdminSite):
    """Custom admin site with parser action."""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('parser/', self.admin_view(run_parser_view), name='run_parser'),
            path('parser/status/', self.admin_view(get_parser_status), name='parser_status'),
        ]
        return custom_urls + urls


# Override default admin site
parser_admin_site = ParserAdminSite(name='likestore_admin')
parser_admin_site.register(Category, CategoryAdmin)
parser_admin_site.register(Brand, BrandAdmin)
parser_admin_site.register(Product, ProductAdmin)
parser_admin_site.register(ProductImage, ProductImageAdmin)
parser_admin_site.register(ProductSpecification, ProductSpecificationAdmin)
parser_admin_site.register(ProductVariant, ProductVariantAdmin)

# We'll use custom URLs in config/urls.py instead
