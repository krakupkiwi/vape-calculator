<script lang="ts">
	import { toasts, dismissToast } from '$lib/stores/toast';
	import { CheckCircle, XCircle, Info, X } from 'lucide-svelte';
</script>

<div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
	{#each $toasts as toast (toast.id)}
		<div
			class="pointer-events-auto flex items-start gap-3 rounded-lg shadow-lg px-4 py-3 text-sm min-w-64 max-w-sm
				{toast.type === 'success' ? 'bg-emerald-600 text-white' :
				 toast.type === 'error'   ? 'bg-red-600 text-white' :
				                            'bg-gray-800 text-white'}"
		>
			<span class="shrink-0 mt-0.5">
				{#if toast.type === 'success'}
					<CheckCircle size={16} />
				{:else if toast.type === 'error'}
					<XCircle size={16} />
				{:else}
					<Info size={16} />
				{/if}
			</span>
			<span class="flex-1">{@html toast.message}</span>
			<button
				type="button"
				onclick={() => dismissToast(toast.id)}
				class="shrink-0 opacity-70 hover:opacity-100 transition"
				aria-label="Dismiss"
			>
				<X size={14} />
			</button>
		</div>
	{/each}
</div>
