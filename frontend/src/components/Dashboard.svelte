<script lang="ts">
	import { onMount } from 'svelte'
	import { apiPost, apiGet } from '../utils/api'

	type Props = {
		username: string
		onLogout: () => void
	}

	type DashboardData = {
		message?: string
		devices?: string[]
	}

	let { username, onLogout }: Props = $props()

	let loading = $state(false)
	let dashboardData = $state<DashboardData>({})
	let fetchError = $state<string | null>(null)

	async function fetchDashboardData() {
		try {
			const data = await apiGet<DashboardData>('/dashboard/', {
				handleLogout: onLogout,
			})
			dashboardData = data
			fetchError = null
		} catch (err) {
			console.error('Failed to fetch dashboard data:', err)
			fetchError = err instanceof Error ? err.message : 'Failed to load dashboard data'
		}
	}

	async function handleLogout() {
		loading = true
		try {
			await apiPost('/auth/logout')
			onLogout()
		} catch (err) {
			console.error('Logout failed:', err)
			// Still call onLogout to clear the UI state
			onLogout()
		} finally {
			loading = false
		}
	}

	onMount(() => {
		fetchDashboardData()
	})
</script>

<div class="w-full max-w-4xl mx-auto p-6">
	<div class="bg-white rounded-lg shadow-md p-6">
		<div class="flex items-center justify-between mb-6">
			<div>
				<h1 class="text-3xl font-bold">Dashboard</h1>
				<p class="text-gray-600 mt-2">Welcome, {username}</p>
			</div>
			<button
				onclick={handleLogout}
				disabled={loading}
				class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
			>
				{loading ? 'Logging out...' : 'Logout'}
			</button>
		</div>

		<div class="border-t pt-6">
			<h2 class="text-xl font-semibold mb-4">IoT Dashboard</h2>
			{#if fetchError}
				<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
					{fetchError}
				</div>
			{:else if dashboardData.message}
				<p class="text-gray-600">{dashboardData.message}</p>
			{:else}
				<p class="text-gray-600">Dashboard content will appear here.</p>
			{/if}
		</div>
	</div>
</div>
