export type FetchOptions = RequestInit & {
	handleLogout?: () => void
}

/**
 * A reusable fetch wrapper that handles authentication failures.
 * If a 401 or 403 response is received and a handleLogout callback is provided,
 * it will be invoked before throwing the error.
 */
export async function apiFetch(url: string, options: FetchOptions = {}): Promise<Response> {
	const { handleLogout, ...fetchOptions } = options

	try {
		const response = await fetch(url, fetchOptions)

		// Handle authentication failures
		if (response.status === 401 || response.status === 403) {
			if (handleLogout) {
				handleLogout()
			}
		}

		return response
	} catch (error) {
		// Re-throw network errors and other exceptions
		throw error
	}
}

/**
 * Convenience method for GET requests with JSON response
 */
export async function apiGet<T>(url: string, options: FetchOptions = {}): Promise<T> {
	const response = await apiFetch(url, {
		...options,
		method: 'GET',
	})

	if (!response.ok) {
		const errorText = await response.text()
		throw new Error(errorText || `Request failed: ${response.status} ${response.statusText}`)
	}

	return response.json()
}

/**
 * Convenience method for POST requests with JSON body
 */
export async function apiPost<T>(
	url: string,
	body: Record<string, unknown>,
	options: FetchOptions = {},
): Promise<T> {
	const response = await apiFetch(url, {
		...options,
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			...options.headers,
		},
		body: JSON.stringify(body),
	})

	if (!response.ok) {
		const errorText = await response.text()
		throw new Error(errorText || `Request failed: ${response.status} ${response.statusText}`)
	}

	return response.json()
}
