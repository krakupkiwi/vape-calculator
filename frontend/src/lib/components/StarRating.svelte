<script lang="ts">
	interface Props {
		value: number;        // current rating (0 = unrated)
		readonly?: boolean;
		onrate?: (stars: number) => void;
	}

	let { value, readonly = false, onrate }: Props = $props();

	let hovered = $state(0);

	function handleClick(star: number) {
		if (!readonly) onrate?.(star);
	}
</script>

<div class="flex items-center gap-0.5" role={readonly ? 'img' : 'group'} aria-label="Rating: {value} out of 5">
	{#each [1, 2, 3, 4, 5] as star}
		<button
			type="button"
			disabled={readonly}
			onclick={() => handleClick(star)}
			onmouseenter={() => { if (!readonly) hovered = star; }}
			onmouseleave={() => { if (!readonly) hovered = 0; }}
			class="text-2xl leading-none transition-colors disabled:cursor-default
				{(hovered || value) >= star ? 'text-amber-400' : 'text-gray-200'}
				{!readonly ? 'hover:scale-110 cursor-pointer' : ''}"
			aria-label="{star} star{star !== 1 ? 's' : ''}"
		>
			★
		</button>
	{/each}
</div>
