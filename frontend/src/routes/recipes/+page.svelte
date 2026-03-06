<script lang="ts">
	import { recipesApi, type RecipeSummary } from '$lib/api/recipes';
	import StarRating from '$lib/components/StarRating.svelte';

	let recipes: RecipeSummary[] = $state([]);
	let loading = $state(true);
	let error: string | null = $state(null);
	let sort: 'date' | 'name' | 'rating' = $state('date');
	let minRating = $state(0);
	let search = $state('');
	let confirmDeleteId: number | null = $state(null);
	let actionBusy = $state(false);

	async function load() {
		loading = true;
		error = null;
		try {
			recipes = await recipesApi.list(sort, minRating || undefined);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		sort; minRating; // re-run on filter change
		load();
	});

	const filtered = $derived(
		recipes.filter((r) => r.name.toLowerCase().includes(search.toLowerCase()))
	);

	async function deleteRecipe(id: number) {
		actionBusy = true;
		try {
			await recipesApi.delete(id);
			recipes = recipes.filter((r) => r.id !== id);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			confirmDeleteId = null;
			actionBusy = false;
		}
	}

	async function cloneRecipe(id: number) {
		actionBusy = true;
		try {
			const cloned = await recipesApi.clone(id);
			recipes = [cloned as unknown as RecipeSummary, ...recipes];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			actionBusy = false;
		}
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
	}
</script>

<div class="space-y-4">
	<div class="flex flex-col sm:flex-row sm:items-center gap-3">
		<h1 class="text-xl font-bold text-gray-900 dark:text-white flex-1">Saved Recipes</h1>
		<a href="/" class="text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-md px-3 py-1.5 transition text-center">
			+ New Recipe
		</a>
	</div>

	<!-- Search + sort + filter -->
	<div class="flex flex-col sm:flex-row gap-2">
		<input
			type="search"
			placeholder="Search recipes..."
			bind:value={search}
			class="flex-1 border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
		/>
		<select
			bind:value={sort}
			class="border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
		>
			<option value="date">Sort: Newest first</option>
			<option value="name">Sort: Name A–Z</option>
			<option value="rating">Sort: Highest rated</option>
		</select>
		<select
			bind:value={minRating}
			class="border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
		>
			<option value={0}>All ratings</option>
			<option value={1}>★ 1+</option>
			<option value={2}>★★ 2+</option>
			<option value={3}>★★★ 3+</option>
			<option value={4}>★★★★ 4+</option>
			<option value={5}>★★★★★ 5 only</option>
		</select>
	</div>

	{#if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-md px-3 py-2 text-sm">{error}</div>
	{/if}

	{#if loading}
		<div class="flex items-center gap-2 text-sm text-gray-400 dark:text-gray-500 py-6 justify-center">
			<svg class="animate-spin h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
			</svg>
			Loading recipes...
		</div>
	{:else if filtered.length === 0}
		<div class="text-center py-12 text-gray-400 dark:text-gray-500">
			<p class="text-sm">{search ? 'No recipes match your search.' : 'No recipes saved yet.'}</p>
			{#if !search}
				<a href="/" class="mt-2 inline-block text-sm text-indigo-600 hover:underline">Create your first recipe</a>
			{/if}
		</div>
	{:else}
		<div class="space-y-2">
			{#each filtered as r (r.id)}
				<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm px-4 py-3 flex items-start gap-3">
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2">
							<a href="/recipes/{r.id}" class="font-semibold text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition truncate">
								{r.name}
							</a>
							{#if r.rating}
								<StarRating value={r.rating} readonly={true} />
							{/if}
						</div>
						<p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
							{r.batch_size_ml} ml &middot;
							{r.target_nic_mg} mg/mL &middot;
							{Math.round(r.pg_ratio * 100)}/{Math.round(r.vg_ratio * 100)} PG/VG &middot;
							{r.flavor_count} {r.flavor_count === 1 ? 'flavor' : 'flavors'} &middot;
							{formatDate(r.created_at)}
						</p>
						{#if r.description}
							<p class="text-xs text-gray-400 dark:text-gray-500 mt-1 truncate">{r.description}</p>
						{/if}
					</div>
					<div class="flex items-center gap-1 shrink-0">
						<button
							type="button"
							onclick={() => cloneRecipe(r.id)}
							disabled={actionBusy}
							class="text-xs text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 border border-gray-200 dark:border-gray-700 rounded px-2 py-1 transition disabled:opacity-40"
							title="Clone recipe"
						>
							Clone
						</button>
						{#if confirmDeleteId === r.id}
							<button
								type="button"
								onclick={() => deleteRecipe(r.id)}
								disabled={actionBusy}
								class="text-xs text-white bg-red-500 hover:bg-red-600 rounded px-2 py-1 transition disabled:opacity-40"
							>
								Confirm
							</button>
							<button
								type="button"
								onclick={() => (confirmDeleteId = null)}
								class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 border border-gray-200 dark:border-gray-700 rounded px-2 py-1 transition"
							>
								Cancel
							</button>
						{:else}
							<button
								type="button"
								onclick={() => (confirmDeleteId = r.id)}
								class="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 border border-gray-200 dark:border-gray-700 rounded px-2 py-1 transition"
								title="Delete recipe"
							>
								Delete
							</button>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
