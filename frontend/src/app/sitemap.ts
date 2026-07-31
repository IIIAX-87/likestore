import { MetadataRoute } from "next";
import { productsAPI, categoriesAPI } from "@/lib/api";

const BASE_URL = "https://likestore.ru";

interface CategoryItem {
	slug: string;
	name?: string;
}

interface ProductItem {
	slug: string;
	updated_at?: string;
}

async function getCategories(): Promise<CategoryItem[]> {
	try {
		const data = await categoriesAPI.tree();
		return (data || []) as CategoryItem[];
	} catch {
		return [];
	}
}

async function getProducts(): Promise<ProductItem[]> {
	try {
		const data = await productsAPI.list({ ordering: "-created_at" });
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const results = (data as any)?.results || data || [];
		return results.map((p: { slug: string; updated_at?: string }) => ({
			slug: p.slug,
			updated_at: p.updated_at,
		}));
	} catch {
		return [];
	}
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
	const [categories, products] = await Promise.all([
		getCategories(),
		getProducts(),
	]);

	const categoryUrls: MetadataRoute.Sitemap = categories.map(
		(cat: CategoryItem) => ({
			url: `${BASE_URL}/catalog/${cat.slug}/`,
			lastModified: new Date(),
			changeFrequency: "weekly",
			priority: 0.8,
		}),
	);

	const productUrls: MetadataRoute.Sitemap = products.map(
		(product: ProductItem) => ({
			url: `${BASE_URL}/product/${product.slug}/`,
			lastModified: product.updated_at
				? new Date(product.updated_at)
				: new Date(),
			changeFrequency: "daily",
			priority: 0.9,
		}),
	);

	return [
		{
			url: BASE_URL,
			lastModified: new Date(),
			changeFrequency: "daily",
			priority: 1,
		},
		{
			url: `${BASE_URL}/catalog/`,
			lastModified: new Date(),
			changeFrequency: "daily",
			priority: 0.9,
		},
		...categoryUrls,
		...productUrls,
	];
}
