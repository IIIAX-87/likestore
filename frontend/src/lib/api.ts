// API Configuration
export const API_URL =
	process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Types
export interface Product {
	id: number;
	name: string;
	slug: string;
	article: string;
	brand: Brand | null;
	brand_name: string | null;
	category: Category | null;
	category_name: string | null;
	description: string;
	short_description: string;
	price: string;
	old_price: string | null;
	discount_percent: number;
	stock: number;
	in_stock: boolean;
	is_featured: boolean;
	is_bestseller: boolean;
	is_new: boolean;
	main_image: string | null;
	images?: ProductImage[];
	specifications?: ProductSpecification[];
	variants?: ProductVariant[];
}

export interface ProductImage {
	id: number;
	image: string;
	image_url: string;
	alt_text: string;
	is_main: boolean;
	order: number;
}

export interface ProductSpecification {
	id: number;
	name: string;
	value: string;
}

export interface ProductVariant {
	id: number;
	name: string;
	sku: string;
	price_modifier: string;
	stock: number;
	attributes: Record<string, string>;
	is_active: boolean;
	final_price: string;
}

export interface Brand {
	id: number;
	name: string;
	slug: string;
	logo: string | null;
	description: string;
	website: string;
}

export interface Category {
	id: number;
	name: string;
	slug: string;
	image: string | null;
	children?: Category[];
	product_count?: number;
}

export interface CartItem {
	id: number;
	product: Product;
	variant: ProductVariant | null;
	variant_name?: string;
	quantity: number;
	price: string;
	total: string;
}

export interface Cart {
	id: number;
	items: CartItem[];
	items_count: number;
	subtotal: string;
	created_at: string;
	updated_at: string;
}

export interface Order {
	id: number;
	first_name: string;
	last_name: string;
	email: string;
	phone: string;
	city: string;
	address: string;
	postal_code: string;
	status: string;
	payment_method: string;
	delivery_type: string;
	subtotal: string;
	delivery_cost: string;
	total: string;
	discount: string;
	comment: string;
	created_at: string;
	items: OrderItem[];
}

export interface OrderItem {
	id: number;
	product: number | null;
	product_name: string;
	product_sku: string;
	variant_name: string;
	quantity: number;
	price: string;
	total: string;
}

// API Functions
async function fetchAPI(endpoint: string, options: RequestInit = {}) {
	const url = `${API_URL}${endpoint}`;
	const config: RequestInit = {
		...options,
		headers: {
			"Content-Type": "application/json",
			...options.headers,
		},
	};

	const response = await fetch(url, config);

	if (!response.ok) {
		throw new Error(`API Error: ${response.status}`);
	}

	return response.json();
}

// Products API
export const productsAPI = {
	list: (params?: Record<string, string>) => {
		const query = params ? "?" + new URLSearchParams(params).toString() : "";
		return fetchAPI(`/products/${query}`);
	},

	detail: (slug: string) => fetchAPI(`/products/${slug}/`),

	featured: () => fetchAPI("/products/featured/"),

	bestsellers: () => fetchAPI("/products/bestsellers/"),

	new: () => fetchAPI("/products/new/"),

	search: (query: string) =>
		fetchAPI(`/products/search/?q=${encodeURIComponent(query)}`),

	related: (slug: string) => fetchAPI(`/products/${slug}/related/`),
};

// Categories API
export const categoriesAPI = {
	list: () => fetchAPI("/products/categories/"),

	tree: () => fetchAPI("/products/categories/tree/"),

	detail: (slug: string) => fetchAPI(`/products/categories/${slug}/`),

	products: (slug: string, params?: Record<string, string>) => {
		const query = params ? "?" + new URLSearchParams(params).toString() : "";
		return fetchAPI(`/products/categories/${slug}/products/${query}`);
	},
};

// Brands API
export const brandsAPI = {
	list: () => fetchAPI("/products/brands/"),

	detail: (slug: string) => fetchAPI(`/products/brands/${slug}/`),

	products: (slug: string) => fetchAPI(`/products/brands/${slug}/products/`),
};

// Cart API
export const cartAPI = {
	get: () => fetchAPI("/cart/"),

	addItem: (data: {
		product_id: number;
		variant_id?: number;
		quantity?: number;
	}) =>
		fetchAPI("/cart/add_item/", { method: "POST", body: JSON.stringify(data) }),

	updateItem: (itemId: number, quantity: number) =>
		fetchAPI("/cart/update_item/", {
			method: "POST",
			body: JSON.stringify({ item_id: itemId, quantity }),
		}),

	removeItem: (itemId: number) =>
		fetchAPI("/cart/remove_item/", {
			method: "POST",
			body: JSON.stringify({ item_id: itemId }),
		}),

	clear: () => fetchAPI("/cart/clear/", { method: "POST" }),
};

// Wishlist API
export const wishlistAPI = {
	get: () => fetchAPI("/cart/wishlist/"),

	add: (productId: number) =>
		fetchAPI("/cart/wishlist/add/", {
			method: "POST",
			body: JSON.stringify({ product_id: productId }),
		}),

	remove: (productId: number) =>
		fetchAPI("/cart/wishlist/remove/", {
			method: "POST",
			body: JSON.stringify({ product_id: productId }),
		}),
};

// Orders API
export const ordersAPI = {
	create: (data: {
		first_name: string;
		last_name: string;
		email: string;
		phone: string;
		city?: string;
		address?: string;
		postal_code?: string;
		payment_method?: string;
		delivery_type?: string;
		comment?: string;
		cart_id?: number;
	}) => fetchAPI("/orders/", { method: "POST", body: JSON.stringify(data) }),

	list: () => fetchAPI("/orders/"),

	detail: (id: number) => fetchAPI(`/orders/${id}/`),

	byEmail: (email: string) =>
		fetchAPI(`/orders/by_email/?email=${encodeURIComponent(email)}`),

	cancel: (id: number) => fetchAPI(`/orders/${id}/cancel/`, { method: "POST" }),
};

// Auth API
export const authAPI = {
	register: (data: {
		email: string;
		password: string;
		password_confirm: string;
		first_name?: string;
		last_name?: string;
		phone?: string;
	}) =>
		fetchAPI("/users/auth/register/", {
			method: "POST",
			body: JSON.stringify(data),
		}),

	login: (email: string, password: string) =>
		fetchAPI("/users/auth/login/", {
			method: "POST",
			body: JSON.stringify({ email, password }),
		}),

	logout: () => fetchAPI("/users/auth/logout/", { method: "POST" }),

	refresh: (refreshToken: string) =>
		fetchAPI("/users/auth/refresh/", {
			method: "POST",
			body: JSON.stringify({ refresh: refreshToken }),
		}),

	passwordResetRequest: (email: string) =>
		fetchAPI("/users/auth/password_reset_request/", {
			method: "POST",
			body: JSON.stringify({ email }),
		}),

	passwordResetConfirm: (token: string, newPassword: string) =>
		fetchAPI("/users/auth/password_reset_confirm/", {
			method: "POST",
			body: JSON.stringify({ token, new_password: newPassword }),
		}),
};
