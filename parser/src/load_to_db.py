#!/usr/bin/env python3
"""
Script to load parsed data into Django database.
Run after migrations: python manage.py migrate
"""
import os
import sys
import json

# Setup Django path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_path))

# Configure Django settings BEFORE importing Django modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django and setup
import django
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
    
    # Get or create Samsung brand
    samsung_brand, _ = Brand.objects.get_or_create(
        slug='samsung',
        defaults={'name': 'Samsung'}
    )
    print(f"  Бренды: {apple_brand.name}, {samsung_brand.name}")
    
    created_count = 0
    skipped_count = 0
    
    for prod_data in products_data:
        # Skip products without name or invalid price
        if not prod_data.get('name') or not prod_data.get('price'):
            skipped_count += 1
            continue
        
        try:
            price = float(str(prod_data.get('price', 0)).replace(' ', ''))
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
        if 'samsung' in brand_name.lower():
            brand = samsung_brand
        else:
            brand = apple_brand
        
        # Create or update product
        slug = prod_data.get('slug') or prod_data['name'].lower().replace(' ', '-')[:100]
        
        # Handle old_price
        old_price = None
        if prod_data.get('old_price'):
            try:
                old_price_val = float(str(prod_data['old_price']).replace(' ', ''))
                if old_price_val > price:
                    old_price = old_price_val
            except (ValueError, TypeError):
                pass
        
        product, created = Product.objects.get_or_create(
            slug=slug,
            defaults={
                'name': prod_data['name'][:200],
                'article': prod_data.get('article', '')[:50],
                'price': price,
                'old_price': old_price,
                'brand': brand,
                'category': category,
                'description': prod_data.get('description', '')[:2000],
                'short_description': prod_data.get('short_description', '')[:500],
                'stock': prod_data.get('stock', 10),
                'in_stock': prod_data.get('stock', 10) > 0,
                'is_active': prod_data.get('is_active', True),
                'is_featured': prod_data.get('is_featured', False),
                'is_bestseller': prod_data.get('is_bestseller', False),
                'is_new': prod_data.get('is_new', False),
            }
        )
        
        # Add images (only for new products)
        if created and prod_data.get('images'):
            for idx, img_url in enumerate(prod_data['images'][:5]):
                ProductImage.objects.create(
                    product=product,
                    image_url=img_url,
                    is_main=(idx == 0),
                    order=idx
                )
        
        if created:
            created_count += 1
            name_display = product.name[:50]
            print(f"  ✅ {name_display}... - {price} ₽")
        else:
            skipped_count += 1
    
    print(f"\n✅ Создано {created_count} товаров, пропущено {skipped_count}")
    return created_count


def main():
    """Main function."""
    # Find parsed data file
    data_file = os.path.join(os.path.dirname(__file__), 'parsed_data.json')
    
    if not os.path.exists(data_file):
        print(f"❌ Файл не найден: {data_file}")
        print("Сначала запустите parser.py")
        sys.exit(1)
    
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
