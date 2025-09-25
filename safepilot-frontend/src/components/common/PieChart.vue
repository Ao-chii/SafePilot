<template>
  <div class="pie-chart-wrapper">
    <canvas ref="chartCanvas" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

interface PieChartData {
  type: string
  count: number
  percentage: number
}

const props = defineProps<{
  data: PieChartData[]
  colors?: string[]
}>()

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chart: ChartJS | null = null

const defaultColors = [
  '#E7D1BB',
  '#c8b39e', 
  '#A096A5',
  '#84725e',
  '#463e4b',
  '#6EE7B7',
  '#FDE68A',
  '#FCA5A5',
  '#93C5FD'
]

const createChart = () => {
  if (!chartCanvas.value || !props.data.length) return
  
  const colors = props.colors || defaultColors
  
  const chartData: ChartData<'pie'> = {
    labels: props.data.map(item => item.type),
    datasets: [{
      data: props.data.map(item => item.count),
      backgroundColor: colors.slice(0, props.data.length),
      borderColor: colors.slice(0, props.data.length).map(color => color + '80'),
      borderWidth: 2,
      hoverBorderWidth: 3,
      hoverOffset: 10
    }]
  }

  const options: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
          color: '#E7D1BB',
          font: {
            size: 12,
            family: 'system-ui'
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(37, 40, 65, 0.95)',
        titleColor: '#E7D1BB',
        bodyColor: '#E7D1BB',
        borderColor: '#E7D1BB',
        borderWidth: 1,
        callbacks: {
          label: (context) => {
            const item = props.data[context.dataIndex]
            return `${item.type}: ${item.count} (${item.percentage}%)`
          }
        }
      }
    },
    animation: {
      animateRotate: true,
      animateScale: true,
      duration: 1000
    }
  }

  chart = new ChartJS(chartCanvas.value, {
    type: 'pie',
    data: chartData,
    options
  })
}

const updateChart = () => {
  if (!chart) return
  
  const colors = props.colors || defaultColors
  chart.data.labels = props.data.map(item => item.type)
  chart.data.datasets[0].data = props.data.map(item => item.count)
  chart.data.datasets[0].backgroundColor = colors.slice(0, props.data.length)
  chart.update()
}

watch(() => props.data, () => {
  if (chart) {
    updateChart()
  } else {
    createChart()
  }
}, { deep: true })

onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chart) {
    chart.destroy()
  }
})
</script>

<style scoped>
.pie-chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>