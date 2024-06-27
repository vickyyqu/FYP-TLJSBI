<template>
  <NavBar />
  <router-view class="main-content" />
</template>

<script>
import NavBar from './components/Navbar.vue';

export default {
  components: {
    NavBar
  }
};
</script>

<style>

#app {
  display: flex;
  justify-content: center; /* This centers the child horizontally */
  align-items: start; /* Aligns children to the top */
  height: 100%;
  width: 100%;
  font-family:Verdana, Geneva, Tahoma, sans-serif
}

.main-content {
  padding-top: 0px; /* Adjust this to match the navbar height */
  padding-bottom: 0px; /* Add some space at the bottom */
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  /* This ensures that there is no scroll overflow */
  overflow-x: hidden;
}


</style>
