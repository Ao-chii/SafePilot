<template>
  <div class="line-chart-wrapper">
    <canvas ref="chartCanvas" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartData,
  type ChartOptions
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface LineChartData {
  date: string
  count: number
}

const props = defineProps<{
  data: LineChartData[]
  label?: string
  color?: string
}>()

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chart: ChartJS | null = null

const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const createChart = () => {
  if (!chartCanvas.value || !props.data.length) return
  
  const color = props.color || '#6EE7B7'
  const label = props.label || '事件数量'
  
  const chartData: ChartData<'line'> = {
    labels: props.data.map(item => formatDate(item.date)),
    datasets: [{
      label,
      data: props.data.map(item => item.count),
      borderColor: color,
      backgroundColor: color + '20',
      fill: true,
      tension: 0.4,
      borderWidth: 3,
      pointBackgroundColor: color,
      pointBorderColor: '#E7D1BB',
      pointBorderWidth: 2,
      pointRadius: 6,
      pointHoverRadius: 8,
      pointHoverBackgroundColor: color,
      pointHoverBorderColor: '#E7D1BB',
      pointHoverBorderWidth: 3
    }]
  }

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index'
    },
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
      duration: 1500,
      easing: 'easeInOutQuart'
    }
  }

  chart = new ChartJS(chartCanvas.value, {
    type: 'line',
    data: chartData,
    options
  })
}

const updateChart = () => {
  if (!chart) return
  
  chart.data.labels = props.data.map(item => formatDate(item.date))
  chart.data.datasets[0].data = props.data.map(item => item.count)
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
.line-chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}
</style>