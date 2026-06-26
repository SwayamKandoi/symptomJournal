import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/logs': 'http://localhost:8000',
      '/history': 'http://localhost:8000',
      '/insights': 'http://localhost:8000',
      '/dashboard': 'http://localhost:8000',
    },
  },
})
