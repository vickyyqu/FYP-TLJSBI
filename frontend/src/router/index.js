import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import ProductsView from '../views/ProductsView.vue'
import MarketTrendsView from '../views/MarketTrendsView.vue'
import DashboardView from '../views/DashboardView.vue'
import {auth} from "./../components/firebase/index.js";
import {onAuthStateChanged} from "firebase/auth";

// Define a function to return a promise that resolves when the auth state is known
function getCurrentUser(auth) {
  return new Promise((resolve, reject) => {
    const unsubscribe = onAuthStateChanged(auth, user => {
      unsubscribe();
      resolve(user);
    }, reject);
  });
}
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/products',
      name: 'products',
      component: ProductsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/markettrends',
      name: 'markettrends',
      component: MarketTrendsView ,
      meta: { requiresAuth: true }  
    },
    {
      path: '/dashboard/:category/:product',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
      props: (route) => ({
        category: route.params.category,
        product: route.params.product,
      })
    },
    
    {
      path: '/',
      name: 'login',
      component: LoginView
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const user = await getCurrentUser(auth);

  if (requiresAuth && !user) {
    next('/');
  } else if (to.path === '/' && user) {
    next('/home');
  } else {
    next();
  }
});

export default router;