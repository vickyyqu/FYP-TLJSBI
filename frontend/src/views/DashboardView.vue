<template>
  <div class="page-container">
    <div v-if="!isDataFilled" class="loading-screen">
      Loading Product Dashboard....
    </div>

    <div class="dashboard">
      <aside class="sidebar">
        <h1 class="product-title">{{ product }}</h1>
        <h4 class="product-subtitle">Category: {{ category }}</h4>
        <div class="latest-price">
          <p>Lowest price:
            <span class="latest-price-text"> ${{ latestPrice }} </span>
          </p>
        </div>
        <div class="platforms">
          <h4 class="platforms-title">Platforms with this product</h4>
          <ul class="platforms-list">
            <li v-for="(details, platform) in platformPriceMap" :key="platform" class="platform-item">
              {{ platform }}:
              <span style="font-weight: bold;">${{ details.price }}</span>
            </li>
          </ul>
        </div>
      </aside>

      <section class="main-content">
        <div class="price-container">
          <div v-if="chartLoaded" class="chart-description">
            <h3>Historical Price Data</h3>
            <p>
              Displays the scraped prices for this product model from the
              respective platforms to date.
            </p>
          </div>
          <PriceChart :priceData="historicData" />
        </div>
      </section>
      <div class="chart-container">
        <div v-if="chartLoaded" class="chart-description">
          <h3>Demand forecast</h3>
          <p>Displays the forecasted search count for this product weekly.</p>
        </div>
        <ProductLinechart :data="fetchedData" :avlb="categoryAvailability" @chart-loaded="chartLoaded = true" />
      </div>
      <div class="chart-container">
        <div v-if="chartLoaded" class="chart-description">
          <h3>Rank forecast</h3>
          <p>
            Displays the ranking of the product weekly, comparing how it is
            forecasted to perform against the other product categories.
          </p>
        </div>
        <MonthlyMixedchart :data="fetchedData" :avlb="categoryAvailability" @chart-loaded="chartLoaded = true" />
        <div v-if="chartLoaded" class="chart-description">
          <br />
          <h4>
            <span>Rank:</span> Calculated using the historical rank positions of
            products for each month using Google Trends data, then forecasting
            these averages on a weekly basis for the next year.
          </h4>
          <h4>
            <span>Trend:</span> General linear trend of the product's ranking
            over the months.
          </h4>
        </div>
      </div>
      <div class="chart-container">
        <div v-if="chartLoaded" class="chart-description">
          <h3>Seasonality impact forecast</h3>
          <p>
            Displays how the seasonality factor is forecasted to impact the
            demand of this product weekly.
          </p>
        </div>
        <WeeklyMixedchart :data="fetchedData" :avlb="categoryAvailability" @chart-loaded="chartLoaded = true" />
        <div v-if="chartLoaded" class="chart-description">
          <br />
          <h4>
            <span>Business Standing:</span> Adjustments made to account for
            specific times when more or less business is expected, like during
            sales or off-peak periods.
          </h4>
          <h4>
            <span>Additional Regressors:</span> The impact of additional
            factors that can influence TLJ's sales, such as marketing campaigns
            or changes in market conditions.
          </h4>
          <h4>
            <span>Seasonality Impact</span> The regular ups and downs observed throughout
            the year due to seasonal changes.
          </h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProductLinechart from "../components/dashboard/demand/ProductLinechart.vue";
import MonthlyMixedchart from "../components/dashboard/demand/MonthlyMixedchart.vue";
import WeeklyMixedchart from "../components/dashboard/demand/WeeklyMixedchart.vue";
import PriceChart from '../components/dashboard/price/PriceChart.vue';
import ForecastService from '../../services/getForecast.js';
import { toRaw } from 'vue';
import axios from "axios";

export default {
  components: {
    ProductLinechart,
    MonthlyMixedchart,
    WeeklyMixedchart,
    PriceChart,
  },

  props: [
    'brand',
    'model',
    'platform',
    'price',
    'dateCollected',
    'category',
    'discountPercentage',
    'discountedPrice',
    'modelNumber',
    'product'
  ],

  data() {
    return {
      fetchedData: null,
      historicData: null,
      resultCategory: null,
      categoryAvailability: null,
      uniquePlatforms: [],
      chartLoaded: false,
      platformPriceMap: null,
      latestPrice: null
    };
  },

  computed: {
    isDataFilled() {
      return (
        this.fetchedData !== null &&
        this.historicData !== null &&
        this.resultCategory !== null &&
        this.categoryAvailability !== null &&
        this.platformPriceMap !== null &&
        this.latestPrice !== null
      );
    }
  },

  async mounted() {
    await this.processCategory(this.category);
    await this.populateFetchData();
    await this.populateHistoricalPriceData();
  },

  methods: {
    async processCategory(category) {
      const availableCategories = [
        "air_con",
        "air_fryer",
        "air_purifier",
        "coffee_machine",
        "dryer",
        "fans",
        "fridge",
        "gas_cooker",
        "hood",
        "induction_cooker",
        "oven",
        "smart_lock",
        "tv",
        "vacuum",
        "washing_machine",
        "water_purifier",
      ];

      try {
        let processedCategory = await category.toLowerCase();
        processedCategory = processedCategory.replace(/\s+/g, '_');

        const categoryMappings = {
          'fan': 'fans',
          'air_conditioner': 'air_con',
          'vacuum_cleaner': 'vacuum',
          'gas_hob': 'gas_cooker',
          'induction_hob': 'induction_cooker',
          'airfryer': 'air_fryer',
          'washing_machine_/_dryer': 'washing_machine'
        };

        if (categoryMappings[processedCategory]) {
          processedCategory = categoryMappings[processedCategory];
        }

        this.resultCategory = availableCategories.includes(processedCategory) ? processedCategory : 'Not Available';
        this.categoryAvailability = this.resultCategory !== 'Not Available';

      } catch (error) {
        console.error('Error processing category:', error);
      }
    },

    async populateFetchData() {
      try {
        const response = await ForecastService.getCategoryDemand();
        const results = toRaw(response.data.body[this.resultCategory]);
        results.shift(); // remove header
        this.fetchedData = toRaw(results);

      } catch (error) {
        this.fetchedData = [];
        console.error('Error fetching forecast data:', error);
      }
    },

    async populateHistoricalPriceData() {
      try {
        const api_url = `https://ir39pxdck8.execute-api.us-east-1.amazonaws.com/exposeAPI/getProductHistory?productKey=${this.product}`;
        const response = await axios.get(api_url);
        const results = response.data;
        console.log(response)

        const groupedData = results.reduce((acc, entry) => {
          const platform = entry.platform?.S;
          if (!acc[platform]) {
            acc[platform] = [];
          }
          acc[platform].push(entry);
          return acc;
        }, {});

        this.historicData = groupedData;

        this.populatePlatformPriceMap(results);

      } catch (error) {
        console.error('Error fetching historical price data:', error);
      }
    },

    populatePlatformPriceMap(data) {
      this.platformPriceMap = {};

      data.forEach(entry => {
        const platform = entry.platform?.S;
        const price = parseFloat(entry.discountedPrice?.N).toFixed(2);
        const dateCollected = entry.dateCollected?.S;

        if (!this.platformPriceMap[platform] || new Date(dateCollected) > new Date(this.platformPriceMap[platform].dateCollected)) {
          this.platformPriceMap[platform] = {
            price,
            dateCollected
          };
        }
      });

      // Find the lowest price among the latest prices
      let lowestLatestPrice = Number.MAX_VALUE;

      for (const platform in this.platformPriceMap) {
        const price = parseFloat(this.platformPriceMap[platform].price);

        if (price < lowestLatestPrice) {
          lowestLatestPrice = price.toFixed(2);
        }
      }

      this.latestPrice = lowestLatestPrice;
    },



  },
}
</script>


<style scoped>
/* ... (no changes here) ... */
</style>


<style scoped>
.page-container {
  position: relative;
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  /* Creates two columns of equal width */
  gap: 20px;
  /* Adds space between the grid items */
  margin-top: 160px;
  width: 100%;
}

.button-container {
  position: relative;
  text-align: left;
  padding-left: 20px;
  margin-top: 200px;
}

.back-button {
  position: absolute;
  /* Absolute position within the .button-container */
  top: -40px;
  /* Adjust this value to place the button right below the navbar */
  left: 0;
  background-color: #f9f9f9;
  /* Or any color you prefer */
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.sidebar {
  padding: 20px;
  /* Add padding to the sidebar */
}

.product-title {
  font-weight: bold;
}

.product-title,
.product-subtitle,
.platforms-title {
  text-align: left;
  margin: 0;
  padding-bottom: 10px;
  /* Add padding under the headings */
}

.latest-price p {
  margin-top: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ccc;
  font-size: 1.5rem;
  color: rgb(82, 82, 82);
}

.latest-price-text {
  color: rgb(27, 101, 27);
  font-weight: bold;
}

.platforms {
  margin-top: 30px;
}

.platforms-list {
  list-style: none;
  /* Remove default list styling */
  padding: 0;
  margin: 0;
}

.platform-item {
  background: #f9f9f9;
  margin-bottom: 10px;
  /* Add space between items */
  padding: 10px 15px;
  width: 50%;
  border-radius: 10px;
  /* Rounded corners for items */
  text-align: left;
  /* Align text to the left */
}

.main-content {
  flex: 1;
  /* Takes the remaining space */
  padding: 1rem;
}

.chart-description {
  text-align: center;
  max-width: 85%;
  margin: auto;
  font-size: 14px;
}

.chart-description h3 {
  font-weight: bold;
  font-size: 17px;
}

.chart-description h4 {
  font-size: 12px;
}

.chart-description h4 span {
  font-weight: bold;
}

.chart-container:nth-child(3) {
  grid-column: 1 / -1;
  /* Span across all available columns */
  width: 100%;
  /* Ensure it takes up the full width */
  margin-bottom: 40px;
}

.chart-container:nth-last-child(1),
.chart-container:nth-last-child(2) {
  grid-column: span 1;
  /* Each takes up one column */
  width: 100%;
  /* Ensure it takes up the full width of its column */
}

.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.7);
  /* Semi-transparent white background */
  z-index: 9999;
  /* Ensure it's on top of everything */
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.7);
  /* Semi-transparent white background */
  z-index: 9999;
  /* Ensure it's on top of everything */
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
