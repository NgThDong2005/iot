<script lang="ts">
	import LineChart from './LineChart.svelte'

	type Props = {
		tempData: number[]
		gasData: number[]
		timeData: string[]
	}

	let { tempData, gasData, timeData }: Props = $props()

	let activeTab: 'temp' | 'gas' | 'all' = $state('all')
</script>

<div class="w-full flex flex-col gap-4">
	<h2 class="text-xl font-semibold">Data Sensor History (Latest 20 Entries)</h2>
	<!-- Tabs -->
	<div class="flex gap-4 mb-4">
		<button
			class="px-4 py-2 rounded-t-lg border-b-2"
			class:border-blue-500={activeTab === 'all'}
			class:border-gray-200={activeTab !== 'all'}
			onclick={() => (activeTab = 'all')}
		>
			All
		</button>
		<button
			class="px-4 py-2 rounded-t-lg border-b-2"
			class:border-blue-500={activeTab === 'temp'}
			class:border-gray-200={activeTab !== 'temp'}
			onclick={() => (activeTab = 'temp')}
		>
			Temperature
		</button>
		<button
			class="px-4 py-2 rounded-t-lg border-b-2"
			class:border-blue-500={activeTab === 'gas'}
			class:border-gray-200={activeTab !== 'gas'}
			onclick={() => (activeTab = 'gas')}
		>
			Gas
		</button>
	</div>
	<div class="w-full mx-auto">
		<LineChart
			series={[
				...(activeTab !== 'gas'
					? [{ data: tempData, label: 'Temperature', color: '#ef4444' }]
					: []),
				...(activeTab !== 'temp' ? [{ data: gasData, label: 'Gas', color: '#3b82f6' }] : []),
			]}
			time={timeData}
		/>
	</div>
</div>
