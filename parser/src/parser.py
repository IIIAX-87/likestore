#!/usr/bin/env python3
"""
Improved Playwright parser for hm.lstore.ru
Parses products, categories, prices from the website.
"""
import asyncio
import json
import re
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeout


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


@dataclass
class ParsedCategory:
    """Parsed category data."""
    name: str = ""
    slug: str = ""
    parent_slug: str = ""
    description: str = ""
    image: str = ""
    order: int = 0


class LikeStoreParser:
    """Parser for hm.lstore.ru"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.products: List[ParsedProduct] = []
        self.categories: List[Dict] = []
        self.session = None
        self.stats = {
            "categories_found": 0,
            "products_found": 0,
            "errors": 0
        }
        
    async def init(self):
        """Initialize browser."""
        print("🚀 Запуск браузера...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        self.page = await self.context.new_page()
        
        # Block unnecessary resources
        await self.context.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}", lambda route: route.abort())
        
        print("✅ Браузер запущен")
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
            print("🔒 Браузер закрыт")
    
    def extract_price(self, text: str) -> str:
        """Extract numeric price from text."""
        if not text:
            return "0"
        # Find all numbers
        numbers = re.findall(r'[\d\s]+', text)
        for num_str in numbers:
            # Clean spaces
            num = num_str.replace(' ', '').replace('\xa0', '')
            if num and num.isdigit():
                return num
        return "0"
    
    def extract_discount(self, text: str) -> Optional[str]:
        """Extract old price from discount text."""
        # Pattern: "99990 ₽ < 119990 ₽" or "119990"
        match = re.search(r'(\d+[\d\s]*)\s*[<‑—]\s*(\d+[\d\s]*)', text)
        if match:
            return match.group(2).replace(' ', '').replace('\xa0', '')
        return None
    
    def clean_text(self, text: str) -> str:
        """Clean text from extra whitespace and newlines."""
        if not text:
            return ""
        return ' '.join(text.split()).strip()
    
    def generate_slug(self, text: str) -> str:
        """Generate URL-friendly slug."""
        if not text:
            return ""
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug[:100].strip('-')
        return slug
    
    async def get_page_content(self, url: str, wait_time: int = 2000) -> bool:
        """Navigate to page and wait for content."""
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await self.page.wait_for_timeout(wait_time)
            return True
        except Exception as e:
            print(f"  ❌ Ошибка загрузки: {e}")
            self.stats["errors"] += 1
            return False
    
    async def find_main_categories(self) -> List[Dict]:
        """Find main navigation categories."""
        print("\n📂 Поиск категорий...")
        
        categories = []
        
        # Try to get from main navigation
        await self.get_page_content(BASE_URL, 3000)
        
        # Try different selectors for main menu
        menu_selectors = [
            "nav a[href*='/catalog/']",
            ".header__menu a",
            ".main-menu a",
            ".nav-list a",
            "header a[href*='/catalog/']"
        ]
        
        found_slugs = set()
        
        for selector in menu_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                links = await self.page.query_selector_all(selector)
                
                for link in links:
                    try:
                        href = await link.get_attribute("href")
                        text = await link.inner_text()
                        text = self.clean_text(text)
                        
                        if href and '/catalog/' in href and text and len(text) > 1:
                            parsed = urlparse(href)
                            path = parsed.path.strip('/')
                            parts = path.split('/')
                            
                            if len(parts) >= 2 and 'catalog' in parts:
                                slug = parts[-1]
                                if slug not in found_slugs and len(slug) > 1:
                                    found_slugs.add(slug)
                                    categories.append({
                                        "name": text,
                                        "slug": slug,
                                        "url": href if href.startswith('http') else BASE_URL + href
                                    })
                    except Exception:
                        continue
                        
                if len(categories) >= 5:
                    break
            except PlaywrightTimeout:
                continue
        
        # If nothing found, use known categories
        if len(categories) < 5:
            print("  📍 Используем известные категории...")
            known_categories = [
                {"name": "iPhone", "slug": "iphone_1", "url": f"{BASE_URL}/catalog/iphone_1/"},
                {"name": "Samsung", "slug": "samsung_1", "url": f"{BASE_URL}/catalog/samsung_1/"},
                {"name": "iPad", "slug": "ipad", "url": f"{BASE_URL}/catalog/ipad/"},
                {"name": "Watch", "slug": "watch", "url": f"{BASE_URL}/catalog/watch/"},
                {"name": "AirPods", "slug": "airpods_1", "url": f"{BASE_URL}/catalog/airpods_1/"},
                {"name": "MacBook", "slug": "macbook", "url": f"{BASE_URL}/catalog/macbook/"},
                {"name": "Приставки", "slug": "pristavki", "url": f"{BASE_URL}/catalog/pristavki/"},
                {"name": "Dyson", "slug": "dyson", "url": f"{BASE_URL}/catalog/dyson/"},
                {"name": "Аксессуары", "slug": "aksessuary_1", "url": f"{BASE_URL}/catalog/aksessuary_1/"},
                {"name": "Canon", "slug": "canon", "url": f"{BASE_URL}/catalog/canon/"},
                {"name": "TradeIn", "slug": "tradein_obmen", "url": f"{BASE_URL}/catalog/tradein_obmen/"},
            ]
            categories = known_categories
        
        # Add order
        for i, cat in enumerate(categories):
            cat["order"] = i + 1
            self.categories.append(cat)
        
        print(f"✅ Найдено {len(categories)} категорий")
        self.stats["categories_found"] = len(categories)
        return categories
    
    async def parse_category_products(self, category: Dict) -> List[ParsedProduct]:
        """Parse products from category page."""
        print(f"\n📦 Парсинг: {category['name']}")
        
        products = []
        category_url = category.get('url', f"{BASE_URL}/catalog/{category['slug']}/")
        
        await self.get_page_content(category_url, 3000)
        
        # Try multiple selectors for product cards
        product_selectors = [
            ".product-card",
            ".catalog-item",
            ".bx-catalogue-item",
            "article",
            ".item",
            "[class*='product']",
            ".goods-item"
        ]
        
        cards = []
        for selector in product_selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=3000)
                cards = await self.page.query_selector_all(selector)
                if len(cards) >= 2:
                    print(f"  📍 Селектор: {selector} ({len(cards)} карточек)")
                    break
            except PlaywrightTimeout:
                continue
        
        # If no cards found, try to find product links
        if len(cards) < 2:
            links = await self.page.query_selector_all("a[href*='/product/']")
            if links:
                for link in links[:30]:
                    try:
                        href = await link.get_attribute("href")
                        if href and '/product/' in href:
                            url = href if href.startswith('http') else BASE_URL + href
                            product = await self.parse_product_detail(url, category)
                            if product:
                                products.append(product)
                    except Exception:
                        continue
        else:
            # Parse each card
            for idx, card in enumerate(cards[:50]):
                try:
                    product = await self.parse_product_card(card, category)
                    if product and product.name:
                        products.append(product)
                        print(f"  ✅ [{idx+1}] {product.name[:40]}... {product.price}₽")
                except Exception as e:
                    print(f"  ⚠️ Карточка {idx}: {e}")
                    continue
        
        # Pagination - load more pages
        next_page = await self.page.query_selector(".pagination__next, .next, a[rel='next'], .bx-pagination-next")
        if next_page and len(products) < 100:
            try:
                href = await next_page.get_attribute("href")
                if href:
                    more_products = await self.parse_category_products(category)
                    products.extend(more_products)
            except Exception:
                pass
        
        return products
    
    async def parse_product_card(self, card, category: Dict) -> Optional[ParsedProduct]:
        """Parse single product card."""
        try:
            # Name
            name = ""
            for selector in ["h3", ".product-card__name", ".product-card__title", ".title", "[class*='name']", "[class*='title']"]:
                elem = await card.query_selector(selector)
                if elem:
                    name = await elem.inner_text()
                    name = self.clean_text(name)
                    if name and len(name) > 2:
                        break
            
            if not name:
                return None
            
            # Price
            price = "0"
            old_price = None
            for selector in [".product-card__price", ".price", "[class*='price']", ".product-price"]:
                price_elem = await card.query_selector(selector)
                if price_elem:
                    price_text = await price_elem.inner_text()
                    old_price = self.extract_discount(price_text)
                    price = self.extract_price(price_text)
                    if price and price != "0":
                        break
            
            # Image
            images = []
            img = await card.query_selector("img[src*='upload'], img[src*='media'], img")
            if img:
                src = await img.get_attribute("src")
                if src and not src.endswith('.svg'):
                    if not src.startswith('http'):
                        src = BASE_URL + src
                    images.append(src)
            
            # URL
            url = ""
            link = await card.query_selector("a[href*='/product/']")
            if not link:
                link = await card.query_selector("a")
            if link:
                href = await link.get_attribute("href")
                if href:
                    url = href if href.startswith('http') else BASE_URL + href
                    
                    # Parse slug from URL
                    parsed = urlparse(href)
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts:
                        slug = path_parts[-1]
                    else:
                        slug = self.generate_slug(name)
                else:
                    slug = self.generate_slug(name)
            else:
                slug = self.generate_slug(name)
            
            # Detect brand from name
            brand = self.detect_brand(name)
            
            return ParsedProduct(
                name=name,
                slug=slug,
                price=price,
                old_price=old_price,
                category_slug=category['slug'],
                category_name=category['name'],
                brand=brand,
                images=images[:3],
                url=url,
                stock=10 if price != "0" else 0
            )
            
        except Exception as e:
            print(f"  ⚠️ Ошибка карточки: {e}")
            return None
    
    async def parse_product_detail(self, url: str, category: Dict) -> Optional[ParsedProduct]:
        """Parse full product detail page."""
        try:
            await self.get_page_content(url, 2000)
            
            # Name
            name = ""
            for selector in ["h1", ".product-detail__title", "[class*='title']"]:
                elem = await self.page.query_selector(selector)
                if elem:
                    name = await elem.inner_text()
                    name = self.clean_text(name)
                    if name:
                        break
            
            if not name:
                return None
            
            # Price
            price = "0"
            old_price = None
            for selector in [".product-detail__price", ".price-current", "[class*='price']"]:
                price_elem = await self.page.query_selector(selector)
                if price_elem:
                    price_text = await price_elem.inner_text()
                    old_price = self.extract_discount(price_text)
                    price = self.extract_price(price_text)
                    if price:
                        break
            
            # Description
            description = ""
            for selector in [".product-detail__description", "[class*='description']"]:
                desc_elem = await self.page.query_selector(selector)
                if desc_elem:
                    description = await desc_elem.inner_text()
                    description = self.clean_text(description)
                    if description:
                        break
            
            # Short description (first 200 chars)
            short_description = description[:300] if description else ""
            
            # Images
            images = []
            img_selectors = ["[class*='gallery'] img", "[class*='swiper'] img", ".product-gallery img", "img"]
            for selector in img_selectors:
                imgs = await self.page.query_selector_all(selector)
                for img in imgs[:5]:
                    src = await img.get_attribute("src")
                    if src and ('upload' in src or 'media' in src or '/wa-data/' in src):
                        if not src.startswith('http'):
                            src = BASE_URL + src
                        if src not in images:
                            images.append(src)
            
            # SKU/Article
            sku = ""
            sku_elem = await self.page.query_selector("[class*='article'], [class*='sku'], .articul")
            if sku_elem:
                sku = await sku_elem.inner_text()
                sku = self.clean_text(sku)
            
            # Specifications
            specs = {}
            spec_rows = await self.page.query_selector_all("tr, [class*='spec']")
            for row in spec_rows[:20]:
                try:
                    cells = await row.query_selector_all("td, [class*='name'], [class*='value']")
                    if len(cells) >= 2:
                        key = await cells[0].inner_text()
                        value = await cells[1].inner_text()
                        if key and value:
                            specs[self.clean_text(key)] = self.clean_text(value)
                except Exception:
                    continue
            
            slug = urlparse(url).path.strip('/').split('/')[-1]
            brand = self.detect_brand(name)
            
            return ParsedProduct(
                name=name,
                slug=slug,
                article=sku,
                price=price,
                old_price=old_price,
                description=description,
                short_description=short_description,
                category_slug=category['slug'],
                category_name=category['name'],
                brand=brand,
                images=images[:5],
                specifications=specs,
                stock=10 if price != "0" else 0,
                url=url
            )
            
        except Exception as e:
            print(f"  ❌ Ошибка деталей: {e}")
            self.stats["errors"] += 1
            return None
    
    def detect_brand(self, name: str) -> str:
        """Detect brand from product name."""
        name_lower = name.lower()
        
        brands = {
            "Apple": ["iphone", "ipad", "apple", "airpods", "macbook", "apple watch", "imac", "mac mini", "apple tv"],
            "Samsung": ["samsung", "galaxy", "galaxy s", "galaxy a", "galaxy tab", "galaxy watch"],
            "Sony": ["sony", "playstation", "ps5", "ps4", "playstation 5"],
            "Microsoft": ["microsoft", "xbox", "surface"],
            "Dyson": ["dyson"],
            "Canon": ["canon", "eos", "powershot"],
            "Xiaomi": ["xiaomi", "redmi", "poco"],
            "Nintendo": ["nintendo", "switch"],
            "JBL": ["jbl"],
            "Huawei": ["huawei"]
        }
        
        for brand, keywords in brands.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return brand
        
        return "Apple"  # Default
    
    def export_data(self, filename: str = None) -> str:
        """Export parsed data to JSON."""
        if filename is None:
            filename = os.path.join(OUTPUT_DIR, "parsed_data.json")
        
        print(f"\n💾 Сохранение данных...")
        
        # Convert dataclasses to dicts
        products_list = []
        for p in self.products:
            if p.name:
                products_list.append(asdict(p))
        
        data = {
            "categories": self.categories,
            "products": products_list,
            "metadata": {
                "total_products": len(products_list),
                "total_categories": len(self.categories),
                "source": BASE_URL,
                "stats": self.stats
            }
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Сохранено: {len(products_list)} товаров, {len(self.categories)} категорий")
        print(f"   Файл: {filename}")
        
        return filename
    
    async def run(self) -> str:
        """Run full parsing."""
        await self.init()
        
        try:
            # Get categories
            categories = await self.find_main_categories()
            
            # Parse each category
            for category in categories:
                products = await self.parse_category_products(category)
                self.products.extend(products)
                self.stats["products_found"] += len(products)
            
            # Export
            filename = self.export_data()
            
            print(f"\n🎉 Парсинг завершён!")
            print(f"   Товаров: {len(self.products)}")
            print(f"   Категорий: {len(self.categories)}")
            print(f"   Ошибок: {self.stats['errors']}")
            
            return filename
            
        finally:
            await self.close()


async def main():
    """Main entry point."""
    parser = LikeStoreParser()
    await parser.run()


if __name__ == "__main__":
    asyncio.run(main())
