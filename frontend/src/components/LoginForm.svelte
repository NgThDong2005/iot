<script lang="ts">
	import { apiPost } from '../utils/api'

	type Props = {
		onLoginSuccess: () => void
		onSwitchToRegister: () => void
	}

	let { onLoginSuccess, onSwitchToRegister }: Props = $props()

	let email = $state('')
	let password = $state('')
	let error = $state('')
	let loading = $state(false)

	async function handleSubmit(e: Event) {
		e.preventDefault()
		loading = true
		error = ''

		try {
			await apiPost('/auth/login', { email, password })
			onLoginSuccess()
		} catch (err) {
			error = err instanceof Error ? err.message : 'Network error. Please try again.'
		} finally {
			loading = false
		}
	}
</script>

<div class="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
	<h2 class="text-2xl font-bold mb-6 text-center">Login</h2>

	<form onsubmit={handleSubmit}>
		<div class="mb-4">
			<label for="email" class="block text-sm font-medium mb-2">Email</label>
			<input
				type="email"
				id="email"
				bind:value={email}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
			/>
		</div>

		<div class="mb-6">
			<label for="password" class="block text-sm font-medium mb-2">Password</label>
			<input
				type="password"
				id="password"
				bind:value={password}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
			/>
		</div>

		{#if error}
			<div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
				{error}
			</div>
		{/if}

		<button
			type="submit"
			disabled={loading}
			class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed mb-4"
		>
			{loading ? 'Logging in...' : 'Login'}
		</button>
	</form>

	<div class="text-center">
		<button type="button" onclick={onSwitchToRegister} class="text-blue-600 hover:underline">
			Don't have an account? Register
		</button>
	</div>
</div>
