"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { productsAPI, type Product } from "@/lib/api";
import { useCartStore } from "@/lib/store";
import { formatPrice } from "@/lib/utils";
import ProductCard from "@/components/ProductCard";

export default function ProductPage() {
	const params = useParams();
	const slug = params.slug as string;

	const [product, setProduct] = useState<Product | null>(null);
	const [relatedProducts, setRelatedProducts] = useState<Product[]>([]);
	const [selectedImage, setSelectedImage] = useState(0);
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const { addItem } = useCartStore();

	useEffect(() => {
		async function loadProduct() {
			try {
				setIsLoading(true);
				const [productData, related] = await Promise.all([
					productsAPI.detail(slug),
					productsAPI.related(slug),
				]);
				setProduct(productData);
				setRelatedProducts(related.results || related || []);
			} catch (err) {
				setError("Товар не найден");
			} finally {
				setIsLoading(false);
			}
		}

		if (slug) {
			loadProduct();
		}
	}, [slug]);

	const handleAddToCart = async () => {
		if (!product) return;
		try {
			await addItem(product.id);
		} catch (err) {
			console.error("Failed to add to cart:", err);
		}
	};

	if (isLoading) {
		return (
			<div className="loading">
				<div className="spinner" />
			</div>
		);
	}

	if (error || !product) {
		return (
			<div
				className="container"
				style={{ padding: "4rem 0", textAlign: "center" }}
			>
				<h1>Товар не найден</h1>
				<Link
					href="/catalog/"
					className="btn btn--primary"
					style={{ marginTop: "1rem" }}
				>
					Вернуться в каталог
				</Link>
			</div>
		);
	}

	const images = product.images?.length
		? product.images.map((img) => img.image_url || img.image)
		: [product.main_image].filter(Boolean);

	const hasDiscount =
		product.old_price &&
		parseFloat(product.old_price) > parseFloat(product.price);

	return (
		<>
			<div className="product-detail">
				<div className="container">
					<nav
						className="breadcrumbs"
						style={{
							marginBottom: "1rem",
							fontSize: "0.875rem",
							color: "#666",
						}}
					>
						<Link href="/">Главная</Link>
						<span style={{ margin: "0 0.5rem" }}>/</span>
						<Link href="/catalog/">Каталог</Link>
						{product.category && (
							<>
								<span style={{ margin: "0 0.5rem" }}>/</span>
								<Link href={`/catalog/${product.category.slug}/`}>
									{product.category.name}
								</Link>
							</>
						)}
						<span style={{ margin: "0 0.5rem" }}>/</span>
						<span>{product.name}</span>
					</nav>

					<div className="product-detail-layout">
						<div className="product-gallery">
							<div className="product-gallery__main">
								{images[selectedImage] ? (
									<img src={images[selectedImage]} alt={product.name} />
								) : (
									<div style={{ fontSize: "6rem" }}>📱</div>
								)}
							</div>
							{images.length > 1 && (
								<div className="product-gallery__thumbs">
									{images.map((img, idx) => (
										<button
											key={idx}
											className={`product-gallery__thumb ${idx === selectedImage ? "active" : ""}`}
											onClick={() => setSelectedImage(idx)}
										>
											<img src={img || ""} alt={`${product.name} ${idx + 1}`} />
										</button>
									))}
								</div>
							)}
						</div>

						<div className="product-info">
							<div className="product-info__header">
								{product.brand && (
									<p className="product-info__brand">{product.brand.name}</p>
								)}
								<h1 className="product-info__title">{product.name}</h1>
								{product.article && (
									<p className="product-info__article">
										Артикул: {product.article}
									</p>
								)}
							</div>

							<div className="product-info__price">
								<span className="product-info__price-current">
									{formatPrice(product.price)}
								</span>
								{hasDiscount && (
									<span className="product-info__price-old">
										{formatPrice(product.old_price!)}
									</span>
								)}
							</div>

							<div className="product-info__description">
								<p>{product.description || product.short_description}</p>
							</div>

							{product.specifications && product.specifications.length > 0 && (
								<div className="product-info__specs">
									<h3>Характеристики</h3>
									<div className="specs-list">
										{product.specifications.map((spec) => (
											<div key={spec.id} className="specs-item">
												<span className="specs-item__name">{spec.name}</span>
												<span className="specs-item__value">{spec.value}</span>
											</div>
										))}
									</div>
								</div>
							)}

							<div className="product-info__actions">
								<button
									className="btn btn--primary product-info__add-btn"
									onClick={handleAddToCart}
									disabled={!product.in_stock}
								>
									{product.in_stock ? "В корзину" : "Нет в наличии"}
								</button>
							</div>
						</div>
					</div>

					{relatedProducts.length > 0 && (
						<section style={{ marginTop: "4rem" }}>
							<h2 className="section-title">Похожие товары</h2>
							<div className="product-grid">
								{relatedProducts.slice(0, 4).map((p) => (
									<ProductCard key={p.id} product={p} />
								))}
							</div>
						</section>
					)}
				</div>
			</div>
		</>
	);
}
