"use client";

import Link from "next/link";
import { useCartStore, useWishlistStore } from "@/lib/store";
import { formatPrice } from "@/lib/utils";
import type { Product } from "@/lib/api";

interface ProductCardProps {
	product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
	const { addItem } = useCartStore();
	const {
		items: wishlistItems,
		addItem: addToWishlist,
		removeItem: removeFromWishlist,
	} = useWishlistStore();

	const isInWishlist = wishlistItems.includes(product.id);

	const handleAddToCart = async (e: React.MouseEvent) => {
		e.preventDefault();
		e.stopPropagation();
		try {
			await addItem(product.id);
		} catch (error) {
			console.error("Failed to add to cart:", error);
		}
	};

	const handleToggleWishlist = async (e: React.MouseEvent) => {
		e.preventDefault();
		e.stopPropagation();
		if (isInWishlist) {
			await removeFromWishlist(product.id);
		} else {
			await addToWishlist(product.id);
		}
	};

	const hasDiscount =
		product.old_price &&
		parseFloat(product.old_price) > parseFloat(product.price);
	const discountPercent = hasDiscount
		? Math.round(
				(1 - parseFloat(product.price) / parseFloat(product.old_price!)) * 100,
			)
		: 0;

	return (
		<article className="product-card">
			<Link href={`/product/${product.slug}/`} className="product-card__link">
				<div className="product-card__image">
					{product.main_image ? (
						<img src={product.main_image} alt={product.name} />
					) : (
						<div className="product-card__placeholder">📱</div>
					)}

					{hasDiscount && (
						<span className="product-card__badge product-card__badge--sale">
							-{discountPercent}%
						</span>
					)}

					{product.is_new && (
						<span className="product-card__badge product-card__badge--new">
							Новинка
						</span>
					)}

					{product.is_featured && (
						<span className="product-card__badge product-card__badge--hit">
							Хит
						</span>
					)}

					<button
						className={`product-card__wishlist ${isInWishlist ? "active" : ""}`}
						onClick={handleToggleWishlist}
						aria-label={
							isInWishlist ? "Удалить из избранного" : "Добавить в избранное"
						}
					>
						<svg
							viewBox="0 0 24 24"
							fill={isInWishlist ? "currentColor" : "none"}
							stroke="currentColor"
							strokeWidth="2"
						>
							<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
						</svg>
					</button>
				</div>

				<div className="product-card__content">
					<h3 className="product-card__title">{product.name}</h3>

					<div className="product-card__price">
						<span className="product-card__price-current">
							{formatPrice(product.price)}
						</span>
						{hasDiscount && (
							<span className="product-card__price-old">
								{formatPrice(product.old_price!)}
							</span>
						)}
					</div>

					{product.stock > 0 ? (
						<span className="product-card__stock product-card__stock--in">
							В наличии
						</span>
					) : (
						<span className="product-card__stock product-card__stock--out">
							Нет в наличии
						</span>
					)}
				</div>
			</Link>

			<button className="product-card__add-btn" onClick={handleAddToCart}>
				В корзину
			</button>
		</article>
	);
}
