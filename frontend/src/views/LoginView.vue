<template>
  <div class="login-wrapper">
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div class="login-container">
      <h1>Login</h1>
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            placeholder="Enter your username"
            required
            class="form-control"
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            placeholder="Enter your password"
            required
            class="form-control"
          />
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
      </form>
    </div>
  </div>
</template>

<script>
import {
  getAuth,
  signInWithEmailAndPassword,
  onAuthStateChanged,
} from "firebase/auth";
import { auth } from "../components/firebase/index.js";

export default {
  data() {
    return {
      credentials: {
        username: "",
        password: "",
      },
      errorMessage: "",
    };
  },
  created() {
    onAuthStateChanged(auth, (user) => {
      if (user) {
        user.getIdToken().then((token) => {
          localStorage.setItem("userToken", token); // Store the JWT in localStorage
          this.$router.push("/home");
        });
      }
    });
  },
  methods: {
    login() {
      console.log("Logging in with:", this.credentials);
      signInWithEmailAndPassword(
        auth,
        this.credentials.username,
        this.credentials.password
      )
        .then((userCredential) => {
          this.errorMessage = "";
          // Get the JWT token after successful login
          userCredential.user.getIdToken().then((token) => {
            // console.log("JWT Token:", token);
            localStorage.setItem('userToken', token); // Store the JWT in localStorage
            this.$router.push("/home");
          });
        })
        .catch((error) => {
          this.errorMessage = "Invalid username or password. Please try again.";
          console.error("Error:", error.code, error.message);
        });
    },
  },
};
</script>

<style scoped>
.login-wrapper {
  padding-top: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #ffffff; /* Set the background color to white or any other color you prefer */
}
.login-container {
  background: white;
  padding: 40px;
  border-radius: 20px; /* Increase the border-radius to make corners more rounded */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 400px; /* Set a fixed width or use a percentage like 50% for responsiveness */
  max-width: 100%; /* Ensure it doesn't exceed the width of its container */
}
.login-form {
  display: flex;
  flex-direction: column;
}
.form-group {
  margin-bottom: 20px;
}
.form-control {
  padding: 10px;
  margin-top: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.btn-primary {
  padding: 10px;
  border: none;
  border-radius: 4px;
  background-color: grey;
  color: white;
  cursor: pointer;
}
.alert {
  padding: 10px;
  background-color: #f2dede;
  color: #a94442;
  margin-bottom: 20px;
  border-radius: 4px;
}
h1 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 30px;
  font-weight: bold;
}
</style>
