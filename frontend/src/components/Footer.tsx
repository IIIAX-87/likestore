import Link from "next/link";

export default function Footer() {
	return (
		<footer className="footer">
			<div className="container">
				<div className="footer-grid">
					<div className="footer-section">
						<h3>О компании</h3>
						<ul>
							<li>
								<Link href="/about/">О нас</Link>
							</li>
							<li>
								<Link href="/contacts/">Контакты</Link>
							</li>
							<li>
								<Link href="/franchise/">Франшиза</Link>
							</li>
							<li>
								<Link href="/vacancies/">Вакансии</Link>
							</li>
						</ul>
					</div>

					<div className="footer-section">
						<h3>Покупателям</h3>
						<ul>
							<li>
								<Link href="/garantiya/">Гарантия</Link>
							</li>
							<li>
								<Link href="/dostavka-i-oplata/">Доставка и оплата</Link>
							</li>
							<li>
								<Link href="/trade-in/">Trade-in</Link>
							</li>
							<li>
								<Link href="/bonus-card/">Бонусная программа</Link>
							</li>
						</ul>
					</div>

					<div className="footer-section">
						<h3>Каталог</h3>
						<ul>
							<li>
								<Link href="/catalog/iphone_1/">iPhone</Link>
							</li>
							<li>
								<Link href="/catalog/macbook/">MacBook</Link>
							</li>
							<li>
								<Link href="/catalog/ipad/">iPad</Link>
							</li>
							<li>
								<Link href="/catalog/watch/">Apple Watch</Link>
							</li>
							<li>
								<Link href="/catalog/airpods_1/">AirPods</Link>
							</li>
						</ul>
					</div>

					<div className="footer-section">
						<h3>Контакты</h3>
						<p className="footer-contact">
							<a href="tel:+79324065333">+7 (932) 406-53-33</a>
						</p>
						<p className="footer-contact">Ханты-Мансийск</p>
						<div className="footer-social">
							<a
								href="https://telegram.me/likestore_shop"
								target="_blank"
								rel="noopener noreferrer"
							>
								Telegram
							</a>
							<a
								href="https://wa.me/79324065333"
								target="_blank"
								rel="noopener noreferrer"
							>
								WhatsApp
							</a>
						</div>
					</div>
				</div>

				<div className="footer-bottom">
					<p>© {new Date().getFullYear()} LikeStore. Все права защищены.</p>
					<p>Магазин техники Apple в Ханты-Мансийске</p>
				</div>
			</div>
		</footer>
	);
}
