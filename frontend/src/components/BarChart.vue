<template>
  <div>
    <canvas ref="barChartCanvas"></canvas>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';

// Register the necessary chart.js components
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);


import ForecastService from '../../services/getForecast.js'


export default {
  emits: ['chart-loaded'],
  setup(props, { emit }) {
    const barChartCanvas = ref(null);

    const fetchData = async () => {

      try {

        const response = await ForecastService.getSBCategory()
        const JSONdata = response.data.body
        console.log(JSONdata)

        const labels = Object.keys(JSONdata);
        const relativeForecast = labels.map(name => JSONdata[name].forecast_relative_to_trend);
        const percIncrease = labels.map(name => JSONdata[name].perc_increase);
        const forecastValues = labels.map(name => JSONdata[name].forecast_value);
        const finalScores = labels.map(name => JSONdata[name].final_score);

        const data = {
          labels: labels,
          datasets: [
            {
              label: 'Forecasted demand',
              data: forecastValues,
              backgroundColor: 'rgba(54, 162, 235, 0.5)',
              borderColor: 'rgba(54, 162, 235, 0.8)',
              borderWidth: 1
            },
            {
              label: 'Final score',
              data: finalScores,
              backgroundColor: 'rgba(255, 206, 86, 0.5)',
              borderColor: 'rgba(255, 206, 86, 0.8)',
              borderWidth: 1
            }
          ]
        };

        const options = {
          responsive: true,
          plugins: {
            legend: {
              position: 'top'
            }
          }
        };

        // Initialize the chart
        if (barChartCanvas.value) {
          const ctx = barChartCanvas.value.getContext('2d');
          new Chart(ctx, {
            type: 'bar',
            data: data,
            options: options
          });
          emit('chart-loaded');
        }

      } catch (error) {
        console.error('Error fetching data:', error);
      }
      
    };

    onMounted(fetchData);

    return {
      barChartCanvas
    };
  }
}

;
</script>

<style scoped>
canvas {
  height: 400px;
}
</style>
