<template>
  <div class="page-container">
    <div class="homecard-container">

      <div class="left">
        <h3 class="card-title"> This Week's Star Buy <i class="bi bi-star-fill"></i></h3>
        <div class="scrollable">
          <!-- This Week's Star Buy HomeCard (top)-->
          <div class="homecard-component" v-for="item in currentTop" :key="item" @click="handleCardClick(item)">
            <div class="homecard">
              <p class="card-product">
                <strong>{{ item.itemName }}</strong>
                ({{ item.starBuyType }})
              </p>
              <p class="card-price">Recommended Price:
                <strong>
                  ${{ item.recPrice.toFixed(2) }}
                </strong>
              </p>
            </div>
          </div>

          <!-- This Week's Star Buy HomeCard (rising)-->
          <div class="homecard-component" v-for="item in currentRising" :key="item" @click="handleCardClick(item)">
            <div class="homecard">
              <p class="card-product">
                <strong>{{ item.itemName }}</strong>
                ({{ item.starBuyType }})
              </p>
              <p class="card-price">Recommended Price:
                <strong>
                  ${{ item.recPrice.toFixed(2) }}
                </strong>
              </p>
            </div>
          </div>
        </div>
        <p style="text-align: right" v-if="currentTop.length + currentRising.length > 2">
          Scroll for more <i class="bi bi-chevron-down"></i>
        </p>
      </div>


      <div class="right">
        <h3 class="card-title"> Next Week's Star Buy <i class="bi bi-graph-up"></i></h3>
        <div class="scrollable">
          <!-- Next Week's Star Buy (top) -->
          <div class="homecard-component" v-for="item in nextTop" :key="item" @click="handleCardClick(item)">
            <div class="homecard">
              <p class="card-product">
              <p class="card-product">
                <strong>{{ item.itemName }}</strong>
                ({{ item.starBuyType }})
              </p>
              </p>
              <p class="card-price">Recommended Price:
                <strong>
                  ${{ item.recPrice.toFixed(2) }}
                </strong>
              </p>
            </div>
          </div>
          <!-- Next Week's Star Buy (rising) -->
          <div class="homecard-component" v-for="item in nextRising" :key="item" @click="handleCardClick(item)">
            <div class="homecard">
              <p class="card-product">
                <strong>{{ item.itemName }}</strong>
                ({{ item.starBuyType }})
              </p>
              <p class="card-price">Recommended Price:
                <strong>
                  ${{ item.recPrice.toFixed(2) }}
                </strong>
              </p>
            </div>
          </div>

        </div>
        <p style="text-align: right" v-if="nextTop.length + nextRising.length > 2">
          Scroll for more <i class="bi bi-chevron-down"></i>
        </p>

      </div>
    </div>



    <div class="chart-container">
      <div v-if="chartLoaded" class="chart-description">
        <h3>Product Demand Comparison</h3>
        <h4>
          <span>Forecasted demand:</span> The raw forecasted demand for each
          product category.
        </h4>
        <h4>
          <span>Final score:</span> Takes into account how much the forecasted
          interest for a product category is expected to grow next week compared
          to its usual level, adjusted by how much it is actually growing from
          this week to the next.
        </h4>
      </div>
      <BarChart @chart-loaded="chartLoaded = true" />
    </div>
  </div>

</template>

<script>
import NavBar from "../components/Navbar.vue";
import BarChart from "../components/BarChart.vue";
import HomeCard from "../components/HomeCard.vue";
import ForecastService from '../../services/getForecast.js'

export default {
  components: {
    NavBar,
    BarChart,
    HomeCard,
  },
  data() {
    return {
      chartLoaded: false,
      currentTop: [],
      currentRising: [],
      nextTop: [],
      nextRising: [],
      product: null,
      item: null
    };
  },

  async mounted() {
    await this.populateStarbuyItems()
  },

  methods: {
    async populateStarbuyItems() {
      try {
        const response = await ForecastService.getStarbuyItems();
        const SBresults = response.data.body
        console.log(SBresults)

        // this week's top and rising
        const current = SBresults.current
        this.currentTop = current.filter(obj => obj.starBuyType === 'top');
        this.currentRising = current.filter(obj => obj.starBuyType === 'rising');
        console.log('Top StarBuyItems (Current):', this.currentTop);
        console.log('Rising StarBuyItems (Current):', this.currentRising);

        // next week's top and rising
        const next = SBresults.forecasted
        this.nextTop = next.filter(obj => obj.starBuyType === 'top');
        this.nextRising = next.filter(obj => obj.starBuyType === 'rising');
        console.log('Top StarBuyItems (Next Week):', this.nextTop);
        console.log('Rising StarBuyItems (Next Week):', this.nextRising);

      } catch (error) {
        console.error("populateStarbuyItems unsuccessful")
      }
    },

    handleCardClick(item) {
      const categoryMapping = {
        'fan': 'fans',
        'air_conditioner': 'air_con',
        'vacuum_cleaner': 'vacuum',
        'gas_hob': 'gas_cooker',
        'induction_hob': 'induction_cooker',
        'airfryer': 'air_fryer',
        'washing_machine_/_dryer': 'washing_machine'
        // Add other mappings as needed
      };
      const categoryToRoute = categoryMapping[item.category.toLowerCase()] || item.category.toLowerCase();


      const url = this.$router.resolve({
        name: 'dashboard',
        params: {
          category: categoryToRoute,
          product: item.product
        }
      }).href;
      window.open(url, '_blank');

    },


  }
};
</script>

<style scoped>
body {
  margin: 0;
  padding-top: 60px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.page-container {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 20px;
  margin-top: 180px;
  width: 60vw;
}

.homecard-container {
  display: flex;
  justify-content: space-around;
  flex-direction: row;
  width: 100%;
  margin-bottom: 20px;
  gap: 20px;
}

.chart-container {
  display: flex;
  align-items: center;
  flex-direction: column;
  padding: 20px;
  width: 150%;
}

.chart-description {
  text-align: center;
  max-width: 65%;
  margin: auto;
}

.chart-description h3 {
  font-weight: bold;
  font-size: 17px;
}

.chart-description h4 span {
  font-weight: bold;
  font-size: 14px;
}

.chart-description h4 {
  font-size: 14px;
  margin-top: 20px;
  margin-bottom: 20px;
}


.homecard-component {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.homecard {
  width: 420px;
  margin-bottom: 20px;
  padding: 20px;
  background: #efefef;
  border-radius: 20px;
  text-align: center;
  align-items: center;
  justify-content: center;
}

.card-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
  padding: 0;
  margin-bottom: 20px;
}

.card-text {
  font-size: 15px;
  color: #2c3e50;
  margin-bottom: 0.25em;
  font-style: italic;
}

.card-price {
  font-size: 15px;
  color: #2c3e50;
  margin-bottom: 0.25em;
  font-style: italic;
}

.card-title .bi {
  margin-left: 8px;
}

.card-product {
  font-size: 15px;
  margin-bottom: 0.25em;
  display: block;
}

.scrollable {
  overflow-y: scroll;
  height: 250px;
  /* Adjust based on header and navbar size */
  scrollbar-width: thin;
  /* For Firefox */
  scrollbar-color: rgba(155, 155, 155, 0.5) rgba(255, 255, 255, 0.5);
  /* For Firefox */

}
</style>