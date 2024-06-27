<template>
  <div>
    <canvas ref="lineChartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {
  Chart,
  Filler,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import Papa from 'papaparse';
import { parseISO } from 'date-fns';


Chart.register(
  Filler,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  CategoryScale
);

import ForecastService from '../../services/getForecast.js';

const lineChartCanvas = ref(null);
const chart = ref(null); // Reference to the Chart instance
const data = ref({ labels: [], datasets: [] });

const contentToRetrieve = defineProps({
  var: {
    type: String,
    required: true
  }
}
);

onMounted(() => {
  fetchCsvData();
});


async function fetchCsvData() {
  let response;
  let csvText;

  // For RSI
  if (contentToRetrieve.var === 'RSI') {
    response = await ForecastService.getRSIForecast();
    csvText = response.data.body;
    csvText = csvText.map(entry => entry.slice(1));
    // remove first item (the header)
    console.log('header of', contentToRetrieve.var, csvText[0]) // header
    console.log('content', csvText) // content
  }

  // For CPI
  else if (contentToRetrieve.var === 'CPI') {
    response = await ForecastService.getCPIForecast();
    csvText = response.data.body;
    csvText = csvText.map(entry => entry.slice(1));
    // remove first item (the header)
    console.log('header of', contentToRetrieve.var, csvText[0]) // header
    console.log('content', csvText) // content
  }

  csvText.shift();
  processData(csvText)

}


async function processData(parsedData) {
  data.value.labels = parsedData.map(entry => parseISO(entry[0])); // date

  data.value.datasets = [
    {
      label: 'High Forecast',
      data: parsedData.map(entry => ({
        x: parseISO(entry[0]), // make sure to parse the date
        y: entry[3] // high forecast
      })),
      borderColor: 'rgba(75, 192, 192, 1)',
      fill: false,
      tension: 0.4
    },
    {
      label: 'Low Forecast',
      data: parsedData.map(entry => ({
        x: parseISO(entry[0]), // make sure to parse the date
        y: entry[2] // low forecast
      })),
      borderColor: 'rgba(255, 99, 132, 1)',
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      fill: '-1',
      tension: 0.4
    },
    {
      label: 'Forecasted Price',
      data: parsedData.map(entry => ({
        x: parseISO(entry[0]), // make sure to parse the date
        y: entry[1] // forecasted price
      })),
      borderColor: 'rgba(54, 162, 235, 1)',
      fill: false,
      pointRadius: 3,
      tension: 0.4
    }
  ];
  await initChart();
}

async function initChart() {
  if (lineChartCanvas.value && !chart.value) {
    const ctx = lineChartCanvas.value.getContext('2d');
    const titleText = contentToRetrieve.var === 'CPI' ? 'CPI of Household Appliance' : 'RSI of Household Appliance';
    const axisText = contentToRetrieve.var === 'CPI' ? 'CPI' : 'RSI';

    chart.value = new Chart(ctx, {
      type: 'line',
      data: data.value,
      options: {
        plugins: {
          title: {
            display: true,
            text: titleText,
          },
          legend: {
            display: true,
          },
          tooltip: {
            callbacks: {
              title: function (tooltipItems) {
                // Assuming the label is in the format "Jul 1, 2024, 12:00:00 AM"
                // You split by the comma and take the first part to exclude the time
                return tooltipItems[0].label.split(',').slice(0, 2).join(',');
              },
              label: function (context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  // Round the value to 2 decimal places
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
              unit: 'year', // might be 'month' or 'year', depending on your data
            },
            title: {
              display: true,
              text: 'Date',
            },
          },
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: axisText,
            },
          },
        },
        responsive: true,
        maintainAspectRatio: false,
      },
    });
  }
}
</script>

<style scoped>
canvas {
  height: 500px;
  width: 100%;
}
</style>