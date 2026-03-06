<script lang="ts">
	import { result, calculating, calcError } from '$lib/stores/recipe';
	import CostPanel from '$lib/components/CostPanel.svelte';

	$: totalG = $result?.ingredients.reduce((s, i) => s + i.weight_g, 0) ?? 0;
	$: totalPct = $result?.ingredients.reduce((s, i) => s + i.percentage, 0) ?? 0;
	$: flavorIngredients = $result?.ingredients.filter(
		(i) => !i.name.startsWith('Nicotine') && !i.name.startsWith('PG') && !i.name.startsWith('VG')
	) ?? [];
	$: flavorTotalMl = flavorIngredients.reduce((s, i) => s + i.volume_ml, 0);
	$: flavorTotalPct = flavorIngredients.reduce((s, i) => s + i.percentage, 0);
</script>

<div class="space-y-4">
	{#if $calculating}
		<div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
			<svg class="animate-spin h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
			</svg>
			Calculating...
		</div>
	{/if}

	{#if $calcError}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-md px-3 py-2 text-sm">
			{$calcError}
		</div>
	{/if}

	{#if $result && !$calculating}
		<!-- Warnings -->
		{#if $result.warnings.length > 0}
			<div class="space-y-1">
				{#each $result.warnings as w}
					<div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-400 rounded-md px-3 py-2 text-sm">
						{w}
					</div>
				{/each}
			</div>
		{/if}

		<!-- Summary -->
		<div class="grid grid-cols-3 gap-3 text-center">
			<div class="bg-indigo-50 dark:bg-indigo-900/30 rounded-md px-3 py-2">
				<p class="text-xs text-indigo-500 dark:text-indigo-400 font-medium">Nicotine</p>
				<p class="text-lg font-bold text-indigo-800 dark:text-indigo-300">{$result.actual_nic_mg} mg/ml</p>
			</div>
			<div class="bg-sky-50 dark:bg-sky-900/30 rounded-md px-3 py-2">
				<p class="text-xs text-sky-500 dark:text-sky-400 font-medium">PG/VG</p>
				<p class="text-lg font-bold text-sky-800 dark:text-sky-300">{$result.actual_pg}/{$result.actual_vg}</p>
			</div>
			<div class="bg-emerald-50 dark:bg-emerald-900/30 rounded-md px-3 py-2">
				<p class="text-xs text-emerald-500 dark:text-emerald-400 font-medium">Total</p>
				<p class="text-lg font-bold text-emerald-800 dark:text-emerald-300">{$result.total_ml} ml</p>
			</div>
		</div>

		<!-- Ingredient table -->
		<div class="overflow-x-auto">
			<table class="w-full text-sm border-collapse">
				<thead>
					<tr class="border-b border-gray-200 dark:border-gray-700 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
						<th class="pb-2 pr-3">Ingredient</th>
						<th class="pb-2 pr-3 text-right">ml</th>
						<th class="pb-2 pr-3 text-right">g</th>
						<th class="pb-2 text-right">%</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
					{#each $result.ingredients as ing}
						<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
							<td class="py-2 pr-3 font-medium text-gray-800 dark:text-gray-200">{ing.name}</td>
							<td class="py-2 pr-3 text-right tabular-nums text-gray-700 dark:text-gray-300">{ing.volume_ml.toFixed(2)}</td>
							<td class="py-2 pr-3 text-right tabular-nums text-gray-700 dark:text-gray-300">{ing.weight_g.toFixed(2)}</td>
							<td class="py-2 text-right tabular-nums text-gray-500 dark:text-gray-400">{ing.percentage.toFixed(1)}%</td>
						</tr>
					{/each}
				</tbody>
				<tfoot>
					<tr class="border-t-2 border-gray-300 dark:border-gray-600 font-semibold text-gray-800 dark:text-gray-200">
						<td class="pt-2 pr-3">Total</td>
						<td class="pt-2 pr-3 text-right tabular-nums">{$result.total_ml.toFixed(2)}</td>
						<td class="pt-2 pr-3 text-right tabular-nums">{totalG.toFixed(2)}</td>
						<td class="pt-2 text-right tabular-nums">{totalPct.toFixed(1)}%</td>
					</tr>
				</tfoot>
			</table>
		</div>

		<!-- Recipe summary -->
		<dl class="space-y-1 text-sm border-t border-gray-100 dark:border-gray-800 pt-3">
			<div>
				<span class="font-bold text-gray-800 dark:text-gray-200">Strength:</span>
				<span class="text-gray-700 dark:text-gray-300 ml-1">{$result.actual_nic_mg} mg/mL</span>
			</div>
			<div>
				<span class="font-bold text-gray-800 dark:text-gray-200">PG/VG ratio:</span>
				<span class="text-gray-700 dark:text-gray-300 ml-1">{$result.actual_pg}/{$result.actual_vg}</span>
			</div>
			<div>
				<span class="font-bold text-gray-800 dark:text-gray-200">Flavor total:</span>
				<span class="text-gray-700 dark:text-gray-300 ml-1">{flavorTotalMl.toFixed(2)} ml ({flavorTotalPct.toFixed(1)}%)</span>
			</div>
		</dl>
		<CostPanel />

	{:else if !$calculating && !$calcError}
		<p class="text-sm text-gray-400 dark:text-gray-500 italic">Results will appear here.</p>
	{/if}
</div>
