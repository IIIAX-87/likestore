import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { OrganizationSchema } from "@/components/ProductSchema";

export const metadata: Metadata = {
  title: {
    default: "LikeStore - Магазин техники Apple",
    template: "%s | LikeStore",
  },
  description:
    "Купить технику Apple, Dyson и аксессуары в фирменном магазине LikeStore. Оригинальная продукция Apple с гарантией и доставкой в Ханты-Мансийске.",
  keywords: [
    "Apple",
    "iPhone",
    "MacBook",
    "iPad",
    "Apple Watch",
    "AirPods",
    "Samsung",
    "купить технику",
    "Ханты-Мансийск",
    "LikeStore",
  ],
  authors: [{ name: "LikeStore" }],
  creator: "LikeStore",
  publisher: "LikeStore",
  openGraph: {
    type: "website",
    locale: "ru_RU",
    url: "https://likestore.ru",
    siteName: "LikeStore",
    title: "LikeStore - Магазин техники Apple",
    description: "Купить технику Apple в Ханты-Мансийске с гарантией",
    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "LikeStore",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "LikeStore - Магазин техники Apple",
    description: "Купить технику Apple в Ханты-Мансийске с гарантией",
    images: ["/og-image.jpg"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    yandex: "your-yandex-verification-code",
    google: "your-google-verification-code",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <head>
        <OrganizationSchema
          name="LikeStore"
          url="https://likestore.ru"
          logo="https://likestore.ru/logo.svg"
          phone="+79324065333"
          address={{
            streetAddress: "ул. Гагарина, 12",
            addressLocality: "Ханты-Мансийск",
            postalCode: "628011",
            addressCountry: "RU",
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
