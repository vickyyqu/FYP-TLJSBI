<template>
  <div>
    <h1>StarBuy Page</h1>
    <p>This is the StarBuy page content.</p>
    <BarChart title="Bar Chart" 
    xKey="name" 
    yKey="amount" 
    :data="barChartData" />

  </div>
</template>
  
<script>
import BarChart from "../components/BarChart.vue";

export default {
  components: {
    BarChart,
},
  data() {
    return {
      barChartData: [],
    };
  },
  mounted() {
    this.fetchCSVData();
  },
  methods: {
    async fetchCSVData() {
      try {
        const response = await fetch('../../public/BarChartMockData.csv'); // Fetch the CSV file
        const data = await response.text(); // Read the response as text
        console.log(data)
        console.log("data fetched successfully")


        // Parse the CSV data
        const parsedData = this.parseCSVData(data);
        // Set the parsed data to the barChartData array
        this.barChartData = parsedData;
        console.log(parsedData)
        console.log("data parsed successfully")

      } catch (error) {
        console.error('Error fetching CSV data:', error);
      }
    },

    parseCSVData(csvData) {
      // Split the CSV data by newline characters to get rows
      const rows = csvData.trim().split('\n');
      // Extract the header row to get column names
      const headers = rows.shift().split(',');
      // Parse each row into an object
      const parsedData = rows.map(row => {
        const values = row.split(',');
        return headers.reduce((obj, header, index) => {
          obj[header.trim()] = values[index].trim();
          return obj;
        }, {});
      });
      return parsedData;
    },
    
  },
};
</script>
  

<!-- 
    data: () => ({
    barChartData: [
      {
        name: "Roses",
        amount: 25
      },
      {
        name: "Tulips",
        amount: 40
      },
      {
        name: "Daisies",
        amount: 15
      },
      {
        name: "Narcissuses",
        amount: 9
      }
    ]
  })
 -->