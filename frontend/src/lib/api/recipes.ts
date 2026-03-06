export interface FlavorIn {
	name: string;
	percentage: number;
	pg_ratio: number;
	vg_ratio: number;
	density: number;
	cost_per_ml: number;
	sort_order?: number;
}

export interface RecipeIn {
	name: string;
	description?: string;
	notes?: string;
	batch_size_ml: number;
	target_nic_mg: number;
	nic_base_strength_mg: number;
	nic_base_pg: number;    // fraction 0–1
	nic_base_vg: number;
	nic_base_density: number;
	nic_cost_per_ml: number;
	pg_ratio: number;       // fraction 0–1
	vg_ratio: number;
	pg_cost_per_ml: number;
	vg_cost_per_ml: number;
	flavors: FlavorIn[];
}

export interface FlavorOut {
	id: number;
	name: string;
	percentage: number;
	pg_ratio: number;
	vg_ratio: number;
	density: number;
	cost_per_ml: number;
	sort_order: number;
}

export interface RecipeOut {
	id: number;
	name: string;
	description: string | null;
	notes: string | null;
	batch_size_ml: number;
	target_nic_mg: number;
	nic_base_strength_mg: number;
	nic_base_pg: number;
	nic_base_vg: number;
	nic_base_density: number;
	nic_cost_per_ml: number;
	pg_ratio: number;
	vg_ratio: number;
	pg_cost_per_ml: number;
	vg_cost_per_ml: number;
	created_at: string;
	updated_at: string;
	rating: number | null;
	flavors: FlavorOut[];
}

export interface RatingIn {
	stars: number;
	note?: string;
}

export interface RatingOut {
	id: number;
	stars: number;
	note: string | null;
	created_at: string;
}

export interface RecipeSummary {
	id: number;
	name: string;
	description: string | null;
	batch_size_ml: number;
	target_nic_mg: number;
	pg_ratio: number;
	vg_ratio: number;
	created_at: string;
	updated_at: string;
	flavor_count: number;
	rating: number | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(path, {
		headers: { 'Content-Type': 'application/json' },
		...init
	});
	if (res.status === 204) return undefined as T;
	const body = await res.json();
	if (!res.ok) throw new Error(body.detail ?? `Request failed: ${res.status}`);
	return body;
}

export const recipesApi = {
	list: (sort: 'date' | 'name' | 'rating' = 'date', minRating?: number) => {
		const params = new URLSearchParams({ sort });
		if (minRating) params.set('min_rating', String(minRating));
		return request<RecipeSummary[]>(`/api/recipes?${params}`);
	},

	get: (id: number) =>
		request<RecipeOut>(`/api/recipes/${id}`),

	create: (data: RecipeIn) =>
		request<RecipeOut>('/api/recipes', { method: 'POST', body: JSON.stringify(data) }),

	update: (id: number, data: RecipeIn) =>
		request<RecipeOut>(`/api/recipes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

	delete: (id: number) =>
		request<void>(`/api/recipes/${id}`, { method: 'DELETE' }),

	clone: (id: number) =>
		request<RecipeOut>(`/api/recipes/${id}/clone`, { method: 'POST' }),

	ratings: (id: number) =>
		request<RatingOut[]>(`/api/recipes/${id}/ratings`),

	rate: (id: number, data: RatingIn) =>
		request<RatingOut>(`/api/recipes/${id}/ratings`, { method: 'POST', body: JSON.stringify(data) })
};
