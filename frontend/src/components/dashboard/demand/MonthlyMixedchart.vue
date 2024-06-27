<template>
  <div class="chart-container">
    <canvas ref="mixedChartRef" v-if="data"></canvas>
  </div>
</template>

<script>
import { ref, watch, toRaw, onMounted } from 'vue';
import {
  Chart,
  BarController,
  BarElement,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  TimeScale,
  Tooltip,
  Legend
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { parseISO, addWeeks, addMonths, subWeeks } from 'date-fns';

Chart.register(
  BarController,
  BarElement,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  TimeScale,
  Tooltip,
  Legend
);

export default {
  props: {
    data: {
      type: null,
      required: true
    }
  },

  emits: ['chart-loaded'],

  setup(props, context) {
    const mixedChartRef = ref(null);

    watch(() => props.data, async (newData) => {
      if (newData.length === 0) {
        console.log("Chart unavailable");
        return;  // Abort the function if newData is empty
      }

      try {
        console.log(newData.length === 0)
        const results = await toRaw(newData);
        const currentDate = new Date();
        const twoWeeksAgo = subWeeks(currentDate, 2);
        const sixMonthsFromNow = addMonths(currentDate, 6);

        const filteredResults = results.filter(entry => {
          const date = parseISO(entry[0]);
          return date >= twoWeeksAgo && date <= sixMonthsFromNow;
        });

        const labels = filteredResults.map(entry => entry[0] ? parseISO(entry[0]) : null).filter(Boolean); // ds
        const barData = filteredResults.map(entry => entry[12] ? parseFloat(entry[12]) : null).filter(Boolean); // rank
        const lineData = filteredResults.map(entry => entry[1] ? parseFloat(entry[1]) : null).filter(Boolean); // trend

        const mixedChartData = {
          labels: labels,
          datasets: [
            {
              type: 'bar',
              label: 'Rank',
              data: barData,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            },
            {
              type: 'line',
              label: 'Trend',
              data: lineData,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1,
              yAxisID: 'y1'
            }
          ]
        };

        const ctx = mixedChartRef.value.getContext('2d');
        new Chart(ctx, {
          data: mixedChartData,
          options: {
            plugins: {
              tooltip: {
                callbacks: {
                  title: function (tooltipItems) {
                    return tooltipItems[0].label.split(',').slice(0, 2).join(',');
                  },
                  label: function (context) {
                    let label = context.dataset.label || '';
                    if (label) {
                      label += ': ';
                    }
                    if (context.parsed.y !== null) {
                      label += context.parsed.y.toFixed(2);
                    }
                    return label;
                  }
                }
              }
            },
            scales: {
              x: {
                type: 'time',
                time: {
                  unit: 'month'
                },
                title: {
                  display: true,
                  text: 'Month of Year'
                }
              },
              y: {
                type: 'linear',
                position: 'left',
                title: {
                  display: true,
                  text: 'Rank'
                }
              },
              y1: {
                type: 'linear',
                position: 'right',
                grid: {
                  drawOnChartArea: false
                },
                title: {
                  display: true,
                  text: 'Trend'
                }
              }
            },
            responsive: true,
            maintainAspectRatio: false,
          }
        });
        console.log("monthly mixed chart LOADED (middle right chart)");
        context.emit('chart-loaded')
        
      } catch (error) {
        console.error('There was a problem fetching the data:', error);
      }
    });

    return {
      mixedChartRef
    };
  }
}
</script>

<style scoped>
.chart-container {
  height: 400px;
  width: 100%;
}
</style>
