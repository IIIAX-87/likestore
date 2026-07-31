import ProductCard from "@/components/ProductCard";
import {
	productsAPI,
	categoriesAPI,
	type Product,
	type Category,
} from "@/lib/api";
import Link from "next/link";

interface CategoryPageProps {
	params: Promise<{ category: string }>;
	searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

async function getCategoryData(
	slug: string,
	params: { [key: string]: string },
) {
	try {
		const category = await categoriesAPI.detail(slug);
		const products = await categoriesAPI.products(slug, params);
		return { category, products };
	} catch {
		return { category: null, products: { results: [], count: 0 } };
	}
}

export async function generateMetadata({ params }: CategoryPageProps) {
	const resolvedParams = await params;
	const { category } = await getCategoryData(resolvedParams.category, {});

	return {
		title: category?.name
			? `${category.name} - LikeStore`
			: "Каталог - LikeStore",
		description: category?.name
			? `Купить ${category.name} в Ханты-Мансийске. Оригинальная техника с гарантией.`
			: "Каталог товаров LikeStore",
	};
}

export default async function CategoryPage({
	params,
	searchParams,
}: CategoryPageProps) {
	const resolvedParams = await params;
	const resolvedSearchParams = await searchParams;

	const page =
		typeof resolvedSearchParams.page === "string"
			? parseInt(resolvedSearchParams.page)
			: 1;
	const ordering =
		typeof resolvedSearchParams.ordering === "string"
			? resolvedSearchParams.ordering
			: "-created_at";

	const queryParams: { [key: string]: string } = {
		ordering,
		page: String(page),
	};

	const { category, products } = await getCategoryData(
		resolvedParams.category,
		queryParams,
	);

	const productList: Product[] = products.results || [];
	const totalCount = products.count || 0;
	const totalPages = Math.ceil(totalCount / 20);

	const sortOptions = [
		{ value: "-created_at", label: "По новизне" },
		{ value: "price", label: "Сначала дешевле" },
		{ value: "-price", label: "Сначала дороже" },
		{ value: "name", label: "По названию" },
	];

	return (
		<div className="catalog-page">
			<div className="container">
				{/* Breadcrumbs */}
				<nav
					className="breadcrumbs"
					style={{ marginBottom: "1rem", fontSize: "0.875rem", color: "#666" }}
				>
					<Link href="/">Главная</Link>
					<span style={{ margin: "0 0.5rem" }}>/</span>
					<Link href="/catalog/">Каталог</Link>
					{category && (
						<>
							<span style={{ margin: "0 0.5rem" }}>/</span>
							<span>{category.name}</span>
						</>
					)}
				</nav>

				<div className="catalog-layout">
					{/* Sidebar */}
					<aside className="catalog-sidebar">
						<div className="filter-section">
							<h3>Бренды</h3>
							<div className="filter-options">
								<label className="filter-option">
									<input type="checkbox" />
									<span>Apple</span>
								</label>
								<label className="filter-option">
									<input type="checkbox" />
									<span>Samsung</span>
								</label>
							</div>
						</div>

						<div className="filter-section">
							<h3>Цена</h3>
							<div style={{ display: "flex", gap: "0.5rem" }}>
								<input
									type="number"
									placeholder="От"
									style={{
										width: "100%",
										padding: "0.5rem",
										border: "1px solid #e0e0e0",
										borderRadius: "4px",
									}}
								/>
								<input
									type="number"
									placeholder="До"
									style={{
										width: "100%",
										padding: "0.5rem",
										border: "1px solid #e0e0e0",
										borderRadius: "4px",
									}}
								/>
							</div>
						</div>

						{category?.children && category.children.length > 0 && (
							<div className="filter-section">
								<h3>Подкатегории</h3>
								<div className="filter-options">
									{category.children.map((child: Category) => (
										<Link
											key={child.id}
											href={`/catalog/${child.slug}/`}
											style={{
												color: "#666",
												marginBottom: "0.25rem",
												display: "block",
											}}
										>
											{child.name}
										</Link>
									))}
								</div>
							</div>
						)}
					</aside>

					{/* Main Content */}
					<div className="catalog-content">
						<div className="catalog-header">
							<h1 className="catalog-title">
								{category?.name || "Каталог товаров"}
							</h1>

							<div className="catalog-sort">
								<span>Сортировка:</span>
								<select
									defaultValue={ordering}
									onChange={(e) => {
										const url = new URL(window.location.href);
										url.searchParams.set("ordering", e.target.value);
										window.location.href = url.toString();
									}}
								>
									{sortOptions.map((opt) => (
										<option key={opt.value} value={opt.value}>
											{opt.label}
										</option>
									))}
								</select>
							</div>
						</div>

						{productList.length > 0 ? (
							<>
								<div className="product-grid">
									{productList.map((product) => (
										<ProductCard key={product.id} product={product} />
									))}
								</div>

								{totalPages > 1 && (
									<nav className="pagination">
										{page > 1 && (
											<Link
												href={`/catalog/${resolvedParams.category}/?page=${page - 1}`}
											>
												←
											</Link>
										)}
										{Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
											const pageNum = Math.max(1, page - 2) + i;
											if (pageNum > totalPages) return null;
											return (
												<Link
													key={pageNum}
													href={`/catalog/${resolvedParams.category}/?page=${pageNum}`}
													style={{
														background:
															pageNum === page
																? "var(--color-primary)"
																: undefined,
														color: pageNum === page ? "#fff" : undefined,
													}}
												>
													{pageNum}
												</Link>
											);
										})}
										{page < totalPages && (
											<Link
												href={`/catalog/${resolvedParams.category}/?page=${page + 1}`}
											>
												→
											</Link>
										)}
									</nav>
								)}
							</>
						) : (
							<div className="empty">
								<p>Товары не найдены</p>
								<Link href="/catalog/" className="btn btn--secondary">
									Посмотреть весь каталог
								</Link>
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}
