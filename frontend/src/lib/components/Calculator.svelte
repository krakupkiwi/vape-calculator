<script lang="ts">
	import { onMount } from 'svelte';
	import { recipe, addFlavor, removeFlavor, updateFlavor } from '$lib/stores/recipe';
	import FlavorSearch from '$lib/components/FlavorSearch.svelte';
	import type { FlavorOut } from '$lib/stores/flavors';
	import { prices, initPrices } from '$lib/stores/prices';

	onMount(() => {
		initPrices();
		// Sync persisted prices into recipe store on first load
		prices.subscribe((p) => {
			recipe.update((r) => ({
				...r,
				pg_cost_per_ml: p.pg_cost_per_ml,
				vg_cost_per_ml: p.vg_cost_per_ml,
				nic_cost_per_ml: p.nic_cost_per_ml
			}));
		});
	});

	// Keep PG+VG linked: when one changes, the other auto-adjusts
	function onPgChange(e: Event) {
		const val = Math.min(100, Math.max(0, Number((e.target as HTMLInputElement).value)));
		recipe.update((r) => ({ ...r, target_pg: val, target_vg: 100 - val }));
	}

	function onVgChange(e: Event) {
		const val = Math.min(100, Math.max(0, Number((e.target as HTMLInputElement).value)));
		recipe.update((r) => ({ ...r, target_vg: val, target_pg: 100 - val }));
	}

	function onNicPgChange(e: Event) {
		const val = Math.min(100, Math.max(0, Number((e.target as HTMLInputElement).value)));
		recipe.update((r) => ({ ...r, nic_base_pg: val, nic_base_vg: 100 - val }));
	}

	function onNicVgChange(e: Event) {
		const val = Math.min(100, Math.max(0, Number((e.target as HTMLInputElement).value)));
		recipe.update((r) => ({ ...r, nic_base_vg: val, nic_base_pg: 100 - val }));
	}
</script>

<div class="space-y-6">
	<!-- Recipe name -->
	<div>
		<label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1" for="recipe-name">Recipe Name</label>
		<input
			id="recipe-name"
			type="text"
			class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
			placeholder="My E-Liquid"
			bind:value={$recipe.name}
		/>
	</div>

	<!-- Batch size -->
	<div class="grid grid-cols-2 gap-4">
		<div>
			<label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1" for="batch-size">Batch Size (ml)</label>
			<input
				id="batch-size"
				type="number"
				min="1"
				step="10"
				class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
				bind:value={$recipe.batch_size_ml}
			/>
		</div>
		<div>
			<label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1" for="target-nic">Target Nicotine (mg/ml)</label>
			<input
				id="target-nic"
				type="number"
				min="0"
				step="0.5"
				class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
				bind:value={$recipe.target_nic_mg}
			/>
		</div>
	</div>

	<!-- PG/VG ratio -->
	<div>
		<p class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">PG/VG Ratio</p>
		<div class="grid grid-cols-2 gap-4">
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="target-pg">PG %</label>
				<input
					id="target-pg"
					type="number"
					min="0"
					max="100"
					step="5"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					value={$recipe.target_pg}
					oninput={onPgChange}
				/>
			</div>
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="target-vg">VG %</label>
				<input
					id="target-vg"
					type="number"
					min="0"
					max="100"
					step="5"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					value={$recipe.target_vg}
					oninput={onVgChange}
				/>
			</div>
		</div>
		<div class="mt-2 h-2 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
			<div
				class="h-full bg-indigo-400 transition-all"
				style="width: {$recipe.target_pg}%"
			></div>
		</div>
		<div class="flex justify-between text-xs text-gray-400 dark:text-gray-500 mt-0.5">
			<span>PG {$recipe.target_pg}%</span>
			<span>VG {$recipe.target_vg}%</span>
		</div>
	</div>

	<!-- Nicotine base -->
	{#if $recipe.target_nic_mg > 0}
	<details class="border border-gray-200 dark:border-gray-700 rounded-md">
		<summary class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 cursor-pointer select-none">
			Nicotine Base Settings
		</summary>
		<div class="px-3 pb-3 pt-2 grid grid-cols-2 gap-4">
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="nic-strength">Base Strength (mg/ml)</label>
				<input
					id="nic-strength"
					type="number"
					min="0"
					step="10"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					bind:value={$recipe.nic_base_strength_mg}
				/>
			</div>
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="nic-density">Density (g/ml)</label>
				<input
					id="nic-density"
					type="number"
					min="0.9"
					max="1.3"
					step="0.001"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					bind:value={$recipe.nic_base_density}
				/>
			</div>
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="nic-pg">Nic Base PG %</label>
				<input
					id="nic-pg"
					type="number"
					min="0"
					max="100"
					step="5"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					value={$recipe.nic_base_pg}
					oninput={onNicPgChange}
				/>
			</div>
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="nic-vg">Nic Base VG %</label>
				<input
					id="nic-vg"
					type="number"
					min="0"
					max="100"
					step="5"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					value={$recipe.nic_base_vg}
					oninput={onNicVgChange}
				/>
			</div>
		</div>
	</details>
	{/if}

	<!-- Pricing -->
	<details class="border border-gray-200 dark:border-gray-700 rounded-md">
		<summary class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 cursor-pointer select-none">
			Pricing (optional)
		</summary>
		<div class="px-3 pb-3 pt-2 grid grid-cols-3 gap-3">
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="price-pg">PG ($/ml)</label>
				<input
					id="price-pg"
					type="number"
					min="0"
					step="0.001"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					value={$prices.pg_cost_per_ml}
					oninput={(e) => {
						const v = Number((e.target as HTMLInputElement).value);
						prices.update((p) => ({ ...p, pg_cost_per_ml: v }));
						recipe.update((r) => ({ ...r, pg_cost_per_ml: v }));
					}}
				/>
			</div>
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="price-vg">VG ($/ml)</label>
				<input
					id="price-vg"
					type="number"
					min="0"
					step="0.001"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					value={$prices.vg_cost_per_ml}
					oninput={(e) => {
						const v = Number((e.target as HTMLInputElement).value);
						prices.update((p) => ({ ...p, vg_cost_per_ml: v }));
						recipe.update((r) => ({ ...r, vg_cost_per_ml: v }));
					}}
				/>
			</div>
			<div>
				<label class="block text-xs text-gray-500 dark:text-gray-400 mb-1" for="price-nic">Nic base ($/ml)</label>
				<input
					id="price-nic"
					type="number"
					min="0"
					step="0.001"
					class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
					value={$prices.nic_cost_per_ml}
					oninput={(e) => {
						const v = Number((e.target as HTMLInputElement).value);
						prices.update((p) => ({ ...p, nic_cost_per_ml: v }));
						recipe.update((r) => ({ ...r, nic_cost_per_ml: v }));
					}}
				/>
			</div>
		</div>
	</details>

	<!-- Flavors -->
	<div>
		<div class="flex items-center justify-between mb-2">
			<p class="text-sm font-medium text-gray-700 dark:text-gray-200">Flavors</p>
			<button
				type="button"
				onclick={addFlavor}
				class="text-xs bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-900/40 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded px-2 py-1 transition"
			>
				+ Add Flavor
			</button>
		</div>

		{#if $recipe.flavors.length === 0}
			<p class="text-sm text-gray-400 dark:text-gray-500 italic">No flavors added. Click "+ Add Flavor".</p>
		{/if}

		<div class="space-y-2">
			{#each $recipe.flavors as flavor (flavor.id)}
				<div class="grid grid-cols-[1fr_80px_80px_auto] gap-2 items-end">
					<div>
						{#if $recipe.flavors.indexOf(flavor) === 0}
							<span class="block text-xs text-gray-500 dark:text-gray-400 mb-1">Flavor Name</span>
						{/if}
						<FlavorSearch
							value={flavor.name}
							onselect={(f: FlavorOut) => updateFlavor(flavor.id, {
								name: `${f.manufacturer} ${f.name}`,
								pg_ratio: f.base_pg,
								vg_ratio: f.base_vg,
								density: f.density,
								cost_per_ml: f.cost_per_ml
							})}
							oninput={(name: string) => updateFlavor(flavor.id, { name })}
						/>
					</div>
					<div>
						{#if $recipe.flavors.indexOf(flavor) === 0}
							<span class="block text-xs text-gray-500 dark:text-gray-400 mb-1">%</span>
						{/if}
						<input
							type="number"
							min="0"
							max="100"
							step="0.5"
							class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
							value={flavor.percentage}
							oninput={(e) => updateFlavor(flavor.id, { percentage: Number((e.target as HTMLInputElement).value) })}
						/>
					</div>
					<div>
						{#if $recipe.flavors.indexOf(flavor) === 0}
							<span class="block text-xs text-gray-500 dark:text-gray-400 mb-1">$/ml</span>
						{/if}
						<input
							type="number"
							min="0"
							step="0.001"
							class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
							value={flavor.cost_per_ml}
							oninput={(e) => updateFlavor(flavor.id, { cost_per_ml: Number((e.target as HTMLInputElement).value) })}
						/>
					</div>
					<button
						type="button"
						onclick={() => removeFlavor(flavor.id)}
						class="mb-0 text-gray-400 hover:text-red-500 transition text-lg leading-none px-1"
						title="Remove flavor"
					>
						&times;
					</button>
				</div>
			{/each}
		</div>

		{#if $recipe.flavors.length > 0}
			<p class="text-xs text-gray-400 dark:text-gray-500 mt-1 text-right">
				Total: {$recipe.flavors.reduce((sum, f) => sum + f.percentage, 0).toFixed(1)}%
			</p>
		{/if}
	</div>
</div>
