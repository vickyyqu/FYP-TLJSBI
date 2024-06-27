<template>
  <div class="homecard-wrapper">
    <h3 class="card-title">
      {{ title }}
      <i :class="iconClass"></i>
    </h3>
    <div class="homecard">
      <p class="card-product">{{ product }}</p>
      <p class="card-model">{{ model }}</p>
      <p class="card-price">{{ price }}</p>
    </div>
  </div>
</template>

<script>
export default {
  props: ["title", "product", "model", "price"],
  computed: {
    iconClass() {
      if (this.title === "This Week's Star Buy") {
        return "bi bi-star-fill";
      } else if (this.title === "Next Week's Star Buy") {
        return "bi bi-graph-up";
      }
      return "bi"; // Default icon class if no title matches
    },
  },
};
</script>

<style scoped>
.homecard-wrapper {
  display: flex;
  flex-direction: column; /* Stack the title and card vertically */
  align-items: center; /* Center the elements */
}

.homecard {
  width: 150%; /* Full width of its parent container */
  margin-bottom: 20px;
  padding: 20px;
  background: #efefef;
  border-radius: 20px;
  text-align: center;
  align-items: center;
  justify-content: center;
}

.card-title {
  white-space: nowrap; /* Prevents the text from wrapping to the next line */
  overflow: hidden; /* Keeps the content from spilling out of the box */
  text-overflow: ellipsis; /* Adds an ellipsis if the text is too long */
  display: flex; /* Use flex layout */
  align-items: center; /* Center the content vertically */
  justify-content: center; /* Center the content horizontally */
  width: 100%; /* Use the full width of the container */
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0; /* Adjust as needed */
  padding: 0; /* Adjust as needed */
  margin-bottom: 20px;
}

.card-product {
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 0.25em;
}
.card-model {
  font-size: 15px;
  margin-bottom: 0.25em;
}

.card-price {
  font-size: 15px;
  color: #2c3e50; /* A different color for the price */
  margin-bottom: 0.25em;
  font-style: italic;
}

.card-title .bi {
  margin-left: 8px; /* Add some space between the icon and the title */
}
</style>
