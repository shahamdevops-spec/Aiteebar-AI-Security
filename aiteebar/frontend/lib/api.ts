import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor - add JWT token
    this.client.interceptors.request.use((config) => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Clear token on unauthorized
          if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token')
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async register(email: string, password: string, name: string) {
    return this.client.post('/v1/auth/register', {
      email,
      password,
      name,
    })
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/v1/auth/login', {
      email,
      password,
    })
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response
  }

  async getCurrentUser() {
    return this.client.get('/v1/auth/me')
  }

  // Generic request methods
  async get<T = any>(url: string, config?: any) {
    return this.client.get<T>(url, config)
  }

  async post<T = any>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config)
  }

  async put<T = any>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config)
  }

  async patch<T = any>(url: string, data?: any, config?: any) {
    return this.client.patch<T>(url, data, config)
  }

  async delete<T = any>(url: string, config?: any) {
    return this.client.delete<T>(url, config)
  }

  // Health check
  async healthCheck() {
    try {
      return await this.client.get('/health')
    } catch (error) {
      return null
    }
  }
}

export const api = new ApiClient()
