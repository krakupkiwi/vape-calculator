export interface FlavorPayload {
	name: string;
	percentage: number;
	pg_ratio: number;
	vg_ratio: number;
	density: number;
	cost_per_ml: number;
}

export interface CalculateRequest {
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
	flavors: FlavorPayload[];
}

export interface IngredientResult {
	name: string;
	volume_ml: number;
	weight_g: number;
	cost: number;
	percentage: number;
}

export interface CalculateResponse {
	ingredients: IngredientResult[];
	total_ml: number;
	total_cost: number;
	cost_per_ml: number;
	actual_nic_mg: number;
	actual_pg: number;
	actual_vg: number;
	warnings: string[];
}

export async function calculate(request: CalculateRequest): Promise<CalculateResponse> {
	const res = await fetch('/api/calculate', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(request)
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(err.detail ?? 'Calculation failed');
	}
	return res.json();
}
