<template>
  <div class="page-container">
    <h3>RSI and CPI trends</h3>
    <p>The Retail Sales Index (RSI) chart measures consumer spending on retail goods for each month. The Consumer Price
      Index (CPI) chart measures the changes in prices paid by consumers on household appliances for each month. Both
      charts are plotted using historical and forecasted values.</p>

    <!-- CPI chart -->
    <div class="chart-container">
      <LineChart :var="'CPI'" />
    </div>
    
    <!-- RSI chart -->
    <div class="chart-container">
      <LineChart :var="'RSI'" />
    </div>


  </div>
</template>

<script>
import LineChart from "../components/LineChart.vue";

export default {
  components: {
    LineChart
  }
}
</script>


<style scoped>
.page-container {
  display: grid;
  grid-column: 1 / -1;
  /* ensures the chart spans across the two card columns */
  grid-gap: 20px;
  /* space between columns */
  margin-top: 200px;
}

.page-container h3 {
  font-weight: bold;
  text-align: center;
}

.page-container p {
  text-align: center;
}

.cards-container {
  margin-top: 250px;
  /* Adjust based on your navbar height */
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  /* also defines two columns for the cards */
  gap: 50px;
  /* Adjust the gap between cards as needed */
  width: 100%
}

.chart-container {
  grid-column: 1 / -1;
  /* ensures the chart spans across the two card columns */
  padding: 20px;
  width: calc(100% + 40px);
  /* accounts for the padding and gap */
  margin-left: -20px;
  /* aligns the left edge with the cards */
  margin-right: -20px;
  /* aligns the right edge with the cards */
}
</style>