#!/usr/bin/env python3
"""
Load products from parsed_data.json into database.
Run: python manage.py shell < load_products.py
Or: python load_products.py (from backend directory)
"""
import os
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from products.models import Category, Brand, Product, ProductImage


def load_data():
    # Find parsed_data.json - try multiple paths
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'parsed_data.json'),  # Backend directory
        '/app/parsed_data.json',  # Docker volume
        '/app/parser_data/parsed_data.json',  # Docker volume (old)
        'parsed_data.json',  # Current directory
    ]
    
    data_file = None
    for path in possible_paths:
        if os.path.exists(path):
            data_file = path
            print(f"📂 Найден файл: {data_file}")
            break
    
    if not data_file:
        print(f"❌ Файл не найден. Искали в:")
        for p in possible_paths:
            print(f"  - {p}")
        return
    
    if not os.path.exists(data_file):
        print(f"❌ Файл не найден: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = data.get('categories', [])
    products = data.get('products', [])
    
    print(f"📊 Загружаю: {len(categories)} категорий, {len(products)} товаров")
    
    # Load categories
    for cat in categories:
        Category.objects.get_or_create(
            slug=cat['slug'],
            defaults={
                'name': cat['name'],
                'order': cat.get('order', 0),
                'is_active': cat.get('is_active', True),
            }
        )
    print(f"✅ Категории: {Category.objects.count()}")
    
    # Load brands
    apple, _ = Brand.objects.get_or_create(slug='apple', defaults={'name': 'Apple'})
    samsung, _ = Brand.objects.get_or_create(slug='samsung', defaults={'name': 'Samsung'})
    
    # Load products
    for prod in products:
        if not prod.get('name') or not prod.get('price'):
            continue
        
        try:
            price = float(str(prod['price']).replace(' ', ''))
        except:
            continue
        
        cat = Category.objects.filter(slug=prod.get('category_slug')).first()
        brand = apple if 'samsung' not in prod.get('brand', '').lower() else samsung
        
        product, created = Product.objects.get_or_create(
            slug=prod.get('slug') or prod['name'].lower().replace(' ', '-')[:100],
            defaults={
                'name': prod['name'][:200],
                'price': price,
                'brand': brand,
                'category': cat,
                'description': prod.get('description', ''),
                'stock': prod.get('stock', 10),
                'in_stock': prod.get('stock', 10) > 0,
            }
        )
        
        if created and prod.get('images'):
            for idx, img in enumerate(prod['images'][:5]):
                ProductImage.objects.create(
                    product=product,
                    image_url=img,
                    is_main=(idx == 0),
                    order=idx
                )
            print(f"  ✅ {product.name[:40]}... - {price}₽")
    
    print(f"\n🎉 Готово! Товаров: {Product.objects.count()}")


if __name__ == '__main__':
    load_data()
