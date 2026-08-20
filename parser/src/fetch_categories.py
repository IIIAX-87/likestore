#!/usr/bin/env python3
"""
Simple parser for hm.lstore.ru using requests and BeautifulSoup.
Can be run without browser in any environment.
"""
import requests
import json
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional


BASE_URL = "https://hm.lstore.ru"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class ParsedProduct:
    """Parsed product data."""
    name: str = ""
    slug: str = ""
    article: str = ""
    price: str = "0"
    old_price: Optional[str] = None
    description: str = ""
    short_description: str = ""
    category_slug: str = ""
    category_name: str = ""
    brand: str = ""
    images: List[str] = field(default_factory=list)
    specifications: Dict[str, str] = field(default_factory=dict)
    stock: int = 10
    is_active: bool = True
    is_featured: bool = False
    is_bestseller: bool = False
    is_new: bool = False
    sku: str = ""
    url: str = ""


def fetch_page(url: str) -> Optional[str]:
    """Fetch page content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'ru-RU,ru;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        return response.text if response.status_code == 200 else None
    except Exception as e:
        print(f"  ❌ Ошибка загрузки {url}: {e}")
        return None


def extract_price(text: str) -> str:
    """Extract price from text."""
    if not text:
        return "0"
    numbers = re.findall(r'[\d\s]+', text)
    for num_str in numbers:
        num = num_str.replace(' ', '').replace('\xa0', '')
        if num and num.isdigit():
            return num
    return "0"


def clean_text(text: str) -> str:
    """Clean text."""
    if not text:
        return ""
    return ' '.join(text.split()).strip()


def detect_brand(name: str) -> str:
    """Detect brand from name."""
    name_lower = name.lower()
    brands = {
        "Apple": ["iphone", "ipad", "airpods", "macbook", "apple watch", "imac", "apple tv", "homepod"],
        "Samsung": ["samsung", "galaxy", "galaxy s", "galaxy a", "galaxy tab", "galaxy watch", "galaxy buds"],
        "Sony": ["sony", "playstation", "ps5", "ps4", "wh-"],
        "Microsoft": ["microsoft", "xbox", "surface"],
        "Dyson": ["dyson"],
        "Canon": ["canon", "eos", "powershot", "rf ", "ef "],
        "Xiaomi": ["xiaomi", "redmi", "poco"],
        "Nintendo": ["nintendo", "switch"],
        "JBL": ["jbl", "flip ", "charge ", "tune "],
        "Huawei": ["huawei", "matepad", "freebuds"],
    }
    for brand, keywords in brands.items():
        for keyword in keywords:
            if keyword in name_lower:
                return brand
    return "Apple"


class LikeStoreParser:
    """Parser for hm.lstore.ru using requests."""
    
    def __init__(self):
        self.products: List[ParsedProduct] = []
        self.categories: List[Dict] = []
        self.stats = {"categories": 0, "products": 0, "errors": 0}
    
    def parse_categories(self) -> List[Dict]:
        """Parse main page for categories."""
        print("\n📂 Парсинг категорий...")
        
        categories = [
            {"name": "iPhone", "slug": "iphone_1"},
            {"name": "Samsung", "slug": "samsung_1"},
            {"name": "iPad", "slug": "ipad"},
            {"name": "Watch", "slug": "watch"},
            {"name": "AirPods", "slug": "airpods_1"},
            {"name": "MacBook", "slug": "macbook"},
            {"name": "Приставки", "slug": "pristavki"},
            {"name": "Dyson", "slug": "dyson"},
            {"name": "Аксессуары", "slug": "aksessuary_1"},
            {"name": "Canon", "slug": "canon"},
            {"name": "TradeIn", "slug": "tradein_obmen"},
        ]
        
        for i, cat in enumerate(categories):
            cat["order"] = i + 1
            cat["url"] = f"{BASE_URL}/catalog/{cat['slug']}/"
            self.categories.append(cat)
        
        print(f"✅ Найдено {len(categories)} категорий")
        self.stats["categories"] = len(categories)
        return categories
    
    def parse_category(self, category: Dict) -> List[ParsedProduct]:
        """Parse products from category page."""
        print(f"\n📦 {category['name']}...")
        products = []
        
        html = fetch_page(category['url'])
        if not html:
            return products
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try different selectors for products
        cards = soup.select('.product-card, .catalog-item, .bx-catalogue-item, article')
        
        if not cards:
            # Try links with products
            links = soup.select('a[href*="/catalog/"]')
            seen = set()
            for link in links:
                href = link.get('href', '')
                if '/catalog/' in href and href not in seen:
                    # Check if it's a product link (usually has specific pattern)
                    parsed = urlparse(href)
                    parts = parsed.path.strip('/').split('/')
                    if len(parts) >= 4:  # catalog/category/product-slug
                        seen.add(href)
                        product = self.parse_product_from_url(urljoin(category['url'], href), category)
                        if product:
                            products.append(product)
        else:
            for card in cards[:50]:
                product = self.parse_card(card, category)
                if product:
                    products.append(product)
        
        print(f"  ✅ Найдено: {len(products)}")
        return products
    
    def parse_card(self, card, category: Dict) -> Optional[ParsedProduct]:
        """Parse product card."""
        try:
            # Name
            name_elem = card.select_one('h3, .product-card__name, .title')
            if not name_elem:
                name_elem = card.find(['a', 'span', 'div'])
            name = clean_text(name_elem.get_text()) if name_elem else ""
            
            if not name or len(name) < 3:
                return None
            
            # Price
            price_text = ""
            price_elem = card.select_one('.product-card__price, .price, [class*="price"]')
            if price_elem:
                price_text = price_elem.get_text()
            price = extract_price(price_text)
            
            # URL
            link = card.select_one('a[href*="/product/"]')
            if not link:
                link = card.select_one('a')
            url = urljoin(BASE_URL, link.get('href', '')) if link else ""
            
            # Slug
            slug = ""
            if url:
                parsed = urlparse(url)
                parts = parsed.path.strip('/').split('/')
                slug = parts[-1] if parts else ""
            if not slug:
                slug = name.lower().replace(' ', '-')[:100]
            
            # Image
            images = []
            img = card.select_one('img[src*="upload"], img[src*="wa-data"], img')
            if img:
                src = img.get('src') or img.get('data-src', '')
                if src:
                    if not src.startswith('http'):
                        src = urljoin(BASE_URL, src)
                    images.append(src)
            
            return ParsedProduct(
                name=name[:200],
                slug=slug,
                price=price,
                category_slug=category['slug'],
                category_name=category['name'],
                brand=detect_brand(name),
                images=images[:3],
                url=url,
                stock=10 if price != "0" else 0
            )
        except Exception as e:
            print(f"  ⚠️ Ошибка: {e}")
            return None
    
    def parse_product_from_url(self, url: str, category: Dict) -> Optional[ParsedProduct]:
        """Parse full product page."""
        try:
            html = fetch_page(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Name
            name_elem = soup.select_one('h1, .product-detail__title')
            name = clean_text(name_elem.get_text()) if name_elem else ""
            
            if not name:
                return None
            
            # Price
            price_elem = soup.select_one('.product-detail__price, .price-current')
            price = extract_price(price_elem.get_text()) if price_elem else "0"
            
            # Description
            desc_elem = soup.select_one('.product-detail__description, [class*="description"]')
            description = clean_text(desc_elem.get_text()) if desc_elem else ""
            short_description = description[:300] if description else ""
            
            # Images
            images = []
            for img in soup.select('.gallery img, .product-gallery img, [class*="gallery"] img'):
                src = img.get('src') or img.get('data-src', '')
                if src and ('upload' in src or 'wa-data' in src):
                    if not src.startswith('http'):
                        src = urljoin(BASE_URL, src)
                    if src not in images:
                        images.append(src)
            
            # Slug
            parsed = urlparse(url)
            parts = parsed.path.strip('/').split('/')
            slug = parts[-1] if parts else name.lower().replace(' ', '-')[:100]
            
            return ParsedProduct(
                name=name[:200],
                slug=slug,
                price=price,
                description=description[:2000],
                short_description=short_description,
                category_slug=category['slug'],
                category_name=category['name'],
                brand=detect_brand(name),
                images=images[:5],
                url=url,
                stock=10 if price != "0" else 0
            )
        except Exception as e:
            self.stats["errors"] += 1
            return None
    
    def save(self, filename: str = None) -> str:
        """Save data to JSON."""
        if filename is None:
            filename = os.path.join(OUTPUT_DIR, "parsed_data.json")
        
        data = {
            "categories": self.categories,
            "products": [asdict(p) for p in self.products if p.name],
            "metadata": {
                "total_products": len(self.products),
                "total_categories": len(self.categories),
                "source": BASE_URL,
                "stats": self.stats
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Сохранено: {len(self.products)} товаров")
        return filename
    
    def run(self):
        """Run parser."""
        print("🕷️  LikeStore Parser (requests)")
        print("=" * 40)
        
        categories = self.parse_categories()
        
        for cat in categories:
            products = self.parse_category(cat)
            self.products.extend(products)
            self.stats["products"] += len(products)
        
        filename = self.save()
        
        print("\n🎉 Готово!")
        print(f"   Товаров: {len(self.products)}")
        print(f"   Файл: {filename}")
        
        return filename


if __name__ == "__main__":
    parser = LikeStoreParser()
    parser.run()
