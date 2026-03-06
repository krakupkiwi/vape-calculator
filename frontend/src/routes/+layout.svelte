<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { loadFlavors } from '$lib/stores/flavors';
	import Toast from '$lib/components/Toast.svelte';
	import { Menu, X, FlaskConical, Moon, Sun } from 'lucide-svelte';

	let { children } = $props();

	let mobileOpen = $state(false);
	let dark = $state(false);

	onMount(() => {
		loadFlavors();
		dark = localStorage.getItem('theme') === 'dark' ||
			(!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
		applyTheme(dark);
	});

	function applyTheme(isDark: boolean) {
		document.documentElement.classList.toggle('dark', isDark);
		localStorage.setItem('theme', isDark ? 'dark' : 'light');
	}

	function toggleDark() {
		dark = !dark;
		applyTheme(dark);
	}

	const navLinks = [
		{ href: '/', label: 'Calculator' },
		{ href: '/recipes', label: 'Recipes' },
		{ href: '/flavors', label: 'Flavors' },
	];

	function isActive(href: string) {
		if (href === '/') return $page.url.pathname === '/';
		return $page.url.pathname.startsWith(href);
	}
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
	<header class="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
		<div class="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
			<!-- Logo -->
			<FlaskConical size={22} class="text-indigo-600 shrink-0" />
			<a href="/" class="text-xl font-bold text-gray-900 dark:text-white tracking-tight hover:text-indigo-600 transition">
				Vape Calculator
			</a>

			<!-- Desktop nav -->
			<nav class="hidden sm:flex items-center gap-1 ml-4">
				{#each navLinks as link}
					<a
						href={link.href}
						class="px-3 py-1.5 text-sm rounded-md transition
							{isActive(link.href)
								? 'bg-indigo-50 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-medium'
								: 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'}"
					>
						{link.label}
					</a>
				{/each}
			</nav>

			<div class="ml-auto flex items-center gap-2">
				<!-- Dark mode toggle -->
				<button
					type="button"
					onclick={toggleDark}
					class="p-1.5 rounded-md text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
					aria-label="Toggle dark mode"
				>
					{#if dark}
						<Sun size={18} />
					{:else}
						<Moon size={18} />
					{/if}
				</button>

				<!-- Mobile hamburger -->
				<button
					type="button"
					onclick={() => (mobileOpen = !mobileOpen)}
					class="sm:hidden p-1.5 rounded-md text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
					aria-label="Toggle menu"
				>
					{#if mobileOpen}
						<X size={20} />
					{:else}
						<Menu size={20} />
					{/if}
				</button>
			</div>
		</div>

		<!-- Mobile nav drawer -->
		{#if mobileOpen}
			<div class="sm:hidden border-t border-gray-100 dark:border-gray-800 px-4 py-2 flex flex-col gap-1">
				{#each navLinks as link}
					<a
						href={link.href}
						onclick={() => (mobileOpen = false)}
						class="px-3 py-2 text-sm rounded-md transition
							{isActive(link.href)
								? 'bg-indigo-50 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-medium'
								: 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}"
					>
						{link.label}
					</a>
				{/each}
			</div>
		{/if}
	</header>

	<main class="max-w-5xl mx-auto px-4 py-6">
		{@render children()}
	</main>
</div>

<Toast />
