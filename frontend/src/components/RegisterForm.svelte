<script lang="ts">
	import { apiPost } from '../utils/api'

	type Props = {
		onRegisterSuccess: () => void
		onSwitchToLogin: () => void
	}

	let { onRegisterSuccess, onSwitchToLogin }: Props = $props()

	let email = $state('')
	let password = $state('')
	let confirmPassword = $state('')
	let error = $state('')
	let loading = $state(false)

	async function handleSubmit(e: Event) {
		e.preventDefault()
		loading = true
		error = ''

		if (password !== confirmPassword) {
			error = 'Passwords do not match'
			loading = false
			return
		}

		try {
			await apiPost('/auth/register', {
				email,
				password,
				confirm_password: confirmPassword,
			})
			onRegisterSuccess()
		} catch (err) {
			error = err instanceof Error ? err.message : 'Network error. Please try again.'
		} finally {
			loading = false
		}
	}
</script>

<div class="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
	<h2 class="text-2xl font-bold mb-6 text-center">Register</h2>

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

		<div class="mb-4">
			<label for="password" class="block text-sm font-medium mb-2">Password</label>
			<input
				type="password"
				id="password"
				bind:value={password}
				required
				minlength="8"
				maxlength="32"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
			/>
		</div>

		<div class="mb-6">
			<label for="confirmPassword" class="block text-sm font-medium mb-2">Confirm Password</label>
			<input
				type="password"
				id="confirmPassword"
				bind:value={confirmPassword}
				required
				minlength="8"
				maxlength="32"
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
			class="w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed mb-4"
		>
			{loading ? 'Registering...' : 'Register'}
		</button>
	</form>

	<div class="text-center">
		<button type="button" onclick={onSwitchToLogin} class="text-blue-600 hover:underline">
			Already have an account? Login
		</button>
	</div>
</div>
