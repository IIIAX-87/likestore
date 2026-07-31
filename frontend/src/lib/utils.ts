// Utility functions
export function formatPrice(price: string | number): string {
	const num = typeof price === "string" ? parseFloat(price) : price;
	return new Intl.NumberFormat("ru-RU", {
		style: "currency",
		currency: "RUB",
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	}).format(num);
}

export function formatDate(date: string): string {
	return new Intl.DateTimeFormat("ru-RU", {
		year: "numeric",
		month: "long",
		day: "numeric",
	}).format(new Date(date));
}

export function pluralize(
	count: number,
	forms: [string, string, string],
): string {
	const absCount = Math.abs(count);
	if (absCount === 0) return forms[2];
	const mod10 = absCount % 10;
	const mod100 = absCount % 100;
	if (mod10 === 1 && mod100 !== 11) return forms[0];
	if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20))
		return forms[1];
	return forms[2];
}

export function getImageUrl(url: string | null): string {
	if (!url) return "/placeholder.png";
	if (url.startsWith("http")) return url;
	return `${process.env.NEXT_PUBLIC_API_URL}${url}`;
}

export function slugify(text: string): string {
	return text
		.toLowerCase()
		.replace(/[^\w\s-]/g, "")
		.replace(/\s+/g, "-")
		.replace(/--+/g, "-")
		.trim();
}

export function truncate(text: string, maxLength: number): string {
	if (text.length <= maxLength) return text;
	return text.slice(0, maxLength).trim() + "...";
}
