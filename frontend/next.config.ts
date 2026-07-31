import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	images: {
		remotePatterns: [
			{
				protocol: "https",
				hostname: "hm.lstore.ru",
			},
			{
				protocol: "https",
				hostname: "*.lstore.ru",
			},
			{
				protocol: "https",
				hostname: "localhost",
				port: "8000",
			},
		],
	},
	async rewrites() {
		return [
			{
				source: "/api/:path*",
				destination: process.env.NEXT_PUBLIC_API_URL + "/:path*",
			},
		];
	},
};

export default nextConfig;
