export interface FlavorOut {
	id: number;
	name: string;
	manufacturer: string;
	abbreviation: string | null;
	base_pg: number;
	base_vg: number;
	density: number;
	cost_per_ml: number;
	notes: string | null;
	is_custom: number;
}

export interface FlavorIn {
	name: string;
	manufacturer: string;
	abbreviation?: string;
	base_pg: number;
	base_vg: number;
	density: number;
	cost_per_ml: number;
	notes?: string;
}

export interface NicBaseOut {
	id: number;
	name: string;
	strength_mg: number;
	base_pg: number;
	base_vg: number;
	cost_per_ml: number;
	notes: string | null;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...init });
	if (res.status === 204) return undefined as T;
	const body = await res.json();
	if (!res.ok) throw new Error(body.detail ?? `Request failed: ${res.status}`);
	return body;
}

export const flavorsApi = {
	list: (q?: string, manufacturer?: string) => {
		const params = new URLSearchParams();
		if (q) params.set('q', q);
		if (manufacturer) params.set('manufacturer', manufacturer);
		return req<FlavorOut[]>(`/api/flavors?${params}`);
	},
	create: (data: FlavorIn) =>
		req<FlavorOut>('/api/flavors', { method: 'POST', body: JSON.stringify(data) }),
	update: (id: number, data: FlavorIn) =>
		req<FlavorOut>(`/api/flavors/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
	delete: (id: number) =>
		req<void>(`/api/flavors/${id}`, { method: 'DELETE' })
};

export const nicBasesApi = {
	list: () => req<NicBaseOut[]>('/api/nic-bases')
};
