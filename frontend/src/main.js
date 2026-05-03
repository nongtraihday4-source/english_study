import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import './assets/css/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// Handle force-logout event dispatched by axios interceptor on refresh failure
window.addEventListener('es:force-logout', async () => {
  const { useAuthStore } = await import('./stores/auth.js')
  const auth = useAuthStore()
  await auth.logout()
  router.push('/login')
})

app.mount('#app')
