import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.bundle';
import 'bootstrap-icons/font/bootstrap-icons.css';

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Amplify } from 'aws-amplify';
import amplifyconfig from '../amplifyconfiguration.json';


Amplify.configure(amplifyconfig);

import App from './App.vue'
import router from './router'
import './style.css'


const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')


