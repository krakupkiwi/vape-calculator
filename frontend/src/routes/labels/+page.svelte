<script lang="ts">
	import { onMount } from 'svelte';
	import { Tag, Download, RefreshCw, Upload, AlertCircle, Loader2 } from 'lucide-svelte';
	import { addToast } from '$lib/stores/toast';

	interface RecipeSummary {
		id: number;
		name: string;
		batch_size_ml: number;
		target_nic_mg: number;
		pg_ratio: number;
		vg_ratio: number;
	}

	interface TemplateInfo {
		name: string;
		size_bytes: number;
	}

	// State
	let recipes = $state<RecipeSummary[]>([]);
	let templates = $state<TemplateInfo[]>([]);
	let loadingRecipes = $state(true);
	let loadingTemplates = $state(true);
	let previewing = $state(false);
	let downloading = $state(false);
	let uploading = $state(false);

	let selectedRecipeId = $state<number | null>(null);
	let selectedTemplate = $state('default_label.html');
	let author = $state('');
	let pageWidth = $state(62);
	let pageHeight = $state(29);

	let previewHtml = $state('');
	let previewError = $state('');

	let fileInput: HTMLInputElement;

	onMount(async () => {
		await Promise.all([fetchRecipes(), fetchTemplates()]);
	});

	async function fetchRecipes() {
		loadingRecipes = true;
		try {
			const res = await fetch('/api/recipes');
			if (!res.ok) throw new Error('Failed to load recipes');
			recipes = await res.json();
			if (recipes.length > 0) selectedRecipeId = recipes[0].id;
		} catch (e) {
			addToast('Could not load recipes.', 'error');
		} finally {
			loadingRecipes = false;
		}
	}

	async function fetchTemplates() {
		loadingTemplates = true;
		try {
			const res = await fetch('/api/labels/templates');
			if (!res.ok) throw new Error('Failed to load templates');
			templates = await res.json();
			if (templates.length > 0) selectedTemplate = templates[0].name;
		} catch (e) {
			addToast('Could not load templates.', 'error');
		} finally {
			loadingTemplates = false;
		}
	}

	async function preview() {
		if (!selectedRecipeId) return;
		previewing = true;
		previewError = '';
		previewHtml = '';
		try {
			const res = await fetch('/api/labels/preview', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					recipe_id: selectedRecipeId,
					template_name: selectedTemplate,
					page_width: pageWidth,
					page_height: pageHeight,
					author
				})
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: res.statusText }));
				throw new Error(err.detail ?? 'Preview failed');
			}
			previewHtml = await res.text();
		} catch (e: any) {
			previewError = e.message ?? 'Preview failed';
		} finally {
			previewing = false;
		}
	}

	async function downloadPdf() {
		if (!selectedRecipeId) return;
		downloading = true;
		try {
			const res = await fetch('/api/labels/generate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					recipe_id: selectedRecipeId,
					template_name: selectedTemplate,
					page_width: pageWidth,
					page_height: pageHeight,
					author
				})
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: res.statusText }));
				throw new Error(err.detail ?? 'PDF generation failed');
			}
			const blob = await res.blob();
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			const disposition = res.headers.get('Content-Disposition') ?? '';
			const match = disposition.match(/filename="([^"]+)"/);
			a.download = match ? match[1] : 'label.pdf';
			a.href = url;
			a.click();
			URL.revokeObjectURL(url);
		} catch (e: any) {
			addToast(e.message ?? 'PDF generation failed', 'error');
		} finally {
			downloading = false;
		}
	}

	async function uploadTemplate() {
		const file = fileInput?.files?.[0];
		if (!file) return;
		if (!file.name.endsWith('.html')) {
			addToast('Only .html files are accepted.', 'error');
			return;
		}
		uploading = true;
		try {
			const form = new FormData();
			form.append('file', file);
			const res = await fetch('/api/labels/templates/upload', {
				method: 'POST',
				body: form
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: res.statusText }));
				throw new Error(err.detail ?? 'Upload failed');
			}
			const info: TemplateInfo = await res.json();
			templates = [...templates.filter((t) => t.name !== info.name), info];
			selectedTemplate = info.name;
			addToast(`Template "${info.name}" uploaded.`, 'success');
			if (fileInput) fileInput.value = '';
		} catch (e: any) {
			addToast(e.message ?? 'Upload failed', 'error');
		} finally {
			uploading = false;
		}
	}

	const inputClass =
		'border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full';
</script>

<div class="space-y-6">
	<!-- Page header -->
	<div class="flex items-center gap-2">
		<Tag size={20} class="text-indigo-600" />
		<h1 class="text-2xl font-bold text-gray-900 dark:text-white">Label Generator</h1>
	</div>

	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Settings panel -->
		<div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 space-y-4">
			<h2 class="font-semibold text-gray-900 dark:text-white">Label Settings</h2>

			<!-- Recipe selector -->
			<div>
				<label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Recipe</label>
				{#if loadingRecipes}
					<div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
						<Loader2 size={14} class="animate-spin" /> Loading recipes…
					</div>
				{:else if recipes.length === 0}
					<p class="text-sm text-gray-500 dark:text-gray-400">
						No recipes found. <a href="/recipes" class="text-indigo-600 dark:text-indigo-400 underline">Create one first.</a>
					</p>
				{:else}
					<select
						class={inputClass}
						bind:value={selectedRecipeId}
					>
						{#each recipes as r}
							<option value={r.id}>{r.name} — {r.batch_size_ml}ml</option>
						{/each}
					</select>
				{/if}
			</div>

			<!-- Template selector -->
			<div>
				<label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Template</label>
				{#if loadingTemplates}
					<div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
						<Loader2 size={14} class="animate-spin" /> Loading templates…
					</div>
				{:else if templates.length === 0}
					<p class="text-sm text-gray-500 dark:text-gray-400">No templates found.</p>
				{:else}
					<select class={inputClass} bind:value={selectedTemplate}>
						{#each templates as t}
							<option value={t.name}>{t.name}</option>
						{/each}
					</select>
				{/if}
			</div>

			<!-- Author -->
			<div>
				<label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Author / Mixer name</label>
				<input type="text" class={inputClass} placeholder="e.g. Sam" bind:value={author} />
			</div>

			<!-- Page size -->
			<div class="grid grid-cols-2 gap-3">
				<div>
					<label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Width (mm)</label>
					<input type="number" class={inputClass} min="10" max="300" bind:value={pageWidth} />
				</div>
				<div>
					<label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Height (mm)</label>
					<input type="number" class={inputClass} min="10" max="300" bind:value={pageHeight} />
				</div>
			</div>

			<!-- Actions -->
			<div class="flex gap-2 pt-1">
				<button
					type="button"
					onclick={preview}
					disabled={previewing || !selectedRecipeId || loadingRecipes}
					class="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition"
				>
					{#if previewing}
						<Loader2 size={14} class="animate-spin" />
					{:else}
						<RefreshCw size={14} />
					{/if}
					Preview
				</button>

				<button
					type="button"
					onclick={downloadPdf}
					disabled={downloading || !selectedRecipeId || loadingRecipes}
					class="flex items-center gap-1.5 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition"
				>
					{#if downloading}
						<Loader2 size={14} class="animate-spin" />
					{:else}
						<Download size={14} />
					{/if}
					Download PDF
				</button>
			</div>

			<!-- Note about WeasyPrint -->
			<p class="text-xs text-gray-500 dark:text-gray-500">
				PDF generation requires WeasyPrint and only works inside Docker. Preview always works.
			</p>

			<!-- Template upload -->
			<div class="border-t border-gray-100 dark:border-gray-800 pt-4 space-y-2">
				<label for="template-upload" class="block text-xs font-medium text-gray-600 dark:text-gray-400">Upload custom template (.html)</label>
				<div class="flex gap-2">
					<input
						id="template-upload"
						type="file"
						accept=".html"
						bind:this={fileInput}
						class="text-sm text-gray-700 dark:text-gray-300 file:mr-2 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-indigo-50 file:text-indigo-700 dark:file:bg-indigo-900/40 dark:file:text-indigo-300"
					/>
					<button
						type="button"
						onclick={uploadTemplate}
						disabled={uploading}
						class="flex items-center gap-1.5 px-3 py-1.5 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 text-gray-800 dark:text-gray-200 text-xs font-medium rounded-lg transition"
					>
						{#if uploading}
							<Loader2 size={12} class="animate-spin" />
						{:else}
							<Upload size={12} />
						{/if}
						Upload
					</button>
				</div>
			</div>
		</div>

		<!-- Preview panel -->
		<div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 space-y-3">
			<h2 class="font-semibold text-gray-900 dark:text-white">Preview</h2>

			{#if previewError}
				<div class="flex items-start gap-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-lg p-3 text-sm">
					<AlertCircle size={16} class="shrink-0 mt-0.5" />
					{previewError}
				</div>
			{/if}

			{#if previewHtml}
				<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-white" style="height: 300px;">
					<iframe
						srcdoc={previewHtml}
						title="Label preview"
						class="w-full h-full border-0"
						sandbox="allow-same-origin"
					></iframe>
				</div>
			{:else if !previewError}
				<div class="flex flex-col items-center justify-center border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg h-64 text-gray-400 dark:text-gray-600 gap-2">
					<Tag size={32} />
					<p class="text-sm">Select a recipe and click Preview</p>
				</div>
			{/if}
		</div>
	</div>
</div>
