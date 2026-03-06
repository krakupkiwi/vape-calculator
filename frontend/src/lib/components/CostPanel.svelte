<script lang="ts">
	import { result } from '$lib/stores/recipe';

	const BOTTLE_SIZES = [10, 30, 60, 100, 120];

	$: hasCost = ($result?.total_cost ?? 0) > 0;
	$: ingredients = $result?.ingredients ?? [];
	$: totalCost = $result?.total_cost ?? 0;
	$: costPerMl = $result?.cost_per_ml ?? 0;
	$: batchMl = $result?.total_ml ?? 0;
</script>

{#if hasCost}
	<div class="space-y-3 border-t border-gray-100 dark:border-gray-800 pt-4">
		<p class="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">Cost Breakdown</p>

		<!-- Per-ingredient cost table -->
		<div class="overflow-x-auto">
			<table class="w-full text-sm border-collapse">
				<thead>
					<tr class="border-b border-gray-200 dark:border-gray-700 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
						<th class="pb-2 pr-3">Ingredient</th>
						<th class="pb-2 pr-3 text-right">ml</th>
						<th class="pb-2 text-right">Cost</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
					{#each ingredients as ing}
						{#if ing.cost > 0}
							<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
								<td class="py-1.5 pr-3 text-gray-700 dark:text-gray-300">{ing.name}</td>
								<td class="py-1.5 pr-3 text-right tabular-nums text-gray-500 dark:text-gray-400">{ing.volume_ml.toFixed(2)}</td>
								<td class="py-1.5 text-right tabular-nums text-gray-700 dark:text-gray-300">${ing.cost.toFixed(3)}</td>
							</tr>
						{/if}
					{/each}
				</tbody>
				<tfoot>
					<tr class="border-t-2 border-gray-300 dark:border-gray-600 font-semibold text-gray-800 dark:text-gray-200">
						<td class="pt-2 pr-3" colspan="2">Total ({batchMl.toFixed(0)} ml)</td>
						<td class="pt-2 text-right tabular-nums">${totalCost.toFixed(3)}</td>
					</tr>
					<tr class="text-gray-500 dark:text-gray-400 text-xs">
						<td class="pt-1 pr-3" colspan="2">Cost per ml</td>
						<td class="pt-1 text-right tabular-nums">${costPerMl.toFixed(4)}</td>
					</tr>
				</tfoot>
			</table>
		</div>

		<!-- Per-bottle grid -->
		<div>
			<p class="text-xs text-gray-400 dark:text-gray-500 mb-2">Cost per bottle size</p>
			<div class="grid grid-cols-5 gap-2">
				{#each BOTTLE_SIZES as size}
					<div class="bg-gray-50 dark:bg-gray-800 rounded-md px-2 py-2 text-center">
						<p class="text-xs text-gray-400 dark:text-gray-500">{size} ml</p>
						<p class="text-sm font-semibold text-gray-800 dark:text-gray-200">${(costPerMl * size).toFixed(2)}</p>
					</div>
				{/each}
			</div>
		</div>
	</div>
{/if}
