<template>
  <tr class="spacer"><td colspan="4"></td></tr>
  <tr class="product-item" @click="emitClickEvent">
      <td> {{ product.brand }} </td>
      <td> {{ product.model }}</td>
      <td> {{ product.platform }}</td>
      <td> {{ product.discountedPrice }}</td>
      <td> {{ product.category }}</td>
  </tr>
</template>

<script>
export default {
  name: 'ProductItem',
  props: {
    product: Object
  },
  methods: {
    emitClickEvent() {
      this.$emit('product-clicked');
    }
  },
  filters: {
    currency(value) {
      return parseFloat(value).toFixed(2);
    }
  },
  async mounted(){

  }
}
</script>

<style scoped>
.product-item {
  background-color: #f8f8f8;
  transition: background-color 0.3s ease;
  text-align: center;
  border-radius: 20px;    
}

.product-item:hover {
  background-color: #f9f9f9;
  cursor: pointer;
}

.tr {
  border-radius: 30px;
  border-spacing: 0 20px; /* This applies 20px vertical spacing between rows */
}
.product-item td {
  padding: 10px 15px;
  border-bottom: none;
  color: black;
  background-color: #f9f9f9;
}

.product-item td:first-child {
  border-top-left-radius: 10px;
  border-bottom-left-radius: 10px;
}

.product-item td:last-child {
  border-top-right-radius: 10px;
  border-bottom-right-radius: 10px;
}

.spacer td {
height: 20px; /* This is the space height */
background-color: transparent; /* No background color */
border: 0px
}
</style>