#!/usr/bin/env python3
"""
Script to load parsed data into Django database.
Usage: python load_to_db.py
"""
import os
import sys
import json
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Category, Brand, Product, ProductImage


def load_categories(categories_data):
    """Load categories from parsed data."""
    print("📂 Загрузка категорий...")
    
    created_count = 0
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'order': cat_data.get('order', 0),
                'is_active': cat_data.get('is_active', True),
            }
        )
        if created:
            created_count += 1
            print(f"  ✅ Создана: {category.name}")
        else:
            print(f"  ⚠️ Уже существует: {category.name}")
    
    print(f"✅ Создано {created_count} категорий")
    return created_count


def load_products(products_data):
    """Load products from parsed data."""
    print("\n📦 Загрузка товаров...")
    
    # Get or create Apple brand
    apple_brand, _ = Brand.objects.get_or_create(
        slug='apple',
        defaults={'name': 'Apple'}
    )
    print(f"  Бренд: {apple_brand.name}")
    
    created_count = 0
    skipped_count = 0
    
    for prod_data in products_data:
        # Skip products without name or invalid price
        if not prod_data.get('name') or prod_data.get('name') == '0':
            skipped_count += 1
            continue
        
        try:
            price = float(prod_data.get('price', 0))
            if price <= 0:
                skipped_count += 1
                continue
        except (ValueError, TypeError):
            skipped_count += 1
            continue
        
        # Get category
        category_slug = prod_data.get('category_slug')
        category = None
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                pass
        
        # Get brand
        brand_name = prod_data.get('brand', 'Apple')
        brand = apple_brand
        if brand_name and brand_name != 'Apple':
            brand, _ = Brand.objects.get_or_create(
                slug=brand_name.lower().replace(' ', '-'),
                defaults={'name': brand_name}
            )
        
        # Create or update product
        product, created = Product.objects.get_or_create(
            slug=prod_data.get('slug', ''),
            defaults={
                'name': prod_data['name'],
                'article': prod_data.get('article', ''),
                'price': price,
                'brand': brand,
                'category': category,
                'description': prod_data.get('description', ''),
                'short_description': prod_data.get('short_description', ''),
                'stock': prod_data.get('stock', 10),
                'is_active': prod_data.get('is_active', True),
                'is_featured': prod_data.get('is_featured', False),
                'is_bestseller': prod_data.get('is_bestseller', False),
                'is_new': prod_data.get('is_new', False),
            }
        )
        
        # Add images
        images = prod_data.get('images', [])
        if images and created:
            for idx, img_url in enumerate(images[:5]):
                ProductImage.objects.create(
                    product=product,
                    image=img_url,
                    is_main=(idx == 0),
                    order=idx
                )
        
        if created:
            created_count += 1
            print(f"  ✅ {product.name[:50]} - {product.price} ₽")
        else:
            print(f"  ⚠️ Обновлён: {product.name[:50]}")
    
    print(f"\n✅ Создано {created_count} товаров, пропущено {skipped_count}")
    return created_count


def main():
    """Main function."""
    # Find parsed data file
    data_file = os.path.join(os.path.dirname(__file__), 'parsed_data.json')
    
    if not os.path.exists(data_file):
        print(f"❌ Файл не найден: {data_file}")
        print("Сначала запустите parser.py")
        return
    
    print(f"📂 Чтение данных из: {data_file}")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories_data = data.get('categories', [])
    products_data = data.get('products', [])
    
    print(f"📊 Загружено: {len(categories_data)} категорий, {len(products_data)} товаров")
    
    # Load data
    load_categories(categories_data)
    load_products(products_data)
    
    print("\n🎉 Загрузка завершена!")
    print(f"   Всего категорий: {Category.objects.count()}")
    print(f"   Всего товаров: {Product.objects.count()}")


if __name__ == '__main__':
    main()
