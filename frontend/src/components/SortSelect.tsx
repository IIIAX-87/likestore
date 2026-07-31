"use client";

import { useRouter } from "next/navigation";

const sortOptions = [
	{ value: "-created_at", label: "По новизне" },
	{ value: "price", label: "Сначала дешевле" },
	{ value: "-price", label: "Сначала дороже" },
	{ value: "name", label: "По названию" },
];

interface SortSelectProps {
	defaultValue: string;
	categorySlug: string;
}

export default function SortSelect({
	defaultValue,
	categorySlug,
}: SortSelectProps) {
	const router = useRouter();

	const handleSort = (value: string) => {
		const params = new URLSearchParams(window.location.search);
		params.set("ordering", value);
		params.delete("page"); // Reset to page 1
		router.push(`/catalog/${categorySlug}/?${params.toString()}`);
	};

	return (
		<select
			defaultValue={defaultValue}
			onChange={(e) => handleSort(e.target.value)}
			style={{
				padding: "0.5rem 1rem",
				border: "1px solid #e0e0e0",
				borderRadius: "4px",
				background: "#fff",
				cursor: "pointer",
			}}
		>
			{sortOptions.map((opt) => (
				<option key={opt.value} value={opt.value}>
					{opt.label}
				</option>
			))}
		</select>
	);
}
