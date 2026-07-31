import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import { productsAPI, type Product } from "@/lib/api";

const categories = [
	{ name: "iPhone", slug: "iphone_1", icon: "📱", from: "от 44 490 ₽" },
	{ name: "Samsung", slug: "samsung_1", icon: "📱", from: "от 8 490 ₽" },
	{ name: "iPad", slug: "ipad", icon: "📲", from: "от 30 990 ₽" },
	{ name: "Watch", slug: "watch", icon: "⌚", from: "от 22 490 ₽" },
	{ name: "AirPods", slug: "airpods_1", icon: "🎧", from: "от 12 490 ₽" },
	{ name: "MacBook", slug: "macbook", icon: "💻", from: "от 54 490 ₽" },
	{ name: "Приставки", slug: "pristavki", icon: "🎮", from: "от 7 490 ₽" },
	{ name: "Dyson", slug: "dyson", icon: "💨", from: "от 34 490 ₽" },
];

async function getFeaturedProducts() {
	try {
		const data = await productsAPI.featured();
		return data.results || data || [];
	} catch {
		return [];
	}
}

async function getBestsellers() {
	try {
		const data = await productsAPI.bestsellers();
		return data.results || data || [];
	} catch {
		return [];
	}
}

export default async function HomePage() {
	const featuredProducts = await getFeaturedProducts();
	const bestsellers = await getBestsellers();

	return (
		<>
			{/* Hero Section */}
			<section className="hero">
				<div className="container">
					<h1>LikeStore — техника Apple в Ханты-Мансийске</h1>
					<p>
						Оригинальная продукция Apple с гарантией 1 год. Trade-in, бесплатная
						доставка, бонусная программа.
					</p>
					<Link href="/catalog/" className="btn btn--primary">
						Перейти в каталог
					</Link>
				</div>
			</section>

			{/* Features */}
			<section className="features">
				<div className="container">
					<div className="features-grid">
						<div className="feature-card">
							<div className="feature-card__icon">🛡️</div>
							<h3 className="feature-card__title">Гарантия</h3>
							<p className="feature-card__description">
								Можно не переживать целый год из-за поломки техники
							</p>
						</div>
						<div className="feature-card">
							<div className="feature-card__icon">🚚</div>
							<h3 className="feature-card__title">Бесплатная доставка</h3>
							<p className="feature-card__description">
								Доставим заказ бесплатно по городу
							</p>
						</div>
						<div className="feature-card">
							<div className="feature-card__icon">🔄</div>
							<h3 className="feature-card__title">TradeIn/Обмен</h3>
							<p className="feature-card__description">
								Узнай свою выгоду за пару кликов
							</p>
						</div>
					</div>
				</div>
			</section>

			{/* Categories */}
			<section className="categories">
				<div className="container">
					<h2 className="section-title">Каталог</h2>
					<div className="categories-grid">
						{categories.map((cat) => (
							<Link
								key={cat.slug}
								href={`/catalog/${cat.slug}/`}
								className="category-card"
							>
								<div className="category-card__icon">{cat.icon}</div>
								<h3 className="category-card__name">{cat.name}</h3>
								<p className="category-card__price">{cat.from}</p>
							</Link>
						))}
					</div>
				</div>
			</section>

			{/* Featured Products */}
			{featuredProducts.length > 0 && (
				<section className="products-section">
					<div className="container">
						<div className="products-header">
							<h2 className="section-title">Хиты продаж</h2>
							<Link
								href="/catalog/?featured=true"
								className="btn btn--secondary"
							>
								Все товары
							</Link>
						</div>
						<div className="product-grid">
							{featuredProducts.slice(0, 8).map((product: Product) => (
								<ProductCard key={product.id} product={product} />
							))}
						</div>
					</div>
				</section>
			)}

			{/* Bestsellers */}
			{bestsellers.length > 0 && (
				<section className="products-section" style={{ background: "#f8f9fa" }}>
					<div className="container">
						<div className="products-header">
							<h2 className="section-title">Бестселлеры</h2>
						</div>
						<div className="product-grid">
							{bestsellers.slice(0, 8).map((product: Product) => (
								<ProductCard key={product.id} product={product} />
							))}
						</div>
					</div>
				</section>
			)}
		</>
	);
}
