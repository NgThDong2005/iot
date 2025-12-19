<script lang="ts">
	import type { Snippet } from 'svelte'

	type Props = {
		icon: string
		children: Snippet<[{ close: () => void }]>
		buttonClass?: string
		iconClass?: string
		ariaLabel?: string
	}

	let {
		icon,
		children,
		buttonClass = '',
		iconClass = 'w-6 h-6',
		ariaLabel = 'Toggle popup',
	}: Props = $props()

	let isOpen = $state(false)

	function close() {
		isOpen = false
	}
</script>

{#if isOpen}
	<!-- Backdrop for mobile/tablet -->
	<button
		type="button"
		class="fixed inset-0 bg-black/50 z-40 xl:hidden"
		onclick={close}
		aria-label="Close popup"
	></button>
	{@render children({ close })}
{:else}
	<button
		class="fixed bottom-4 right-4 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-colors {buttonClass}"
		onclick={() => (isOpen = true)}
		aria-label={ariaLabel}
	>
		<div class={iconClass}>
			{@html icon}
		</div>
	</button>
{/if}

<style>
	div :global(svg) {
		width: 100%;
		height: 100%;
	}
</style>
