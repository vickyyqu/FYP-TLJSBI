<template>
  <div class="chart-container">
    <canvas v-show="isAvailable" ref="mixedChartRef"></canvas>
    <h1 v-show="!isAvailable">Forecasts for Category Unavailable</h1>
  </div>
</template>

<script>
import { ref, watch, toRaw } from 'vue';
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
    },
    avlb: {
      type: null,
      required: true
    }
  },

  emits: ['chart-loaded'],

  setup(props, context) {
    const mixedChartRef = ref(null);
    const isAvailable = ref(true);  // To check if data is available

    watch(() => props.avlb, async (newAvlb) => {
      isAvailable.value = newAvlb;
    });

    watch(() => props.data, async (newData) => {
      try {
        if (!isAvailable.value) return;  // Return if data is not available
        const results = await toRaw(newData);
        const currentDate = new Date();
        const twoWeeksAgo = subWeeks(currentDate, 2);
        const sixMonthsFromNow = addMonths(currentDate, 6);

        const filteredResults = results.filter(entry => {
          const date = parseISO(entry[0]);
          return date >= twoWeeksAgo && date <= sixMonthsFromNow;
        });

        const labels = filteredResults.map(entry => entry[0] ? parseISO(entry[0]) : null).filter(Boolean);
        const additiveData = filteredResults.map(entry => entry[6] ? parseFloat(entry[6]) : null).filter(Boolean);
        const regressorsData = filteredResults.map(entry => entry[9] ? parseFloat(entry[9]) : null).filter(Boolean);
        const yearlyData = filteredResults.map(entry => entry[15] ? parseFloat(entry[15]) : null).filter(Boolean);

        const mixedChartData = {
          labels: labels,
          datasets: [
            {
              type: 'line',
              label: 'Business Standing',
              data: additiveData,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            },
            {
              type: 'line',
              label: 'Additional Regressors',
              data: regressorsData,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1,
              yAxisID: 'y1'
            },
            {
              type: 'line',
              label: 'Seasonality Impact',
              data: yearlyData,
              backgroundColor: 'rgba(60, 179, 113, 0.2)',
              borderColor: 'rgba(60, 179, 113, 1)',
              borderWidth: 1,
              yAxisID: 'y2'
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
                  unit: 'week'
                },
                title: {
                  display: true,
                  text: 'Week of Year'
                }
              },
              y: {
                type: 'linear',
                position: 'left',
                title: {
                  display: true,
                  text: 'Additive Terms'
                }
              },
              y1: {
                type: 'linear',
                position: 'left',
                grid: {
                  drawOnChartArea: false
                },
                title: {
                  display: true,
                  text: 'Extra Regressors Additive'
                }
              },
              y2: {
                type: 'linear',
                position: 'right',
                grid: {
                  drawOnChartArea: false
                },
                title: {
                  display: true,
                  text: 'Yearly'
                }
              }
            },
            responsive: true,
            maintainAspectRatio: false,
          }
        });

        console.log("weekly mixed chart LOADED (middle left chart)");
        context.emit('chart-loaded')

      } catch (error) {
        console.error('There was a problem fetching the data:', error);
      }
    });

    return {
      mixedChartRef,
      isAvailable
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
