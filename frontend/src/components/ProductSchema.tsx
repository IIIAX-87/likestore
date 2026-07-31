// Schema.org JSON-LD компоненты для SEO

interface ProductSchemaProps {
	product: {
		id: number;
		name: string;
		slug: string;
		description: string;
		price: string;
		old_price?: string | null;
		brand?: { name: string } | null;
		category?: { name: string } | null;
		main_image?: string | null;
		in_stock?: boolean;
		sku?: string;
	};
	url: string;
}

export function ProductSchema({ product, url }: ProductSchemaProps) {
	const schema = {
		"@context": "https://schema.org",
		"@type": "Product",
		name: product.name,
		description: product.description,
		url: url,
		sku: product.sku || String(product.id),
		image: product.main_image ? [product.main_image] : [],
		brand: product.brand
			? {
					"@type": "Brand",
					name: product.brand.name,
				}
			: undefined,
		category: product.category?.name,
		offers: {
			"@type": "Offer",
			price: product.price.replace(/[^\d.]/g, ""),
			priceCurrency: "RUB",
			availability: product.in_stock
				? "https://schema.org/InStock"
				: "https://schema.org/OutOfStock",
			seller: {
				"@type": "Organization",
				name: "LikeStore",
			},
		},
	};

	return (
		<script
			type="application/ld+json"
			dangerouslySetInnerHTML={{ __html: JSON.stringify(schema, null, 0) }}
		/>
	);
}

interface BreadcrumbSchemaProps {
	items: Array<{ name: string; url: string }>;
}

export function BreadcrumbSchema({ items }: BreadcrumbSchemaProps) {
	const schema = {
		"@context": "https://schema.org",
		"@type": "BreadcrumbList",
		itemListElement: items.map((item, index) => ({
			"@type": "ListItem",
			position: index + 1,
			name: item.name,
			item: item.url,
		})),
	};

	return (
		<script
			type="application/ld+json"
			dangerouslySetInnerHTML={{ __html: JSON.stringify(schema, null, 0) }}
		/>
	);
}

interface OrganizationSchemaProps {
	name: string;
	url: string;
	logo: string;
	phone: string;
	address: {
		streetAddress: string;
		addressLocality: string;
		postalCode: string;
		addressCountry: string;
	};
}

export function OrganizationSchema({
	name,
	url,
	logo,
	phone,
	address,
}: OrganizationSchemaProps) {
	const schema = {
		"@context": "https://schema.org",
		"@type": "Organization",
		name: name,
		url: url,
		logo: logo,
		telephone: phone,
		address: {
			"@type": "PostalAddress",
			...address,
		},
		sameAs: ["https://t.me/likestore_shop", "https://wa.me/79324065333"],
	};

	return (
		<script
			type="application/ld+json"
			dangerouslySetInnerHTML={{ __html: JSON.stringify(schema, null, 0) }}
		/>
	);
}

interface ProductListSchemaProps {
	products: Array<{
		id: number;
		name: string;
		slug: string;
		price: string;
		main_image?: string | null;
	}>;
	name: string;
	description: string;
	url: string;
}

export function ProductListSchema({
	products,
	name,
	description,
	url,
}: ProductListSchemaProps) {
	const schema = {
		"@context": "https://schema.org",
		"@type": "ItemList",
		name: name,
		description: description,
		url: url,
		itemListElement: products.map((product, index) => ({
			"@type": "ListItem",
			position: index + 1,
			url: `${url}/${product.slug}/`,
			name: product.name,
			image: product.main_image,
		})),
	};

	return (
		<script
			type="application/ld+json"
			dangerouslySetInnerHTML={{ __html: JSON.stringify(schema, null, 0) }}
		/>
	);
}
