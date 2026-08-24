"""
Admin configuration for Products app with integrated parser.
"""
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
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
# Parser Tasks (Celery)
# ============================================

def run_parser_sync(request):
    """
    Синхронный запуск парсера прямо из админки.
    Использует subprocess для запуска fetch_categories.py
    """
    import subprocess
    import threading
    import time
    
    # Путь к парсеру - работает и локально и в Docker
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    likestore_dir = os.path.dirname(backend_dir)
    
    # Docker: likestore_dir = /app, Local: likestore_dir = likestore
    if os.path.basename(likestore_dir) == 'app':
        project_root = likestore_dir
    else:
        project_root = likestore_dir
    
    parser_script = os.path.join(project_root, 'parser', 'src', 'fetch_categories.py')
    venv_python = os.path.join(project_root, 'parser', 'venv', 'bin', 'python')
    
    # Проверяем существование
    if not os.path.exists(parser_script):
        messages.error(request, f'Файл парсера не найден: {parser_script}')
        return redirect('admin:run_parser')
    
    # Сохраняем статус в сессию
    request.session['parser_status'] = 'running'
    request.session['parser_start_time'] = time.time()
    
    def run_parser():
        """Запуск парсера в фоне."""
        try:
            # Используем системный python если venv не найден
            if os.path.exists(venv_python):
                cmd = [venv_python, parser_script]
            else:
                cmd = ['python3', parser_script]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 минут timeout
                cwd=os.path.dirname(parser_script)
            )
            
            # Сохраняем результат
            request.session['parser_status'] = 'completed'
            request.session['parser_output'] = result.stdout + result.stderr
            request.session['parser_returncode'] = result.returncode
            
        except subprocess.TimeoutExpired:
            request.session['parser_status'] = 'timeout'
            request.session['parser_output'] = 'Превышен таймаут (5 минут)'
        except Exception as e:
            request.session['parser_status'] = 'error'
            request.session['parser_output'] = str(e)
    
    # Запускаем в отдельном потоке
    thread = threading.Thread(target=run_parser)
    thread.daemon = True
    thread.start()
    
    messages.info(request, '🕷️ Парсер запущен! Статус можно проверить на этой странице.')
    return redirect('admin:run_parser')


# ============================================
# Parser Integration View
# ============================================

def run_parser_view(request):
    """
    Главная страница парсера в админке.
    """
    from django.core.management import call_command
    import time
    
    # Пути - работает и локально и в Docker (/app)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    likestore_dir = os.path.dirname(base_dir)
    
    # Если в Docker - base_dir уже будет /app/backend, likestore_dir = /app
    # Если локально - base_dir = likestore/backend, likestore_dir = likestore
    # Проверяем структуру
    if os.path.basename(likestore_dir) == 'app':
        # Docker environment
        project_root = likestore_dir
    else:
        # Local environment
        project_root = likestore_dir
    
    json_path = os.path.join(project_root, 'parser', 'src', 'parsed_data.json')
    parser_script = os.path.join(project_root, 'parser', 'src', 'fetch_categories.py')
    
    context = {
        'title': '🕷️ Импорт товаров с сайта',
        'parser_template': True,
        'json_path': json_path,
        'parser_script': parser_script,
    }
    
    # Статистика базы
    context['stats'] = {
        'categories': Category.objects.count(),
        'brands': Brand.objects.count(),
        'products': Product.objects.count(),
    }
    
    # Проверка файла
    context['json_exists'] = os.path.exists(json_path)
    context['parser_exists'] = os.path.exists(parser_script)
    
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
    
    # Статус парсера
    parser_status = request.session.get('parser_status', 'idle')
    context['parser_status'] = parser_status
    
    if parser_status == 'running':
        start_time = request.session.get('parser_start_time', 0)
        elapsed = int(time.time() - start_time)
        context['parser_elapsed'] = elapsed
        context['parser_output'] = '⏳ Парсинг выполняется...'
    elif parser_status == 'completed':
        context['parser_output'] = request.session.get('parser_output', '')
        context['parser_returncode'] = request.session.get('parser_returncode', 0)
    elif parser_status == 'error':
        context['parser_output'] = f"❌ Ошибка: {request.session.get('parser_output', '')}"
    elif parser_status == 'timeout':
        context['parser_output'] = "⏰ Таймаут! Парсинг занял слишком много времени."
    
    # Обработка POST
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'run_parser':
            # Запускаем парсер
            import subprocess
            import threading
            
            def run_parser():
                try:
                    result = subprocess.run(
                        ['python3', parser_script],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=os.path.dirname(parser_script)
                    )
                    request.session['parser_status'] = 'completed'
                    request.session['parser_output'] = result.stdout
                    request.session['parser_returncode'] = result.returncode
                except subprocess.TimeoutExpired:
                    request.session['parser_status'] = 'timeout'
                    request.session['parser_output'] = 'Превышен таймаут (5 минут)'
                except Exception as e:
                    request.session['parser_status'] = 'error'
                    request.session['parser_output'] = str(e)
            
            request.session['parser_status'] = 'running'
            request.session['parser_start_time'] = time.time()
            request.session.pop('parser_output', None)
            
            thread = threading.Thread(target=run_parser)
            thread.daemon = True
            thread.start()
            
            messages.info(request, '🕷️ Парсер запущен! Обновите страницу через несколько секунд.')
        
        elif action == 'load_data':
            if not os.path.exists(json_path):
                messages.error(request, f'Файл не найден: {json_path}')
            else:
                try:
                    # Очищаем сессию парсера
                    request.session.pop('parser_status', None)
                    request.session.pop('parser_output', None)
                    
                    call_command('load_products', '--file=' + json_path, verbosity=2)
                    messages.success(request, f'✅ Загружено! Товаров в базе: {Product.objects.count()}')
                except Exception as e:
                    messages.error(request, f'Ошибка загрузки: {e}')
        
        elif action == 'clear_and_load':
            if not os.path.exists(json_path):
                messages.error(request, f'Файл не найден: {json_path}')
            else:
                try:
                    request.session.pop('parser_status', None)
                    call_command('load_products', '--file=' + json_path, '--clear', verbosity=2)
                    messages.success(request, '✅ База очищена и загружена!')
                except Exception as e:
                    messages.error(request, f'Ошибка: {e}')
        
        elif action == 'clear_all':
            try:
                Product.objects.all().delete()
                Category.objects.all().delete()
                messages.success(request, '✅ База очищена!')
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
        
        return redirect('admin:run_parser')
    
    return render(request, 'admin/parser_action.html', context)


def parser_status_api(request):
    """API для проверки статуса парсера (AJAX polling)."""
    status = request.session.get('parser_status', 'idle')
    output = request.session.get('parser_output', '')
    
    return JsonResponse({
        'status': status,
        'output': output,
        'returncode': request.session.get('parser_returncode', None),
    })


# ============================================
# Custom Admin Site
# ============================================

class ParserAdminSite(admin.AdminSite):
    """Custom admin site with parser action."""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('parser/', self.admin_view(run_parser_view), name='run_parser'),
            path('parser/status/', self.admin_view(parser_status_api), name='parser_status'),
            path('parser/run/', self.admin_view(run_parser_sync), name='run_parser_sync'),
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
