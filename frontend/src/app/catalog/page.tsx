import ProductCard from "@/components/ProductCard";
import {
	productsAPI,
	categoriesAPI,
	type Product,
	type Category,
} from "@/lib/api";
import Link from "next/link";

async function getCatalogData() {
	try {
		const [categories, products] = await Promise.all([
			categoriesAPI.tree(),
			productsAPI.list({ ordering: "-created_at", page: "1" }),
		]);
		return { categories: categories || [], products: products.results || [] };
	} catch {
		return { categories: [], products: [] };
	}
}

export const metadata = {
	title: "Каталог - LikeStore",
	description:
		"Каталог товаров LikeStore. iPhone, MacBook, iPad, Apple Watch, AirPods и аксессуары.",
};

const mainCategories = [
	{
		name: "iPhone",
		slug: "iphone_1",
		icon: "📱",
		description: "Флагманские смартфоны Apple",
	},
	{
		name: "Samsung",
		slug: "samsung_1",
		icon: "📱",
		description: "Смартфоны Samsung",
	},
	{ name: "iPad", slug: "ipad", icon: "📲", description: "Планшеты Apple" },
	{
		name: "Watch",
		slug: "watch",
		icon: "⌚",
		description: "Умные часы Apple Watch",
	},
	{
		name: "AirPods",
		slug: "airpods_1",
		icon: "🎧",
		description: "Беспроводные наушники",
	},
	{
		name: "MacBook",
		slug: "macbook",
		icon: "💻",
		description: "Ноутбуки Apple",
	},
	{
		name: "Приставки",
		slug: "pristavki",
		icon: "🎮",
		description: "Игровые приставки",
	},
	{ name: "Dyson", slug: "dyson", icon: "💨", description: "Техника Dyson" },
	{
		name: "Аксессуары",
		slug: "aksessuary_1",
		icon: "🔌",
		description: "Чехлы, кабели, зарядки",
	},
];

export default async function CatalogPage() {
	const { categories, products } = await getCatalogData();

	return (
		<div className="catalog-page">
			<div className="container">
				<h1 className="section-title" style={{ marginBottom: "2rem" }}>
					Каталог товаров
				</h1>

				{/* Main Categories */}
				<section style={{ marginBottom: "3rem" }}>
					<h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>
						Категории
					</h2>
					<div className="categories-grid">
						{mainCategories.map((cat) => (
							<Link
								key={cat.slug}
								href={`/catalog/${cat.slug}/`}
								className="category-card"
							>
								<div className="category-card__icon">{cat.icon}</div>
								<h3 className="category-card__name">{cat.name}</h3>
								<p className="category-card__price">{cat.description}</p>
							</Link>
						))}
					</div>
				</section>

				{/* Featured Products */}
				{products.length > 0 && (
					<section className="products-section">
						<div className="products-header">
							<h2 className="section-title">Новинки</h2>
						</div>
						<div className="product-grid">
							{products.slice(0, 8).map((product: Product) => (
								<ProductCard key={product.id} product={product} />
							))}
						</div>
					</section>
				)}
			</div>
		</div>
	);
}
