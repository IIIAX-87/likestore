"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCartStore } from "@/lib/store";
import { ordersAPI } from "@/lib/api";

export default function CheckoutPage() {
	const router = useRouter();
	const { cart, clearCart } = useCartStore();
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const [formData, setFormData] = useState({
		first_name: "",
		last_name: "",
		email: "",
		phone: "",
		city: "",
		address: "",
		postal_code: "",
		payment_method: "cash",
		delivery_type: "pickup",
		comment: "",
	});

	const handleChange = (
		e: React.ChangeEvent<
			HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
		>,
	) => {
		setFormData((prev) => ({
			...prev,
			[e.target.name]: e.target.value,
		}));
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsSubmitting(true);
		setError(null);

		try {
			const order = await ordersAPI.create({
				...formData,
				cart_id: cart?.id,
			});

			await clearCart();
			router.push(`/checkout/success/?order_id=${order.id}`);
		} catch (err) {
			setError("Произошла ошибка при оформлении заказа. Попробуйте еще раз.");
		} finally {
			setIsSubmitting(false);
		}
	};

	if (!cart || cart.items.length === 0) {
		return (
			<div
				className="container"
				style={{ padding: "4rem 0", textAlign: "center" }}
			>
				<h1>Корзина пуста</h1>
				<Link
					href="/catalog/"
					className="btn btn--primary"
					style={{ marginTop: "1rem" }}
				>
					Перейти в каталог
				</Link>
			</div>
		);
	}

	return (
		<div className="checkout-page">
			<div className="container">
				<h1 className="section-title" style={{ marginBottom: "2rem" }}>
					Оформление заказа
				</h1>

				<div className="checkout-layout">
					<form onSubmit={handleSubmit}>
						{error && (
							<div className="error" style={{ marginBottom: "1rem" }}>
								{error}
							</div>
						)}

						<div className="checkout-section">
							<h2>Контактные данные</h2>
							<div className="form-row">
								<div className="form-group">
									<label htmlFor="first_name">Имя *</label>
									<input
										type="text"
										id="first_name"
										name="first_name"
										value={formData.first_name}
										onChange={handleChange}
										required
									/>
								</div>
								<div className="form-group">
									<label htmlFor="last_name">Фамилия *</label>
									<input
										type="text"
										id="last_name"
										name="last_name"
										value={formData.last_name}
										onChange={handleChange}
										required
									/>
								</div>
							</div>
							<div className="form-row">
								<div className="form-group">
									<label htmlFor="email">Email *</label>
									<input
										type="email"
										id="email"
										name="email"
										value={formData.email}
										onChange={handleChange}
										required
									/>
								</div>
								<div className="form-group">
									<label htmlFor="phone">Телефон *</label>
									<input
										type="tel"
										id="phone"
										name="phone"
										value={formData.phone}
										onChange={handleChange}
										placeholder="+7 (___) ___-__-__"
										required
									/>
								</div>
							</div>
						</div>

						<div className="checkout-section">
							<h2>Доставка</h2>
							<div className="form-group">
								<label htmlFor="delivery_type">Способ получения</label>
								<select
									id="delivery_type"
									name="delivery_type"
									value={formData.delivery_type}
									onChange={handleChange}
								>
									<option value="pickup">Самовывоз</option>
									<option value="courier">Курьер</option>
								</select>
							</div>

							{formData.delivery_type !== "pickup" && (
								<>
									<div className="form-group">
										<label htmlFor="city">Город *</label>
										<input
											type="text"
											id="city"
											name="city"
											value={formData.city}
											onChange={handleChange}
										/>
									</div>
									<div className="form-group">
										<label htmlFor="address">Адрес *</label>
										<input
											type="text"
											id="address"
											name="address"
											value={formData.address}
											onChange={handleChange}
											placeholder="Улица, дом, квартира"
										/>
									</div>
									<div className="form-group">
										<label htmlFor="postal_code">Почтовый индекс</label>
										<input
											type="text"
											id="postal_code"
											name="postal_code"
											value={formData.postal_code}
											onChange={handleChange}
										/>
									</div>
								</>
							)}
						</div>

						<div className="checkout-section">
							<h2>Оплата</h2>
							<div className="form-group">
								<label htmlFor="payment_method">Способ оплаты</label>
								<select
									id="payment_method"
									name="payment_method"
									value={formData.payment_method}
									onChange={handleChange}
								>
									<option value="cash">Наличными при получении</option>
									<option value="card">Картой при получении</option>
								</select>
							</div>
						</div>

						<div className="checkout-section">
							<h2>Комментарий к заказу</h2>
							<div className="form-group">
								<textarea
									id="comment"
									name="comment"
									value={formData.comment}
									onChange={handleChange}
									rows={3}
									placeholder="Дополнительные пожелания..."
									style={{
										width: "100%",
										padding: "0.75rem",
										border: "1px solid #e0e0e0",
										borderRadius: "8px",
										resize: "vertical",
									}}
								/>
							</div>
						</div>
					</form>

					{/* Order Summary */}
					<div className="checkout-summary">
						<div className="checkout-section">
							<h2>Ваш заказ</h2>

							<div className="checkout-items">
								{cart.items.map((item) => (
									<div key={item.id} className="checkout-item">
										<div className="checkout-item__image">
											{item.product.main_image ? (
												<img
													src={item.product.main_image}
													alt={item.product.name}
												/>
											) : (
												<span>📱</span>
											)}
										</div>
										<div className="checkout-item__info">
											<p className="checkout-item__name">{item.product.name}</p>
											<p className="checkout-item__quantity">
												x{item.quantity}
											</p>
										</div>
										<p className="checkout-item__price">
											{parseFloat(item.price) * item.quantity} ₽
										</p>
									</div>
								))}
							</div>

							<div className="checkout-totals">
								<div className="checkout-total-row">
									<span>Товары ({cart.items_count})</span>
									<span>{cart.subtotal} ₽</span>
								</div>
								<div className="checkout-total-row">
									<span>Доставка</span>
									<span>
										{formData.delivery_type === "pickup"
											? "Бесплатно"
											: "Рассчитывается"}
									</span>
								</div>
								<div className="checkout-total-row total">
									<span>Итого</span>
									<span>{cart.subtotal} ₽</span>
								</div>
							</div>

							<div className="checkout-actions">
								<button
									type="submit"
									className="btn btn--primary"
									onClick={handleSubmit}
									disabled={isSubmitting}
									style={{ width: "100%" }}
								>
									{isSubmitting ? "Оформляем..." : "Оформить заказ"}
								</button>
							</div>

							<p
								style={{
									fontSize: "0.8rem",
									color: "#666",
									marginTop: "1rem",
									textAlign: "center",
								}}
							>
								Нажимая кнопку, вы соглашаетесь с условиями оферты
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
