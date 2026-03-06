import { writable } from 'svelte/store';
import type { CalculateResponse } from '$lib/api/client';
import type { RecipeIn, RecipeOut } from '$lib/api/recipes';

export interface FlavorRow {
	id: number;
	name: string;
	percentage: number;
	pg_ratio: number;
	vg_ratio: number;
	density: number;
	cost_per_ml: number;
}

export interface RecipeState {
	name: string;
	batch_size_ml: number;
	target_nic_mg: number;
	nic_base_strength_mg: number;
	nic_base_pg: number;
	nic_base_vg: number;
	nic_base_density: number;
	nic_cost_per_ml: number;
	target_pg: number;
	target_vg: number;
	pg_cost_per_ml: number;
	vg_cost_per_ml: number;
	flavors: FlavorRow[];
}

let _nextId = 1;

function defaultRecipe(): RecipeState {
	return {
		name: '',
		batch_size_ml: 100,
		target_nic_mg: 3,
		nic_base_strength_mg: 100,
		nic_base_pg: 100,
		nic_base_vg: 0,
		nic_base_density: 1.036,
		nic_cost_per_ml: 0,
		target_pg: 30,
		target_vg: 70,
		pg_cost_per_ml: 0,
		vg_cost_per_ml: 0,
		flavors: [{ id: _nextId++, name: '', percentage: 5, pg_ratio: 1.0, vg_ratio: 0.0, density: 1.0, cost_per_ml: 0 }]
	};
}

export const recipe = writable<RecipeState>(defaultRecipe());

export const result = writable<CalculateResponse | null>(null);
export const calculating = writable(false);
export const calcError = writable<string | null>(null);

export function addFlavor() {
	recipe.update((r) => ({
		...r,
		flavors: [
			...r.flavors,
			{ id: _nextId++, name: '', percentage: 5, pg_ratio: 1.0, vg_ratio: 0.0, density: 1.0, cost_per_ml: 0 }
		]
	}));
}

export function removeFlavor(id: number) {
	recipe.update((r) => ({ ...r, flavors: r.flavors.filter((f) => f.id !== id) }));
}

export function updateFlavor(id: number, patch: Partial<FlavorRow>) {
	recipe.update((r) => ({
		...r,
		flavors: r.flavors.map((f) => (f.id === id ? { ...f, ...patch } : f))
	}));
}

/** Convert store state → API payload (percentages → fractions) */
export function stateToRecipeIn(r: RecipeState): RecipeIn {
	return {
		name: r.name || 'Untitled Recipe',
		batch_size_ml: r.batch_size_ml,
		target_nic_mg: r.target_nic_mg,
		nic_base_strength_mg: r.nic_base_strength_mg,
		nic_base_pg: r.nic_base_pg / 100,
		nic_base_vg: r.nic_base_vg / 100,
		nic_base_density: r.nic_base_density,
		nic_cost_per_ml: r.nic_cost_per_ml,
		pg_ratio: r.target_pg / 100,
		vg_ratio: r.target_vg / 100,
		pg_cost_per_ml: r.pg_cost_per_ml,
		vg_cost_per_ml: r.vg_cost_per_ml,
		flavors: r.flavors
			.filter((f) => f.name.trim() !== '')
			.map((f, i) => ({
				name: f.name,
				percentage: f.percentage,
				pg_ratio: f.pg_ratio,
				vg_ratio: f.vg_ratio,
				density: f.density,
				cost_per_ml: f.cost_per_ml,
				sort_order: i
			}))
	};
}

/** Load a saved RecipeOut back into the calculator store */
export function loadRecipeIntoStore(r: RecipeOut) {
	recipe.set({
		name: r.name,
		batch_size_ml: r.batch_size_ml,
		target_nic_mg: r.target_nic_mg,
		nic_base_strength_mg: r.nic_base_strength_mg,
		nic_base_pg: Math.round(r.nic_base_pg * 100),
		nic_base_vg: Math.round(r.nic_base_vg * 100),
		nic_base_density: r.nic_base_density,
		nic_cost_per_ml: r.nic_cost_per_ml,
		target_pg: Math.round(r.pg_ratio * 100),
		target_vg: Math.round(r.vg_ratio * 100),
		pg_cost_per_ml: r.pg_cost_per_ml,
		vg_cost_per_ml: r.vg_cost_per_ml,
		flavors: r.flavors.map((f) => ({
			id: _nextId++,
			name: f.name,
			percentage: f.percentage,
			pg_ratio: f.pg_ratio,
			vg_ratio: f.vg_ratio,
			density: f.density,
			cost_per_ml: f.cost_per_ml
		}))
	});
}
