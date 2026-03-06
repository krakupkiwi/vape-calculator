<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { recipesApi, type RecipeOut, type RatingOut } from '$lib/api/recipes';
	import { loadRecipeIntoStore } from '$lib/stores/recipe';
	import StarRating from '$lib/components/StarRating.svelte';
	import { showToast } from '$lib/stores/toast';
	import { marked } from 'marked';
	import { Download, Upload, Copy, Trash2, Calculator } from 'lucide-svelte';

	let recipe: RecipeOut | null = $state(null);
	let loading = $state(true);
	let error: string | null = $state(null);
	let confirmDelete = $state(false);
	let actionBusy = $state(false);

	// Rating state
	let ratings: RatingOut[] = $state([]);
	let currentRating = $state(0);
	let ratingNote = $state('');
	let submittingRating = $state(false);

	// Import ref
	let importInput: HTMLInputElement = $state()!;

	const id = Number($page.params.id);

	async function load() {
		loading = true;
		error = null;
		try {
			[recipe, ratings] = await Promise.all([
				recipesApi.get(id),
				recipesApi.ratings(id)
			]);
			currentRating = recipe?.rating ?? 0;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	load();

	async function handleRate(stars: number) {
		currentRating = stars;
	}

	async function submitRating() {
		if (!currentRating) return;
		submittingRating = true;
		try {
			const r = await recipesApi.rate(id, { stars: currentRating, note: ratingNote || undefined });
			ratings = [r, ...ratings];
			ratingNote = '';
			if (recipe) recipe = { ...recipe, rating: currentRating } as RecipeOut;
			showToast('Rating saved');
		} catch (e) {
			showToast((e as Error).message, 'error');
		} finally {
			submittingRating = false;
		}
	}

	async function handleDelete() {
		actionBusy = true;
		try {
			await recipesApi.delete(id);
			goto('/recipes');
		} catch (e) {
			showToast((e as Error).message, 'error');
			actionBusy = false;
		}
	}

	async function handleClone() {
		actionBusy = true;
		try {
			const cloned = await recipesApi.clone(id);
			showToast('Recipe cloned');
			goto(`/recipes/${cloned.id}`);
		} catch (e) {
			showToast((e as Error).message, 'error');
			actionBusy = false;
		}
	}

	function handleLoadIntoCalculator() {
		if (!recipe) return;
		loadRecipeIntoStore(recipe);
		goto('/');
	}

	function exportJson() {
		if (!recipe) return;
		const blob = new Blob([JSON.stringify(recipe, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `${recipe.name.replace(/[^a-z0-9]/gi, '_')}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}

	async function handleImport(e: Event) {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (!file) return;
		try {
			const text = await file.text();
			const data = JSON.parse(text);
			await recipesApi.create(data);
			showToast('Recipe imported');
			goto('/recipes');
		} catch {
			showToast('Invalid recipe file', 'error');
		}
		(e.target as HTMLInputElement).value = '';
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleString(undefined, {
			year: 'numeric', month: 'short', day: 'numeric',
			hour: '2-digit', minute: '2-digit'
		});
	}

	function formatDateShort(iso: string) {
		return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
	}

	function renderMarkdown(text: string): string {
		return marked(text) as string;
	}
</script>

{#if loading}
	<div class="flex items-center gap-2 text-sm text-gray-400 dark:text-gray-500 py-8 justify-center">
		<svg class="animate-spin h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
			<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
		</svg>
		Loading recipe...
	</div>
{:else if error}
	<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-md px-3 py-2 text-sm">{error}</div>
{:else if recipe}
	<div class="max-w-2xl space-y-5">
		<!-- Header -->
		<div class="flex items-start gap-3">
			<div class="flex-1">
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">{recipe.name}</h1>
				{#if recipe.description}
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{recipe.description}</p>
				{/if}
				<p class="text-xs text-gray-400 mt-1">Saved {formatDate(recipe.created_at)}</p>
			</div>
			<div class="flex flex-wrap gap-2 shrink-0">
				<button
					type="button"
					onclick={handleLoadIntoCalculator}
					class="flex items-center gap-1.5 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-md px-3 py-1.5 transition"
				>
					<Calculator size={14} />
					Load
				</button>
				<button
					type="button"
					onclick={handleClone}
					disabled={actionBusy}
					class="flex items-center gap-1.5 text-sm border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-md px-3 py-1.5 transition disabled:opacity-40"
				>
					{#if actionBusy}
						<svg class="animate-spin h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
						</svg>
					{:else}
						<Copy size={14} />
					{/if}
					Clone
				</button>
				<button
					type="button"
					onclick={exportJson}
					class="flex items-center gap-1.5 text-sm border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-md px-3 py-1.5 transition"
				>
					<Download size={14} />
					Export
				</button>
			</div>
		</div>

		<!-- Summary cards -->
		<div class="grid grid-cols-3 gap-3 text-center">
			<div class="bg-indigo-50 dark:bg-indigo-950 rounded-md px-3 py-2">
				<p class="text-xs text-indigo-500 font-medium">Batch Size</p>
				<p class="text-lg font-bold text-indigo-800 dark:text-indigo-300">{recipe.batch_size_ml} ml</p>
			</div>
			<div class="bg-sky-50 dark:bg-sky-950 rounded-md px-3 py-2">
				<p class="text-xs text-sky-500 font-medium">Nicotine</p>
				<p class="text-lg font-bold text-sky-800 dark:text-sky-300">{recipe.target_nic_mg} mg/mL</p>
			</div>
			<div class="bg-emerald-50 dark:bg-emerald-950 rounded-md px-3 py-2">
				<p class="text-xs text-emerald-500 font-medium">PG/VG</p>
				<p class="text-lg font-bold text-emerald-800 dark:text-emerald-300">
					{Math.round(recipe.pg_ratio * 100)}/{Math.round(recipe.vg_ratio * 100)}
				</p>
			</div>
		</div>

		<!-- Flavors -->
		<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-4 print:shadow-none">
			<h2 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Flavors</h2>
			{#if recipe.flavors.length === 0}
				<p class="text-sm text-gray-400 italic">No flavors.</p>
			{:else}
				<table class="w-full text-sm">
					<thead>
						<tr class="border-b border-gray-100 dark:border-gray-800 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
							<th class="pb-2 text-left">Name</th>
							<th class="pb-2 text-right">%</th>
							<th class="pb-2 text-right">PG/VG</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-50 dark:divide-gray-800">
						{#each recipe.flavors as f}
							<tr>
								<td class="py-1.5 font-medium text-gray-800 dark:text-gray-200">{f.name}</td>
								<td class="py-1.5 text-right tabular-nums text-gray-600 dark:text-gray-400">{f.percentage}%</td>
								<td class="py-1.5 text-right tabular-nums text-gray-500 dark:text-gray-400">
									{Math.round(f.pg_ratio * 100)}/{Math.round(f.vg_ratio * 100)}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		</div>

		<!-- Nic base -->
		{#if recipe.target_nic_mg > 0}
			<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-4 print:shadow-none">
				<h2 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Nicotine Base</h2>
				<dl class="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
					<div class="flex justify-between"><dt class="text-gray-500">Strength</dt><dd class="font-medium dark:text-gray-200">{recipe.nic_base_strength_mg} mg/mL</dd></div>
					<div class="flex justify-between"><dt class="text-gray-500">PG/VG</dt><dd class="font-medium dark:text-gray-200">{Math.round(recipe.nic_base_pg * 100)}/{Math.round(recipe.nic_base_vg * 100)}</dd></div>
					<div class="flex justify-between"><dt class="text-gray-500">Density</dt><dd class="font-medium dark:text-gray-200">{recipe.nic_base_density} g/mL</dd></div>
				</dl>
			</div>
		{/if}

		<!-- Notes (Markdown) -->
		{#if recipe.notes}
			<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-4 print:shadow-none">
				<h2 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Notes</h2>
				<div class="prose prose-sm max-w-none text-gray-700 dark:text-gray-300">{@html renderMarkdown(recipe.notes)}</div>
			</div>
		{/if}

		<!-- Rating section (hidden when printing) -->
		<div class="print:hidden bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-4 space-y-4">
			<h2 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Rate this Recipe</h2>

			<div class="space-y-3">
				<StarRating value={currentRating} onrate={handleRate} />
				<textarea
					bind:value={ratingNote}
					rows="2"
					placeholder="Add a note (optional)..."
					class="w-full border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
				></textarea>
				<button
					type="button"
					onclick={submitRating}
					disabled={!currentRating || submittingRating}
					class="text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-md px-3 py-1.5 transition disabled:opacity-40"
				>
					{submittingRating ? 'Saving...' : 'Save Rating'}
				</button>
			</div>

			<!-- Rating history -->
			{#if ratings.length > 0}
				<div class="border-t border-gray-100 dark:border-gray-800 pt-3 space-y-2">
					<p class="text-xs font-medium text-gray-500 uppercase tracking-wide">History</p>
					{#each ratings as r}
						<div class="flex items-start gap-3">
							<StarRating value={r.stars} readonly={true} />
							<div class="flex-1 min-w-0">
								{#if r.note}
									<p class="text-sm text-gray-700 dark:text-gray-300">{r.note}</p>
								{/if}
								<p class="text-xs text-gray-400">{formatDateShort(r.created_at)}</p>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Delete + import (hidden when printing) -->
		<div class="print:hidden border-t border-gray-100 dark:border-gray-800 pt-4 flex items-center justify-between">
			{#if confirmDelete}
				<div class="flex items-center gap-2">
					<span class="text-sm text-gray-600 dark:text-gray-400">Delete permanently?</span>
					<button
						type="button"
						onclick={handleDelete}
						disabled={actionBusy}
						class="flex items-center gap-1.5 text-sm bg-red-500 hover:bg-red-600 text-white rounded-md px-3 py-1.5 transition disabled:opacity-40"
					>
						<Trash2 size={13} />
						Yes, delete
					</button>
					<button
						type="button"
						onclick={() => (confirmDelete = false)}
						class="text-sm border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md px-3 py-1.5 transition"
					>
						Cancel
					</button>
				</div>
			{:else}
				<button
					type="button"
					onclick={() => (confirmDelete = true)}
					class="flex items-center gap-1.5 text-sm text-red-500 hover:text-red-700 transition"
				>
					<Trash2 size={13} />
					Delete recipe
				</button>
			{/if}

			<label class="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-indigo-600 cursor-pointer transition">
				<Upload size={13} />
				Import JSON
				<input
					type="file"
					accept=".json"
					class="hidden"
					bind:this={importInput}
					onchange={handleImport}
				/>
			</label>
		</div>
	</div>
{/if}
