<script lang="ts">
	import { searchFlavors } from '$lib/stores/flavors';
	import type { FlavorOut } from '$lib/stores/flavors';

	interface Props {
		value: string;
		onselect: (flavor: FlavorOut) => void;
		oninput?: (name: string) => void;
	}

	let { value, onselect, oninput }: Props = $props();

	let query = $state('');
	let results = $state<FlavorOut[]>([]);
	let open = $state(false);
	let activeIndex = $state(-1);
	let containerEl: HTMLDivElement;

	$effect(() => {
		query = value;
	});

	function handleInput(e: Event) {
		const val = (e.target as HTMLInputElement).value;
		query = val;
		oninput?.(val);
		results = val.trim() ? searchFlavors(val) : [];
		open = results.length > 0;
		activeIndex = -1;
	}

	function selectFlavor(flavor: FlavorOut) {
		query = `${flavor.manufacturer} ${flavor.name}`;
		open = false;
		results = [];
		onselect(flavor);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (!open) return;
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			activeIndex = Math.min(activeIndex + 1, results.length - 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			activeIndex = Math.max(activeIndex - 1, -1);
		} else if (e.key === 'Enter' && activeIndex >= 0) {
			e.preventDefault();
			selectFlavor(results[activeIndex]);
		} else if (e.key === 'Escape') {
			open = false;
		}
	}

	function handleBlur() {
		// Delay so click on dropdown item fires first
		setTimeout(() => { open = false; }, 150);
	}
</script>

<div class="relative" bind:this={containerEl}>
	<input
		type="text"
		class="w-full border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
		placeholder="e.g. TFA Strawberry"
		value={query}
		oninput={handleInput}
		onkeydown={handleKeydown}
		onblur={handleBlur}
	/>
	{#if open && results.length > 0}
		<ul class="absolute z-50 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg max-h-56 overflow-y-auto text-sm">
			{#each results as flavor, i}
				<li>
					<button
						type="button"
						class="w-full text-left px-3 py-2 hover:bg-indigo-50 dark:hover:bg-indigo-900/40 transition {i === activeIndex ? 'bg-indigo-50 dark:bg-indigo-900/40' : ''}"
						onmousedown={() => selectFlavor(flavor)}
					>
						<span class="font-medium text-gray-800 dark:text-gray-200">{flavor.name}</span>
						<span class="text-gray-400 dark:text-gray-500 ml-1">{flavor.manufacturer}</span>
					</button>
				</li>
			{/each}
		</ul>
	{/if}
</div>
