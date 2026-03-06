import { writable, get } from 'svelte/store';
import Fuse, { type IFuseOptions } from 'fuse.js';
import type { FlavorOut } from '$lib/api/flavors';

export type { FlavorOut };

export const flavors = writable<FlavorOut[]>([]);
export const flavorsLoaded = writable(false);

let fuse: Fuse<FlavorOut> | null = null;

const FUSE_OPTIONS: IFuseOptions<FlavorOut> = {
	keys: [
		{ name: 'name', weight: 0.7 },
		{ name: 'manufacturer', weight: 0.3 }
	],
	threshold: 0.35,
	includeScore: true,
	minMatchCharLength: 1
};

export async function loadFlavors() {
	if (get(flavorsLoaded)) return;
	try {
		const res = await fetch('/api/flavors');
		if (!res.ok) return;
		const data: FlavorOut[] = await res.json();
		flavors.set(data);
		fuse = new Fuse(data, FUSE_OPTIONS);
		flavorsLoaded.set(true);
	} catch {
		// silently fail — search just won't auto-complete
	}
}

export function searchFlavors(query: string): FlavorOut[] {
	if (!query.trim()) return [];
	if (!fuse) {
		// Fallback: simple substring match
		const q = query.toLowerCase();
		return get(flavors)
			.filter((f) => f.name.toLowerCase().includes(q) || f.manufacturer.toLowerCase().includes(q))
			.slice(0, 8);
	}
	return fuse.search(query, { limit: 8 }).map((r) => r.item);
}

export function refreshFlavors() {
	flavorsLoaded.set(false);
	fuse = null;
	loadFlavors();
}
