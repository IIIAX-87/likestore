"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { cartAPI, wishlistAPI, type Cart, type Product } from "./api";

interface CartState {
	cart: Cart | null;
	isLoading: boolean;
	error: string | null;
	fetchCart: () => Promise<void>;
	addItem: (
		productId: number,
		variantId?: number,
		quantity?: number,
	) => Promise<void>;
	updateItem: (itemId: number, quantity: number) => Promise<void>;
	removeItem: (itemId: number) => Promise<void>;
	clearCart: () => Promise<void>;
}

export const useCartStore = create<CartState>()(
	persist(
		(set, get) => ({
			cart: null,
			isLoading: false,
			error: null,

			fetchCart: async () => {
				set({ isLoading: true, error: null });
				try {
					const cart = await cartAPI.get();
					set({ cart, isLoading: false });
				} catch (error) {
					set({ error: (error as Error).message, isLoading: false });
				}
			},

			addItem: async (productId, variantId, quantity = 1) => {
				set({ isLoading: true, error: null });
				try {
					const cart = await cartAPI.addItem({
						product_id: productId,
						variant_id: variantId,
						quantity,
					});
					set({ cart, isLoading: false });
				} catch (error) {
					set({ error: (error as Error).message, isLoading: false });
					throw error;
				}
			},

			updateItem: async (itemId, quantity) => {
				set({ isLoading: true, error: null });
				try {
					const cart = await cartAPI.updateItem(itemId, quantity);
					set({ cart, isLoading: false });
				} catch (error) {
					set({ error: (error as Error).message, isLoading: false });
					throw error;
				}
			},

			removeItem: async (itemId) => {
				set({ isLoading: true, error: null });
				try {
					const cart = await cartAPI.removeItem(itemId);
					set({ cart, isLoading: false });
				} catch (error) {
					set({ error: (error as Error).message, isLoading: false });
					throw error;
				}
			},

			clearCart: async () => {
				set({ isLoading: true, error: null });
				try {
					const cart = await cartAPI.clear();
					set({ cart, isLoading: false });
				} catch (error) {
					set({ error: (error as Error).message, isLoading: false });
					throw error;
				}
			},
		}),
		{
			name: "likestore-cart",
			partialize: (state) => ({ cart: state.cart }),
		},
	),
);

interface WishlistState {
	items: number[];
	addItem: (productId: number) => Promise<void>;
	removeItem: (productId: number) => Promise<void>;
	isInWishlist: (productId: number) => boolean;
}

export const useWishlistStore = create<WishlistState>()(
	persist(
		(set, get) => ({
			items: [],

			addItem: async (productId) => {
				try {
					await wishlistAPI.add(productId);
					set((state) => ({ items: [...state.items, productId] }));
				} catch (error) {
					console.error("Failed to add to wishlist:", error);
				}
			},

			removeItem: async (productId) => {
				try {
					await wishlistAPI.remove(productId);
					set((state) => ({
						items: state.items.filter((id) => id !== productId),
					}));
				} catch (error) {
					console.error("Failed to remove from wishlist:", error);
				}
			},

			isInWishlist: (productId) => get().items.includes(productId),
		}),
		{
			name: "likestore-wishlist",
		},
	),
);
