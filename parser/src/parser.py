#!/usr/bin/env python3
"""
Improved Playwright parser for hm.lstore.ru
Parses products and categories from the website.
"""
import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeout


BASE_URL = "https://hm.lstore.ru"


@dataclass
class Product:
    """Product data model."""
    name: str = ""
    slug: str = ""
    article: str = ""
    price: str = "0"
    old_price: Optional[str] = None
    description: str = ""
    short_description: str = ""
    category_slug: str = ""
    category_name: str = ""
    brand: str = "Apple"
    images: List[str] = field(default_factory=list)
    specifications: Dict[str, str] = field(default_factory=dict)
    stock: int = 10
    is_active: bool = True
    is_featured: bool = False
    is_bestseller: bool = False
    is_new: bool = False


@dataclass 
class Category:
    """Category data model."""
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
        self.products: List[Product] = []
        self.categories: List[Dict] = []
        
    async def init(self):
        """Initialize browser."""
        print("🚀 Запуск браузера...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        print("✅ Браузер запущен")
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
            print("🔒 Браузер закрыт")
    
    async def wait_for_selector_with_timeout(self, selector: str, timeout: int = 10000):
        """Wait for selector with custom timeout."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeout:
            return False

    async def parse_main_page(self) -> List[Category]:
        """Parse main page categories."""
        print("\n📂 Парсинг категорий...")
        
        categories = [
            {"name": "iPhone", "slug": "iphone_1", "order": 1},
            {"name": "Samsung", "slug": "samsung_1", "order": 2},
            {"name": "iPad", "slug": "ipad", "order": 3},
            {"name": "Watch", "slug": "watch", "order": 4},
            {"name": "AirPods", "slug": "airpods_1", "order": 5},
            {"name": "MacBook", "slug": "macbook", "order": 6},
            {"name": "Приставки", "slug": "pristavki", "order": 7},
            {"name": "Dyson", "slug": "dyson", "order": 8},
            {"name": "Аксессуары", "slug": "aksessuary_1", "order": 9},
            {"name": "Canon", "slug": "canon", "order": 10},
            {"name": "TradeIn/Обмен", "slug": "tradein_obmen", "order": 11},
        ]
        
        for cat in categories:
            self.categories.append({
                "name": cat["name"],
                "slug": cat["slug"],
                "order": cat["order"],
                "is_active": True
            })
        
        print(f"✅ Найдено {len(categories)} категорий")
        return [Category(**c) for c in categories]
    
    def extract_price(self, text: str) -> str:
        """Extract numeric price from text."""
        # Remove spaces and non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d,.]', '', text.replace(' ', '').replace(',', '.'))
        # Take only the first number
        match = re.search(r'(\d+\.?\d*)', cleaned)
        return match.group(1) if match else "0"
    
    def clean_text(self, text: str) -> str:
        """Clean text from extra whitespace and newlines."""
        return ' '.join(text.split()).strip()

    async def parse_category(self, category: Category) -> List[Product]:
        """Parse products from category page."""
        print(f"\n📦 Парсинг категории: {category.name}")
        
        products = []
        
        try:
            await self.page.goto(
                f"{BASE_URL}/catalog/{category.slug}/",
                wait_until="networkidle",
                timeout=60000
            )
            
            # Wait for content to load
            await self.page.wait_for_timeout(3000)
            
            # Try multiple selectors for product cards
            selectors_to_try = [
                "article.product-card",
                ".product-card",
                "[class*='product-card']",
                ".catalog-section__item",
                ".bx-catalogue-item",
            ]
            
            product_elements = None
            for selector in selectors_to_try:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    product_elements = await self.page.query_selector_all(selector)
                    if product_elements:
                        print(f"  📍 Найден селектор: {selector}")
                        break
                except PlaywrightTimeout:
                    continue
            
            if not product_elements:
                # Try to get all links to products
                product_links = await self.page.query_selector_all("a[href*='/catalog/'][href*='/']")
                print(f"  📍 Найдено ссылок на товары: {len(product_links)}")
                
                seen_urls = set()
                for link in product_links:
                    try:
                        href = await link.get_attribute("href")
                        if href and '/catalog/' in href and href.count('/') >= 3:
                            parsed = urlparse(href)
                            clean_url = parsed.path.rstrip('/')
                            if clean_url not in seen_urls and len(clean_url.split('/')) >= 4:
                                seen_urls.add(clean_url)
                    except Exception:
                        continue
                
                # Parse product URLs
                for url in list(seen_urls)[:20]:
                    product = await self.parse_product_from_url(url, category)
                    if product and product.name:
                        products.append(product)
                        self.products.append(product)
                        print(f"  ✅ {product.name} - {product.price} ₽")
                
                print(f"✅ Собрано {len(products)} товаров из {category.name}")
                return products
            
            for idx, card in enumerate(product_elements[:50]):
                try:
                    # Try to get product name
                    name = ""
                    for name_selector in ["h3", ".product-card__title", ".title", "[class*='title']"]:
                        name_elem = await card.query_selector(name_selector)
                        if name_elem:
                            name = await name_elem.inner_text()
                            name = self.clean_text(name)
                            if name:
                                break
                    
                    # Try to get price
                    price = "0"
                    for price_selector in [".product-card__price", "[class*='price']", ".price"]:
                        price_elem = await card.query_selector(price_selector)
                        if price_elem:
                            price_text = await price_elem.inner_text()
                            price = self.extract_price(price_text)
                            if price and price != "0":
                                break
                    
                    # Get product URL
                    url = ""
                    link_elem = await card.query_selector("a[href*='/catalog/']")
                    if link_elem:
                        href = await link_elem.get_attribute("href")
                        if href:
                            url = href
                    
                    # Extract slug from URL
                    slug = ""
                    if url:
                        parts = url.rstrip('/').split('/')
                        slug = parts[-1] if parts else ""
                    
                    if name and len(name) > 2:
                        product = Product(
                            name=name,
                            slug=slug,
                            price=price,
                            category_slug=category.slug,
                            category_name=category.name,
                        )
                        products.append(product)
                        print(f"  ✅ {name[:50]}... - {price} ₽")
                        
                except Exception as e:
                    print(f"  ⚠️ Ошибка: {e}")
                    continue
                    
        except Exception as e:
            print(f"  ❌ Ошибка загрузки категории: {e}")
        
        print(f"✅ Найдено {len(products)} товаров в {category.name}")
        return products
    
    async def parse_product_from_url(self, url: str, category: Category) -> Optional[Product]:
        """Parse product from direct URL."""
        try:
            full_url = url if url.startswith('http') else f"{BASE_URL}{url}"
            await self.page.goto(full_url, wait_until="networkidle", timeout=30000)
            await self.page.wait_for_timeout(1500)
            
            # Get name
            name = ""
            for selector in ["h1", ".product-detail__title", "[class*='title']"]:
                elem = await self.page.query_selector(selector)
                if elem:
                    name = await elem.inner_text()
                    name = self.clean_text(name)
                    if name:
                        break
            
            # Get price
            price = "0"
            for selector in [".product-info__price-current", "[class*='price-current']", ".price"]:
                elem = await self.page.query_selector(selector)
                if elem:
                    price_text = await elem.inner_text()
                    price = self.extract_price(price_text)
                    break
            
            # Get description
            description = ""
            for selector in [".product-info__description", "[class*='description']"]:
                elem = await self.page.query_selector(selector)
                if elem:
                    description = await elem.inner_text()
                    description = self.clean_text(description)
                    if description:
                        break
            
            # Get images
            images = []
            img_elems = await self.page.query_selector_all("[class*='gallery'] img, .product-gallery img, [class*='product'] img")
            for img in img_elems[:5]:
                src = await img.get_attribute("src")
                if src and ("upload" in src or "media" in src):
                    if not src.startswith('http'):
                        src = BASE_URL + src
                    images.append(src)
            
            slug = url.rstrip('/').split('/')[-1] if url else ""
            
            return Product(
                name=name,
                slug=slug,
                price=price,
                description=description,
                images=images,
                category_slug=category.slug,
                category_name=category.name,
            )
            
        except Exception as e:
            print(f"  ❌ Ошибка парсинга {url}: {e}")
            return None

    def export_data(self, filename: str = "parsed_data.json"):
        """Export parsed data to JSON."""
        print(f"\n💾 Экспорт данных в {filename}...")
        
        data = {
            "categories": self.categories,
            "products": [
                asdict(p) for p in self.products if p.name
            ],
            "metadata": {
                "total_products": len(self.products),
                "total_categories": len(self.categories),
                "source": BASE_URL,
            }
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Экспортировано {len(self.products)} товаров и {len(self.categories)} категорий")
        return filename


async def main():
    """Main parser function."""
    parser = LikeStoreParser()
    
    try:
        await parser.init()
        
        # Parse categories
        categories = await parser.parse_main_page()
        
        # Parse each category
        for category in categories[:3]:  # Limit to 3 categories for demo
            products = await parser.parse_category(category)
            parser.products.extend(products)
        
        # Export results
        filename = parser.export_data()
        
        print(f"\n🎉 Парсинг завершён!")
        print(f"   Товаров: {len(parser.products)}")
        print(f"   Категорий: {len(parser.categories)}")
        print(f"   Файл: {filename}")
        
    finally:
        await parser.close()


if __name__ == "__main__":
    asyncio.run(main())
