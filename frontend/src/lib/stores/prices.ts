import { writable } from 'svelte/store';

const STORAGE_KEY = 'vape_prices_v1';

export interface PriceSettings {
	pg_cost_per_ml: number;
	vg_cost_per_ml: number;
	nic_cost_per_ml: number;
}

function loadFromStorage(): PriceSettings {
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (raw) return JSON.parse(raw);
	} catch {
		// localStorage unavailable (SSR or private browsing)
	}
	return { pg_cost_per_ml: 0, vg_cost_per_ml: 0, nic_cost_per_ml: 0 };
}

export const prices = writable<PriceSettings>({ pg_cost_per_ml: 0, vg_cost_per_ml: 0, nic_cost_per_ml: 0 });

/** Call once in browser context (onMount) to hydrate from localStorage */
export function initPrices() {
	const stored = loadFromStorage();
	prices.set(stored);
}

prices.subscribe((p) => {
	try {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(p));
	} catch {
		// ignore
	}
});
