import router from '@/router'
import axios from 'axios'
import { getAccessToken } from './utils'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })

api.interceptors.request.use((config) => {
    config.headers['Authorization'] = getAccessToken()
    return config
}, (error) => {
    return Promise.reject(error)
})

api.interceptors.response.use((response) => {
    return response
}, (error) => {
    if (error.response) {
        if (error.response.status === 401) {
            router.push({ name: 'login' })
        }
    }
    return Promise.reject(error)
})

export default api
