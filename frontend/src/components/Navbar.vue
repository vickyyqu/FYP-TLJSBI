<template>
  <nav class="navbar navbar-expand-lg bg-light">
    <div class="container">
      <div class="header text-center" style="background-color: black">
        <small style="color: white; font-size: 12px"
          >TLJ Star-Buy Intel (SBI) Platform
        </small>
      </div>
      <!-- Brand/logo -->
      <div class="navbar-brand">
        <div class="logo pb-0">TLJ SBI</div>
        <div class="sub-text text-center">Star-Buy Intel</div>
      </div>

      <!-- Navbar links -->
      <div class="navbar-links" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/home">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/products">Products</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/marketTrends"
              >Market Trends</router-link
            >
          </li>
        </ul>
      </div>
      <div class="profile d-flex align-items-center" v-if="!user">
        <router-link class="nav-link" to="/">
          <span class="nav-link">Login</span>
        </router-link>
      </div>
      <div class="profile d-flex align-items-center" v-if="user">
        <router-link class="nav-link" to="/" @click="logout">
          <span class="nav-link">Logout</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script>
import { onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from "./../components/firebase/index.js";
export default {
  name: "Navbar",
  data() {
    return {
      user: null,
    };
  },
  created() {
    onAuthStateChanged(auth, (firebaseUser) => {
      this.user = firebaseUser;
    });
  },
  methods: {
    logout() {
      signOut(auth)
        .then(() => {
          this.user = null;
          this.$router.push("/");
        })
        .catch((error) => {
          console.error("Logout Error:", error);
        });
    },
  },
};
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 25px;
  z-index: 1001;
}
.navbar {
  position: fixed;
  top: 20px;
  left: 0;
  right: 0;
  height: 100px;
  margin: 0px 0.5px;
  padding: 20px 50px;
  z-index: 1000;
}

.logo {
  font-size: 40px;
  font-weight: bold;
  padding-left: 80px;
}

.sub-text {
  font-size: 12px;
  padding-left: 80px;
}

.nav-link {
  color: black;
  margin-right: 100px; /* Add space to the right of each link */
}
.nav-link:hover {
  font-style: italics;
}

.nav-item:last-child .nav-link {
  margin-right: 0;
}

.profile {
  /* Align profile icon and name */
  display: flex;
  align-items: center;
  justify-content: flex-end; /* Aligns the profile to the end of the container */
}

.user-name {
  padding-left: 5px;
}

.login {
  background-color: rgb(164, 164, 164);
  color: white;
  padding: 8px 15px 8px 15px;
  border-radius: 10px;
}
</style>
