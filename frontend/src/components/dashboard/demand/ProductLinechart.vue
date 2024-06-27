<template>
  <div class="chart-container">
    <canvas ref="lineChartRef"></canvas>
  </div>
</template>

<script>
import { ref, watch, toRaw, onMounted } from 'vue';
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, TimeScale, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { parseISO, addWeeks, addMonths, subWeeks } from 'date-fns';

export default {
  props: {
    data: {
      type: null,
      required: true
    }
  },
  emits: ['chart-loaded'],


  setup(props, context) {
  
    Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, TimeScale, Tooltip, Legend);
    const lineChartRef = ref(null);

    watch(() => props.data, async (newData) => {
      if (newData.length === 0) {
        console.log("Chart unavailable");
        return;  // Abort the function if newData is empty
      }
      
      try {
        const results = await toRaw(newData);
        const currentDate = new Date();
        const twoWeeksAgo = subWeeks(currentDate, 2);
        const sixMonthsFromNow = addMonths(currentDate, 6);

        const filteredResults = results.filter(entry => {
          const date = parseISO(entry[0]);
          return date >= twoWeeksAgo && date <= sixMonthsFromNow;
        });

        const labels = filteredResults.map(entry => entry[0] ? parseISO(entry[0]) : null).filter(Boolean);
        const data = filteredResults.map(entry => entry[21] ? parseFloat(entry[21]) : null).filter(Boolean);

        if (labels.length && data.length) {
          const lineChartData = {
            labels,
            datasets: [{
              label: 'Forecasted demand vs. Date',
              data,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          };

          const ctx = lineChartRef.value.getContext('2d');
          new Chart(ctx, {
            type: 'line',
            data: lineChartData,
            options: {
              scales: {
                x: {
                  type: 'time',
                  time: {
                    parser: 'yyyy-MM-dd',
                    unit: 'week',
                    displayFormats: {
                      month: 'MMM yyyy'
                    }
                  },
                  title: {
                    display: true,
                    text: 'Week of Year'
                  },
                  ticks: {
                    source: 'auto',
                    autoSkip: true,
                    maxTicksLimit: 20
                  }
                },
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Forecast Demand'
                  }
                }
              },
              plugins: {
                legend: {
                  display: true
                },
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
              responsive: true,
              maintainAspectRatio: false,
            }
          });
          context.emit('chart-loaded')
        } else {
          throw new Error('Incomplete data for chart');
        }
        console.log("product line chart LOADED (bottom chart)");
      }
      catch (error) {
        console.error('There was a problem fetching the data:', error);
      }
    });

    return {
      lineChartRef
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
