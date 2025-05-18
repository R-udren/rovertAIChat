// API service for making HTTP requests
import { useAuthStore } from '@/stores/auth'

// Base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * Creates a full URL by combining the base URL with the provided endpoint path
 * @param {string} path - The API endpoint path
 * @returns {string} - The complete URL
 */
export const apiUrl = (path) => {
  // Remove leading slash from path if present to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return `${API_BASE_URL}/${cleanPath}`
}

/**
 * Make an authenticated API request
 * @param {string} url - The API endpoint
 * @param {Object} options - Fetch options
 * @param {boolean} refreshOnAuthError - Whether to attempt token refresh on 401
 * @returns {Promise<any>} - The response data
 */
export const apiRequest = async (url, options = {}, refreshOnAuthError = true) => {
  const authStore = useAuthStore()

  // Set default headers
  const headers = {
    ...options.headers,
  }

  // Add auth header if token exists
  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`
  }
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    // Handle 401 Unauthorized - attempt to refresh token
    if (response.status === 401 && refreshOnAuthError) {
      // Try to refresh the token
      const refreshed = await authStore.refreshAccessToken()
      if (refreshed) {
        // Retry the request with the new token
        return apiRequest(url, options, false) // Pass false to prevent infinite loop
      } else {
        // Token refresh failed, force logout
        authStore.logout()
        throw new Error('Authentication failed')
      }
    }

    // Parse JSON response
    const data = await response.json().catch(() => ({}))

    // Handle non-2xx responses
    if (!response.ok) {
      // Structured error formatting
      let errorMessage = `Request failed with status ${response.status}`
      let errors = []

      if (data.detail) {
        if (Array.isArray(data.detail)) {
          // Handle validation errors (like the UUID parsing error)
          data.detail.forEach((err) => {
            // Get field name from location array if available
            const fieldName = err.loc && err.loc.length > 1 ? err.loc[1] : 'unknown field'
            errors.push({
              field: fieldName,
              message: err.msg,
              type: err.type || 'validation_error',
            })
          })
          // Create user-friendly message
          errorMessage = `Validation error: ${errors.map((e) => `${e.field} - ${e.message}`).join('; ')}`
        } else {
          // Simple error message
          errorMessage = data.detail
        }
      }

      const error = new Error(errorMessage)
      error.status = response.status
      error.errors = errors
      error.rawResponse = data
      throw error
    }

    return data
  } catch (error) {
    console.error('API request error:', error)
    throw error
  }
}

/**
 * API service object with methods for common HTTP requests
 */
export const api = {
  /**
   * Send a GET request
   * @param {string} endpoint - API endpoint path
   * @param {Object} options - Additional fetch options
   * @returns {Promise<any>}
   */
  get: (endpoint, options = {}) => {
    return apiRequest(apiUrl(endpoint), {
      method: 'GET',
      ...options,
    })
  },

  /**
   * Send a POST request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request payload
   * @param {Object} options - Additional fetch options
   * @returns {Promise<any>}
   */
  post: (endpoint, data = {}, options = {}) => {
    return apiRequest(apiUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    })
  },

  /**
   * Send a form data POST request (for login)
   * @param {string} endpoint - API endpoint path
   * @param {Object} formData - Form data as key-value pairs
   * @param {Object} options - Additional fetch options
   * @returns {Promise<any>}
   */
  postForm: (endpoint, formData = {}, options = {}) => {
    const urlEncodedData = new URLSearchParams()

    // Add each key-value pair to the URLSearchParams object
    Object.entries(formData).forEach(([key, value]) => {
      urlEncodedData.append(key, value)
    })

    return apiRequest(apiUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...options.headers,
      },
      body: urlEncodedData,
      ...options,
    })
  },

  /**
   * Send a PUT request
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request payload
   * @param {Object} options - Additional fetch options
   * @returns {Promise<any>}
   */
  put: (endpoint, data = {}, options = {}) => {
    return apiRequest(apiUrl(endpoint), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    })
  },

  /**
   * Send a DELETE request
   * @param {string} endpoint - API endpoint path
   * @param {Object} options - Additional fetch options
   * @returns {Promise<any>}
   */
  delete: (endpoint, options = {}) => {
    return apiRequest(apiUrl(endpoint), {
      method: 'DELETE',
      ...options,
    })
  },
}
