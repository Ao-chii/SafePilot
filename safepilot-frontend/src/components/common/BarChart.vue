<template>
  <div class="bar-chart-wrapper">
    <canvas ref="chartCanvas" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface BarChartData {
  label: string
  value: number
}

const props = defineProps<{
  data: BarChartData[]
  title?: string
  color?: string
  horizontal?: boolean
}>()

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chart: ChartJS | null = null

const createChart = () => {
  if (!chartCanvas.value || !props.data.length) return
  
  const color = props.color || '#A096A5'
  const chartType = props.horizontal ? 'bar' : 'bar'
  
  const chartData: ChartData<'bar'> = {
    labels: props.data.map(item => item.label),
    datasets: [{
      label: props.title || '数值',
      data: props.data.map(item => item.value),
      backgroundColor: color + '80',
      borderColor: color,
      borderWidth: 2,
      borderRadius: 6,
      borderSkipped: false,
      hoverBackgroundColor: color + 'A0',
      hoverBorderColor: color,
      hoverBorderWidth: 3
    }]
  }

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: props.horizontal ? 'y' : 'x',
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(37, 40, 65, 0.95)',
        titleColor: '#E7D1BB',
        bodyColor: '#E7D1BB',
        borderColor: '#E7D1BB',
        borderWidth: 1,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
        padding: 12,
        cornerRadius: 8,
        displayColors: false
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(160, 150, 165, 0.15)',
          drawOnChartArea: true
        },
        ticks: {
          color: '#A096A5',
          font: {
            size: 11
          }
        },
        border: {
          color: 'rgba(231, 209, 187, 0.3)'
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(160, 150, 165, 0.15)',
          drawOnChartArea: true
        },
        ticks: {
          color: '#A096A5',
          font: {
            size: 11
          }
        },
        border: {
          color: 'rgba(231, 209, 187, 0.3)'
        }
      }
    },
    animation: {
      duration: 1200,
      easing: 'easeOutQuart'
    }
  }

  chart = new ChartJS(chartCanvas.value, {
    type: chartType,
    data: chartData,
    options
  })
}

const updateChart = () => {
  if (!chart) return
  
  chart.data.labels = props.data.map(item => item.label)
  chart.data.datasets[0].data = props.data.map(item => item.value)
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
.bar-chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>