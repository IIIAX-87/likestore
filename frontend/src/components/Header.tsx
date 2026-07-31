"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useCartStore } from "@/lib/store";

const categories = [
	{
		name: "iPhone",
		slug: "iphone_1",
		subcategories: [
			"iPhone 17",
			"iPhone 16",
			"iPhone 15",
			"iPhone 14",
			"iPhone 13",
		],
	},
	{
		name: "Samsung",
		slug: "samsung_1",
		subcategories: ["Samsung A", "Samsung S", "Samsung Z", "Наушники Samsung"],
	},
	{
		name: "iPad",
		slug: "ipad",
		subcategories: ["iPad Air", "iPad", "iPad Pro"],
	},
	{
		name: "Watch",
		slug: "watch",
		subcategories: [
			"Apple Watch Series 11",
			"Apple Watch SE",
			"Apple Watch Ultra",
		],
	},
	{
		name: "AirPods",
		slug: "airpods_1",
		subcategories: [
			"AirPods Pro 2",
			"AirPods Max",
			"AirPods 4",
			"AirPods Pro 3",
		],
	},
	{
		name: "MacBook",
		slug: "macbook",
		subcategories: ["MacBook Neo", "MacBook Pro", "MacBook Air"],
	},
	{
		name: "Приставки",
		slug: "pristavki",
		subcategories: [
			"Nintendo Switch",
			"Sony PlayStation",
			"Steam Deck",
			"Xbox",
		],
	},
	{ name: "Dyson", slug: "dyson", subcategories: ["Стайлер Dyson"] },
	{
		name: "Аксессуары",
		slug: "aksessuary_1",
		subcategories: ["Чехлы", "Защитные стёкла", "Кабели", "Ремешки"],
	},
];

export default function Header() {
	const [isCatalogOpen, setIsCatalogOpen] = useState(false);
	const [isCartOpen, setIsCartOpen] = useState(false);
	const { cart, fetchCart } = useCartStore();

	useEffect(() => {
		fetchCart();
	}, [fetchCart]);

	const itemsCount = cart?.items_count || 0;

	return (
		<header className="header">
			<div className="header-top">
				<div className="container">
					<div className="header-top__city">
						<svg
							className="icon"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
						>
							<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
							<circle cx="12" cy="9" r="2.5" />
						</svg>
						<span>Ханты-Мансийск</span>
					</div>
					<nav className="header-top__nav">
						<Link href="/garantiya/">Гарантия</Link>
						<Link href="/stock/">Акции</Link>
						<Link href="/trade-in/">TradeIn/Обмен</Link>
						<Link href="/contacts/">Контакты</Link>
						<Link href="/about/">О компании</Link>
					</nav>
					<div className="header-top__contact">
						<a href="tel:+79324065333">+7 (932) 406-53-33</a>
					</div>
				</div>
			</div>

			<div className="header-main">
				<div className="container">
					<Link href="/" className="logo">
						<svg viewBox="0 0 205 40" width="180" height="35">
							<path
								d="M12.4902 0L24.9804 8.17338L37.4705 0L50.0574 8.11834L24.9804 23.9972L0 8.22841L12.4902 0Z"
								fill="#16B0BF"
							/>
							<path
								d="M24.9665 23.9835L0 8.22842V23.9835L24.9804 39.9862V23.9835H24.9665Z"
								fill="#24D8FF"
							/>
							<path
								d="M50.0575 8.13208L24.9805 23.9835V40L50.0575 24.0385V8.13208Z"
								fill="white"
							/>
						</svg>
					</Link>

					<nav className="header-nav">
						{categories.slice(0, 7).map((cat) => (
							<Link
								key={cat.slug}
								href={`/catalog/${cat.slug}/`}
								className="nav-link"
							>
								{cat.name}
							</Link>
						))}
						<button
							className="nav-link nav-link--catalog"
							onClick={() => setIsCatalogOpen(!isCatalogOpen)}
						>
							Каталог
						</button>
					</nav>

					<div className="header-actions">
						<button className="action-btn" aria-label="Поиск">
							<svg
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								strokeWidth="2"
							>
								<circle cx="11" cy="11" r="8" />
								<path d="M21 21l-4.35-4.35" />
							</svg>
						</button>
						<button
							className="action-btn"
							aria-label="Корзина"
							onClick={() => setIsCartOpen(true)}
						>
							<svg
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								strokeWidth="2"
							>
								<path d="M6 6h15l-1.5 9h-12z" />
								<circle cx="9" cy="20" r="1" />
								<circle cx="18" cy="20" r="1" />
								<path d="M6 6L5 2H2" />
							</svg>
							{itemsCount > 0 && (
								<span className="cart-count">{itemsCount}</span>
							)}
						</button>
					</div>
				</div>
			</div>

			{/* Mobile Header */}
			<div className="header-mobile">
				<Link href="/" className="logo">
					<svg viewBox="0 0 205 40" width="150" height="30">
						<path
							d="M12.4902 0L24.9804 8.17338L37.4705 0L50.0574 8.11834L24.9804 23.9972L0 8.22841L12.4902 0Z"
							fill="#16B0BF"
						/>
						<path
							d="M24.9665 23.9835L0 8.22842V23.9835L24.9804 39.9862V23.9835H24.9665Z"
							fill="#24D8FF"
						/>
						<path
							d="M50.0575 8.13208L24.9805 23.9835V40L50.0575 24.0385V8.13208Z"
							fill="white"
						/>
					</svg>
				</Link>
				<div className="header-mobile__actions">
					<button className="action-btn" aria-label="Поиск">
						<svg
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
						>
							<circle cx="11" cy="11" r="8" />
							<path d="M21 21l-4.35-4.35" />
						</svg>
					</button>
					<button className="action-btn" onClick={() => setIsCartOpen(true)}>
						<svg
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
						>
							<path d="M6 6h15l-1.5 9h-12z" />
							<circle cx="9" cy="20" r="1" />
							<circle cx="18" cy="20" r="1" />
						</svg>
						{itemsCount > 0 && <span className="cart-count">{itemsCount}</span>}
					</button>
					<button
						className="action-btn"
						onClick={() => setIsCatalogOpen(!isCatalogOpen)}
					>
						<svg
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
						>
							<path d="M3 12h18M3 6h18M3 18h18" />
						</svg>
					</button>
				</div>
			</div>

			{/* Catalog Dropdown */}
			{isCatalogOpen && (
				<div className="catalog-dropdown">
					<div className="container">
						<div className="catalog-grid">
							{categories.map((cat) => (
								<div key={cat.slug} className="catalog-section">
									<Link
										href={`/catalog/${cat.slug}/`}
										className="catalog-section__title"
									>
										{cat.name}
									</Link>
									<div className="catalog-section__items">
										{cat.subcategories.map((sub) => (
											<Link
												key={sub}
												href={`/catalog/${cat.slug}/`}
												className="catalog-section__item"
											>
												{sub}
											</Link>
										))}
									</div>
								</div>
							))}
						</div>
					</div>
					<button
						className="catalog-close"
						onClick={() => setIsCatalogOpen(false)}
					>
						✕
					</button>
				</div>
			)}

			{/* Cart Drawer */}
			{isCartOpen && <CartDrawer onClose={() => setIsCartOpen(false)} />}
		</header>
	);
}

function CartDrawer({ onClose }: { onClose: () => void }) {
	const { cart, updateItem, removeItem } = useCartStore();

	return (
		<div className="cart-overlay" onClick={onClose}>
			<div className="cart-drawer" onClick={(e) => e.stopPropagation()}>
				<div className="cart-drawer__header">
					<h2>Корзина</h2>
					<button className="cart-drawer__close" onClick={onClose}>
						✕
					</button>
				</div>

				{cart?.items && cart.items.length > 0 ? (
					<>
						<div className="cart-drawer__items">
							{cart.items.map((item) => (
								<div key={item.id} className="cart-item">
									<div className="cart-item__image">
										{item.product.main_image ? (
											<img
												src={item.product.main_image}
												alt={item.product.name}
											/>
										) : (
											<div className="cart-item__placeholder">📱</div>
										)}
									</div>
									<div className="cart-item__info">
										<h3>{item.product.name}</h3>
										<p className="cart-item__price">{item.price} ₽</p>
										<div className="cart-item__quantity">
											<button
												onClick={() => updateItem(item.id, item.quantity - 1)}
											>
												−
											</button>
											<span>{item.quantity}</span>
											<button
												onClick={() => updateItem(item.id, item.quantity + 1)}
											>
												+
											</button>
										</div>
									</div>
									<button
										className="cart-item__remove"
										onClick={() => removeItem(item.id)}
									>
										✕
									</button>
								</div>
							))}
						</div>
						<div className="cart-drawer__footer">
							<div className="cart-drawer__total">
								<span>Итого:</span>
								<span>{cart.subtotal} ₽</span>
							</div>
							<Link
								href="/checkout/"
								className="btn btn--primary"
								onClick={onClose}
							>
								Оформить заказ
							</Link>
						</div>
					</>
				) : (
					<div className="cart-drawer__empty">
						<p>Корзина пуста</p>
						<button className="btn btn--secondary" onClick={onClose}>
							Продолжить покупки
						</button>
					</div>
				)}
			</div>
		</div>
	);
}
