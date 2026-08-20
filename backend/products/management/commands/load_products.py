"""
Django management command to load products from parsed JSON.
Usage: python manage.py load_products
"""
import json
import os
from django.core.management.base import BaseCommand
from products.models import Category, Brand, Product, ProductImage


class Command(BaseCommand):
    help = 'Load products and categories from parsed JSON data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Path to parsed_data.json file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products before loading'
        )

    def handle(self, *args, **options):
        # Find JSON file
        if options['file']:
            json_path = options['file']
        else:
            # Default path
            json_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'parser', 'src', 'parsed_data.json'
            )

        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories_data = data.get('categories', [])
        products_data = data.get('products', [])

        self.stdout.write(f"Found: {len(categories_data)} categories, {len(products_data)} products\n")

        # Clear if requested
        if options['clear']:
            self.stdout.write('Clearing existing products...')
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared!'))

        # Load categories
        self.stdout.write('\nLoading categories...')
        brand_map = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'order': cat_data.get('order', 0),
                    'is_active': cat_data.get('is_active', True),
                }
            )
            status = self.style.SUCCESS('created') if created else self.style.WARNING('exists')
            self.stdout.write(f"  [{status}] {category.name}")

        # Create default brand
        apple_brand, _ = Brand.objects.get_or_create(
            slug='apple',
            defaults={'name': 'Apple'}
        )
        brand_map['Apple'] = apple_brand

        # Load products
        self.stdout.write('\nLoading products...')
        created_count = 0
        skipped = 0

        for prod_data in products_data:
            # Skip invalid
            if not prod_data.get('name') or not prod_data.get('price'):
                skipped += 1
                continue

            try:
                price = float(str(prod_data.get('price', 0)).replace(' ', ''))
                if price <= 0:
                    skipped += 1
                    continue
            except (ValueError, TypeError):
                skipped += 1
                continue

            # Get category
            category = None
            cat_slug = prod_data.get('category_slug')
            if cat_slug:
                category = Category.objects.filter(slug=cat_slug).first()

            # Get/create brand
            brand_name = prod_data.get('brand', 'Apple')
            brand = brand_map.get(brand_name)
            if not brand:
                brand, _ = Brand.objects.get_or_create(
                    slug=brand_name.lower().replace(' ', '-'),
                    defaults={'name': brand_name}
                )
                brand_map[brand_name] = brand

            # Create product
            slug = prod_data.get('slug') or prod_data['name'].lower().replace(' ', '-')[:100]
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': prod_data['name'][:200],
                    'article': prod_data.get('article', '')[:50],
                    'price': price,
                    'old_price': float(str(p).replace(' ', '')) if (p := prod_data.get('old_price')) and p != '0' else None,
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

            # Add images
            if created and prod_data.get('images'):
                for idx, img_url in enumerate(prod_data['images'][:5]):
                    ProductImage.objects.create(
                        product=product,
                        image_url=img_url,
                        is_main=(idx == 0),
                        order=idx
                    )

            created_count += 1
            status = self.style.SUCCESS('+') if created else self.style.WARNING('~')
            self.stdout.write(f"  [{status}] {product.name[:45]}... {price}₽")

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✓ Done!'))
        self.stdout.write(f"  Categories: {Category.objects.count()}")
        self.stdout.write(f"  Products: {Product.objects.count()}")
        self.stdout.write(f"  Created: {created_count}, Skipped: {skipped}")
