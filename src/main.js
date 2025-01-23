import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:5000'

const app = createApp(App)
app.use(router)
app.mount('#app')
