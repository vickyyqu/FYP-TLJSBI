<template>
  <div class="product-list-page">
    <div v-if="isLoading" class="loading-screen">
      Loading All Products....
    </div>
    <div class="search-bar">
      <i class="bi bi-search"></i>
      <input type="text" placeholder="Search for brand or model number..." v-model="search" />
    </div>
    <div class="table-container">
      <div class="table-header-container">
        <table class="table">
          <thead>
            <tr>
              <th>Brand</th>
              <th>Model</th>
              <th>Platform</th>
              <th>Lowest Price / SGD</th>
              <th>Category</th>
            </tr>
          </thead>
        </table>
      </div>
      <div class="table-body-container">
        <table class="table">
          <tbody v-if="search.length > 0">
            <ProductItem v-for="product in filteredList" :product="product"
              @product-clicked="handleProductClick(product)" />
          </tbody>
          <tbody v-if="search.length == 0">


            <ProductItem v-for="product in products" :product="product"
              @product-clicked="handleProductClick(product)" />
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import ProductItem from '../components/ProductItem.vue'; // adjust the path as necessary
import ForecastService from '../../services/getForecast.js';

export default {
  components: {
    ProductItem
  },
  data() {
    return {
      isLoading: true,
      search: '',
      products: [],
      product: null
    }
  },

  async mounted() {
    this.loadTableData();
  },

  computed: {
    filteredList() {
      console.log(this.products[1])
      const filteredList = this.products.filter(product => product.model.toLowerCase().includes(this.search.toLowerCase()));
      console.log(filteredList)
      return filteredList
    }
  },

  methods: {
    async handleProductClick(product) {
      this.product = product
      console.log(product)
      const url = this.$router.resolve({
        name: 'dashboard',
        params: {
          category: this.product.category,
          product: this.product.product
        }
      }).href;
      window.open(url, '_blank');
    },


    async loadTableData() {
      try {
        const response = await ForecastService.getAllProducts();
        const jsonString = response.data.body;
        const results = JSON.parse(jsonString);
        console.log(results.Items)

        this.products = results.Items.map(item => ({
          // "S" for strings and "N" for numbers
          brand: item.brand["S"],
          model: item.model["S"],
          platform: item.platform["S"],
          price: item.listedPrice["N"],
          dateCollected: this.formatDate(item.dateCollected["S"]), // standardise date format

          category: item.category["S"],
          discountPercentage: item.discountPercentage["N"],
          discountedPrice: parseFloat(item.discountedPrice["N"]).toFixed(2),
          modelNumber: item.modelNumber["S"],
          product: item.product["S"]

        }));
        this.isLoading = false;

      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },

    formatDate(dateString) {
      // Check if the date string contains time
      const date = new Date(dateString);

      // Check if the date string contains time
      if (!isNaN(date.getTime())) {
        return date.toISOString().split('T')[0];  // Remove the time portion
      }
      return dateString;
    },
  },


}


</script>

<style scoped>
.product-list-page {
  display: flex;
  justify-content: center;
  /* Center the action links horizontally */
  margin: 10px;
  width: 100%;
  position: fixed;
  top: 180px;
  /* Adjust this value based on the actual height of your main navbar */
  left: 0;
  right: 0;
}

.search-bar {
  background-color: #f8f8f8;
  /* Light grey background */
  border-radius: 15px;
  position: relative;
  display: flex;
  justify-content: center;
  /* Center the action links horizontally */
  align-items: center;
  padding: 20px 20px;
  /* Add some padding above and below the links */
  text-decoration: none;
  padding: 0;
  width: 80%;
  margin-bottom: 20px;
  margin-top: 0;
  /* Remove top margin to reduce space */
  z-index: 1000;
}

.search-bar i {
  position: absolute;
  left: 30px;
  color: rgb(179, 179, 179);
  /* Adjust icon color as necessary */
  z-index: 5;
  /* Ensure the icon stays above the input field */
}

.search-bar input {
  background-color: #f8f8f8;
  /* Light grey background */
  border-radius: 15px;
  width: 100%;
  padding: 20px;
  margin-left: 40px;
  border: none;
  font-size: 15px;
}

.search-bar input::placeholder {
  color: rgb(179, 179, 179);
  /* Light grey placeholder text */
  font-style: italic;
  /* Italicized placeholder text */
}

.search-bar input:focus {
  outline: none;
}

.table-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 80%;
  margin: 0 auto;
  /* Centers the table-container */
  top: 250px;
  /* Adjust this value */
  justify-content: center;
  /* Center the action links horizontally */
  padding: 20px 20px;
  /* Add some padding above and below the links */
  position: fixed;
}

.table-header-container {
  width: 100%;
}

.table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  /* This ensures that the columns do not adjust their size */
}

.table tr th {
  background-color: white;
  border-bottom: 1px solid #ddd;
  text-align: center;
  color: grey;
  font-size: 15px;
  padding: 12px 15px;
  position: sticky;
  top: 0;
  /* This will make the header stick to the top */
  z-index: 10;
}


.table thead {
  background-color: white;
  border-bottom: 1px solid #ddd;
  text-align: center;
  color: grey;
  font-size: 15px;
  padding: 12px 15px;
}



.table-body-container {
  width: 100%;
  overflow-y: auto;
  max-height: calc(100vh - 280px - 60px);
  /* Adjust based on header and navbar size */
}


.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.7); /* Semi-transparent white background */
  z-index: 9999; /* Ensure it's on top of everything */
  display: flex;
  justify-content: center;
  align-items: center;
}

</style>