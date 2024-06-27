<template>
  <div class="chart-container">
    <canvas ref="lineChartRef"></canvas>
  </div>
</template>

<script>
import { ref, watch, toRaw } from 'vue';
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, TimeScale, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { parseISO } from 'date-fns';

export default {
  props: {
    priceData: {
      type: null,
      required: true
    }
  },
  emits: ['chart-loaded'],

  setup(props, context) {

    Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, TimeScale, Tooltip, Legend);
    const lineChartRef = ref(null);

    // Define colors for the datasets
    const colors = [
      'rgba(54, 162, 235, 0.2)',
      'rgba(255, 99, 132, 0.2)',
      'rgba(255, 206, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(255, 159, 64, 0.2)'
    ];
    const borderColors = [
      'rgba(54, 162, 235, 1)',
      'rgba(255, 99, 132, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)'
    ];

    watch(() => props.priceData, async () => {
  try {
    console.log(props.priceData);
    
    const datasets = [];
    let widestRangeLabels = [];  // Labels from the platform with the widest date range
    let i = 0;
    let widestRange = 0;

    for (let platform in props.priceData) {
      const results = await toRaw(props.priceData[platform]);
      const dataWithDates = results.map(entry => ({
        x: entry['dateCollected']['S'] ? parseISO(entry['dateCollected']['S']) : null,
        y: entry['discountedPrice']['N'] ? parseFloat(entry['discountedPrice']['N']) : null
      })).filter(entry => entry.x && entry.y);

      const labels = dataWithDates.map(entry => entry.x).filter(Boolean);
      const data = dataWithDates.map(entry => entry.y).filter(Boolean);

      // Determine the widest date range
      if (labels.length > widestRange) {
        widestRange = labels.length;
        widestRangeLabels = labels.map(date => date.toISOString().split('T')[0]); // Convert to ISO string format
      }

      datasets.push({
        type: 'line',
        label: platform,
        data: dataWithDates,
        backgroundColor: colors[i % colors.length],
        borderColor: borderColors[i % borderColors.length],
        borderWidth: 1
      });

      i++;
    }

    if (datasets.length) {
      const lineChartData = {
        labels: widestRangeLabels,
        datasets
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
              title: {
                display: true,
                text: 'Price ($)'
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
      context.emit('chart-loaded');
    } else {
      throw new Error('Incomplete data for chart');
    }
    console.log("price chart LOADED (top right chart)");
  }
  catch (error) {
    console.error('There was a problem fetching the data:', error);
  }
});

return {
  lineChartRef
};


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
