<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import Calculator from '$lib/components/Calculator.svelte';
	import ResultsPanel from '$lib/components/ResultsPanel.svelte';
	import { recipe, result, calculating, calcError, stateToRecipeIn } from '$lib/stores/recipe';
	import { calculate } from '$lib/api/client';
	import { recipesApi } from '$lib/api/recipes';
	import { showToast } from '$lib/stores/toast';
	import { Save, X, Info } from 'lucide-svelte';

	let debounceTimer: ReturnType<typeof setTimeout>;

	// Onboarding tip — shown once, dismissed to localStorage
	let showTip = $state(false);
	onMount(() => {
		if (!localStorage.getItem('vape_onboarded')) showTip = true;
	});
	function dismissTip() {
		showTip = false;
		localStorage.setItem('vape_onboarded', '1');
	}

	// Re-run calculation whenever recipe state changes
	const unsubscribe = recipe.subscribe((r) => {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(async () => {
			if (r.batch_size_ml <= 0) return;
			calculating.set(true);
			calcError.set(null);
			try {
				const res = await calculate({
					batch_size_ml: r.batch_size_ml,
					target_nic_mg: r.target_nic_mg,
					nic_base_strength_mg: r.nic_base_strength_mg,
					nic_base_pg: r.nic_base_pg / 100,
					nic_base_vg: r.nic_base_vg / 100,
					nic_base_density: r.nic_base_density,
					nic_cost_per_ml: r.nic_cost_per_ml,
					target_pg: r.target_pg / 100,
					target_vg: r.target_vg / 100,
					pg_cost_per_ml: r.pg_cost_per_ml,
					vg_cost_per_ml: r.vg_cost_per_ml,
					flavors: r.flavors
						.filter((f) => f.name.trim() !== '')
						.map((f) => ({
							name: f.name,
							percentage: f.percentage,
							pg_ratio: f.pg_ratio,
							vg_ratio: f.vg_ratio,
							density: f.density,
							cost_per_ml: f.cost_per_ml
						}))
				});
				result.set(res);
			} catch (e) {
				calcError.set((e as Error).message);
				result.set(null);
			} finally {
				calculating.set(false);
			}
		}, 150);
	});

	onDestroy(() => {
		unsubscribe();
		clearTimeout(debounceTimer);
	});

	// --- Save recipe ---
	let saving = false;
	let savedId: number | null = null;

	async function saveRecipe() {
		if (saving) return;
		saving = true;
		try {
			const payload = stateToRecipeIn($recipe);
			const saved = await recipesApi.create(payload);
			savedId = saved.id;
			showToast(`Recipe saved! <a href="/recipes/${saved.id}" class="underline font-medium">View</a>`, 'success', 5000);
		} catch (e) {
			showToast((e as Error).message, 'error');
		} finally {
			saving = false;
		}
	}

	// Ctrl+S shortcut
	function handleKeydown(e: KeyboardEvent) {
		if ((e.ctrlKey || e.metaKey) && e.key === 's') {
			e.preventDefault();
			saveRecipe();
		}
	}

	onMount(() => {
		window.addEventListener('keydown', handleKeydown);
		return () => window.removeEventListener('keydown', handleKeydown);
	});
</script>

{#if showTip}
	<div class="mb-4 flex items-start gap-3 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg px-4 py-3 text-sm text-indigo-800 dark:text-indigo-300">
		<Info size={16} class="shrink-0 mt-0.5 text-indigo-500" />
		<div class="flex-1">
			<p class="font-medium mb-1">Welcome to Vape Calculator!</p>
			<ul class="space-y-0.5 text-indigo-700 dark:text-indigo-400">
				<li>Fill in batch size, nicotine strength, and PG/VG ratio — results update live.</li>
				<li>Add flavors by typing a name or searching the database.</li>
				<li>Set ingredient prices in the <a href="/flavors" class="underline font-medium">Flavors</a> page for cost tracking.</li>
				<li>Press <kbd class="bg-indigo-100 dark:bg-indigo-800 rounded px-1 font-mono text-xs">Ctrl+S</kbd> or click Save to store a recipe.</li>
			</ul>
		</div>
		<button type="button" onclick={dismissTip} class="shrink-0 text-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-200 transition" aria-label="Dismiss">
			<X size={16} />
		</button>
	</div>
{/if}

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
	<section class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-5">
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-base font-semibold text-gray-800 dark:text-gray-200">Recipe</h2>
			<button
				type="button"
				onclick={saveRecipe}
				disabled={saving}
				class="flex items-center gap-1.5 text-sm bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-md px-3 py-1.5 transition"
				title="Save recipe (Ctrl+S)"
			>
				{#if saving}
					<svg class="animate-spin h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
					</svg>
					Saving...
				{:else}
					<Save size={14} />
					Save
				{/if}
			</button>
		</div>

		<Calculator />
	</section>

	<section class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-5">
		<h2 class="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">Results</h2>
		<ResultsPanel />
	</section>
</div>
