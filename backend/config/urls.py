"""
URL configuration for likestore project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.admin import run_parser_view

urlpatterns = [
    # Admin с встроенным парсером
    path('admin/', admin.site.urls),
    path('parser/', run_parser_view, name='run_parser'),
    
    # API
    path('api/v1/products/', include('products.urls')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/cart/', include('cart.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
