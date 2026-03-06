<script lang="ts">
	import { onMount } from 'svelte';
	import { flavorsApi } from '$lib/api/flavors';
	import { refreshFlavors } from '$lib/stores/flavors';
	import type { FlavorOut, FlavorIn } from '$lib/api/flavors';
	import { prices, initPrices } from '$lib/stores/prices';

	let flavors = $state<FlavorOut[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let search = $state('');
	let manufacturerFilter = $state('');

	// Modal state
	let showModal = $state(false);
	let saving = $state(false);
	let saveError = $state<string | null>(null);
	let editingId = $state<number | null>(null);

	// Form fields
	let form = $state<FlavorIn>({
		name: '',
		manufacturer: '',
		abbreviation: '',
		base_pg: 100,
		base_vg: 0,
		density: 1.0,
		cost_per_ml: 0,
		notes: ''
	});

	const manufacturers = $derived(
		[...new Set(flavors.map((f) => f.manufacturer))].sort()
	);

	const filtered = $derived(
		flavors.filter((f) => {
			const q = search.toLowerCase();
			const matchesSearch =
				!q ||
				f.name.toLowerCase().includes(q) ||
				f.manufacturer.toLowerCase().includes(q) ||
				(f.abbreviation?.toLowerCase().includes(q) ?? false);
			const matchesMfr = !manufacturerFilter || f.manufacturer === manufacturerFilter;
			return matchesSearch && matchesMfr;
		})
	);

	async function load() {
		loading = true;
		error = null;
		try {
			flavors = await flavorsApi.list();
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		initPrices();
		load();
	});

	function openAdd() {
		editingId = null;
		form = { name: '', manufacturer: '', abbreviation: '', base_pg: 100, base_vg: 0, density: 1.0, cost_per_ml: 0, notes: '' };
		saveError = null;
		showModal = true;
	}

	function openEdit(flavor: FlavorOut) {
		editingId = flavor.id;
		form = {
			name: flavor.name,
			manufacturer: flavor.manufacturer,
			abbreviation: flavor.abbreviation ?? '',
			base_pg: Math.round(flavor.base_pg * 100),
			base_vg: Math.round(flavor.base_vg * 100),
			density: flavor.density,
			cost_per_ml: flavor.cost_per_ml,
			notes: flavor.notes ?? ''
		};
		saveError = null;
		showModal = true;
	}

	async function save() {
		saving = true;
		saveError = null;
		try {
			const payload: FlavorIn = {
				...form,
				base_pg: form.base_pg / 100,
				base_vg: form.base_vg / 100
			};
			if (editingId !== null) {
				await flavorsApi.update(editingId, payload);
			} else {
				await flavorsApi.create(payload);
			}
			showModal = false;
			await load();
			refreshFlavors();
		} catch (e) {
			saveError = (e as Error).message;
		} finally {
			saving = false;
		}
	}

	async function deleteFlavor(flavor: FlavorOut) {
		if (!confirm(`Delete "${flavor.manufacturer} ${flavor.name}"? This cannot be undone.`)) return;
		try {
			await flavorsApi.delete(flavor.id);
			await load();
			refreshFlavors();
		} catch (e) {
			alert((e as Error).message);
		}
	}

	function onPgInput(e: Event) {
		const val = Math.min(100, Math.max(0, Number((e.target as HTMLInputElement).value)));
		form = { ...form, base_pg: val, base_vg: 100 - val };
	}

	function onVgInput(e: Event) {
		const val = Math.min(100, Math.max(0, Number((e.target as HTMLInputElement).value)));
		form = { ...form, base_vg: val, base_pg: 100 - val };
	}
</script>

<div class="space-y-4">
	<div class="flex items-center justify-between">
		<h1 class="text-xl font-semibold text-gray-900 dark:text-white">Flavors</h1>
		<button
			type="button"
			onclick={openAdd}
			class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-3 py-1.5 rounded-md transition"
		>
			+ Add Flavor
		</button>
	</div>

	<!-- Base ingredients pricing -->
	<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
		<table class="w-full text-sm">
			<thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
				<tr>
					<th class="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">Base Ingredient</th>
					<th class="text-right px-4 py-2 font-medium text-gray-600 dark:text-gray-300 w-36">Cost / ml ($)</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
				<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
					<td class="px-4 py-2 font-medium text-gray-800 dark:text-gray-200">PG (Propylene Glycol)</td>
					<td class="px-4 py-2 text-right">
						<input
							type="number"
							min="0"
							step="0.001"
							value={$prices.pg_cost_per_ml}
							oninput={(e) => prices.update((p) => ({ ...p, pg_cost_per_ml: Number((e.target as HTMLInputElement).value) }))}
							class="w-28 border border-gray-300 dark:border-gray-700 rounded-md px-2 py-1 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-right focus:outline-none focus:ring-2 focus:ring-indigo-500"
						/>
					</td>
				</tr>
				<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
					<td class="px-4 py-2 font-medium text-gray-800 dark:text-gray-200">VG (Vegetable Glycerin)</td>
					<td class="px-4 py-2 text-right">
						<input
							type="number"
							min="0"
							step="0.001"
							value={$prices.vg_cost_per_ml}
							oninput={(e) => prices.update((p) => ({ ...p, vg_cost_per_ml: Number((e.target as HTMLInputElement).value) }))}
							class="w-28 border border-gray-300 dark:border-gray-700 rounded-md px-2 py-1 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-right focus:outline-none focus:ring-2 focus:ring-indigo-500"
						/>
					</td>
				</tr>
				<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
					<td class="px-4 py-2 font-medium text-gray-800 dark:text-gray-200">Nicotine Base</td>
					<td class="px-4 py-2 text-right">
						<input
							type="number"
							min="0"
							step="0.001"
							value={$prices.nic_cost_per_ml}
							oninput={(e) => prices.update((p) => ({ ...p, nic_cost_per_ml: Number((e.target as HTMLInputElement).value) }))}
							class="w-28 border border-gray-300 dark:border-gray-700 rounded-md px-2 py-1 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-right focus:outline-none focus:ring-2 focus:ring-indigo-500"
						/>
					</td>
				</tr>
			</tbody>
		</table>
	</div>

	<!-- Filters -->
	<div class="flex gap-3">
		<input
			type="text"
			placeholder="Search flavors..."
			bind:value={search}
			class="flex-1 border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
		/>
		<select
			bind:value={manufacturerFilter}
			class="border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
		>
			<option value="">All manufacturers</option>
			{#each manufacturers as mfr}
				<option value={mfr}>{mfr}</option>
			{/each}
		</select>
	</div>

	{#if loading}
		<div class="flex items-center gap-2 text-sm text-gray-400 dark:text-gray-500 py-8 justify-center">
			<svg class="animate-spin h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
			</svg>
			Loading flavors...
		</div>
	{:else if error}
		<p class="text-sm text-red-500 py-4">{error}</p>
	{:else if filtered.length === 0}
		<p class="text-sm text-gray-400 dark:text-gray-500 italic py-8 text-center">No flavors found.</p>
	{:else}
		<p class="text-xs text-gray-400 dark:text-gray-500">{filtered.length} flavor{filtered.length !== 1 ? 's' : ''}</p>
		<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
			<table class="w-full text-sm">
				<thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
					<tr>
						<th class="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">Name</th>
						<th class="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">Manufacturer</th>
						<th class="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300 hidden sm:table-cell">Abbr</th>
						<th class="text-right px-4 py-2 font-medium text-gray-600 dark:text-gray-300 hidden md:table-cell">PG/VG</th>
						<th class="text-right px-4 py-2 font-medium text-gray-600 dark:text-gray-300 hidden md:table-cell">Cost/ml</th>
						<th class="px-4 py-2"></th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
					{#each filtered as flavor (flavor.id)}
						<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition">
							<td class="px-4 py-2 font-medium text-gray-800 dark:text-gray-200">
								{flavor.name}
								{#if flavor.is_custom}
									<span class="ml-1 text-xs bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400 rounded px-1 py-0.5">custom</span>
								{/if}
							</td>
							<td class="px-4 py-2 text-gray-500 dark:text-gray-400">{flavor.manufacturer}</td>
							<td class="px-4 py-2 text-gray-400 dark:text-gray-500 hidden sm:table-cell">{flavor.abbreviation ?? '—'}</td>
							<td class="px-4 py-2 text-right text-gray-500 dark:text-gray-400 hidden md:table-cell">
								{Math.round(flavor.base_pg * 100)}/{Math.round(flavor.base_vg * 100)}
							</td>
							<td class="px-4 py-2 text-right text-gray-500 dark:text-gray-400 hidden md:table-cell">
								{flavor.cost_per_ml > 0 ? `$${flavor.cost_per_ml.toFixed(3)}` : '—'}
							</td>
							<td class="px-4 py-2 text-right whitespace-nowrap">
								<button
									type="button"
									onclick={() => openEdit(flavor)}
									class="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 mr-3 transition"
								>Edit</button>
								<button
									type="button"
									onclick={() => deleteFlavor(flavor)}
									class="text-xs text-red-400 hover:text-red-600 transition"
								>Delete</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<!-- Add/Edit Modal -->
{#if showModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
		<div class="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-md mx-4 p-6 space-y-4">
			<h2 class="text-lg font-semibold text-gray-900 dark:text-white">
				{editingId !== null ? 'Edit Flavor' : 'Add Flavor'}
			</h2>

			<div class="grid grid-cols-2 gap-3">
				<div class="col-span-2">
					<label for="f-name" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Name *</label>
					<input
						id="f-name"
						type="text"
						bind:value={form.name}
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
						placeholder="Strawberry"
					/>
				</div>
				<div>
					<label for="f-mfr" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Manufacturer *</label>
					<input
						id="f-mfr"
						type="text"
						bind:value={form.manufacturer}
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
						placeholder="TFA"
					/>
				</div>
				<div>
					<label for="f-abbr" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Abbreviation</label>
					<input
						id="f-abbr"
						type="text"
						bind:value={form.abbreviation}
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
						placeholder="TFA SW"
					/>
				</div>
				<div>
					<label for="f-pg" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">PG %</label>
					<input
						id="f-pg"
						type="number" min="0" max="100" step="5"
						value={form.base_pg}
						oninput={onPgInput}
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					/>
				</div>
				<div>
					<label for="f-vg" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">VG %</label>
					<input
						id="f-vg"
						type="number" min="0" max="100" step="5"
						value={form.base_vg}
						oninput={onVgInput}
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					/>
				</div>
				<div>
					<label for="f-density" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Density (g/ml)</label>
					<input
						id="f-density"
						type="number" min="0.8" max="1.3" step="0.001"
						bind:value={form.density}
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					/>
				</div>
				<div>
					<label for="f-cost" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Cost / ml ($)</label>
					<input
						id="f-cost"
						type="number" min="0" step="0.001"
						bind:value={form.cost_per_ml}
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					/>
				</div>
				<div class="col-span-2">
					<label for="f-notes" class="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Notes</label>
					<textarea
						id="f-notes"
						bind:value={form.notes}
						rows="2"
						class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
						placeholder="Optional notes..."
					></textarea>
				</div>
			</div>

			{#if saveError}
				<p class="text-sm text-red-500">{saveError}</p>
			{/if}

			<div class="flex justify-end gap-2 pt-1">
				<button
					type="button"
					onclick={() => (showModal = false)}
					class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition"
				>Cancel</button>
				<button
					type="button"
					onclick={save}
					disabled={saving}
					class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition disabled:opacity-50"
				>
					{saving ? 'Saving...' : 'Save'}
				</button>
			</div>
		</div>
	</div>
{/if}
