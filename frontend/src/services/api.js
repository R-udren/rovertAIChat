// API service for making HTTP requests
import { useAuthStore } from '@/stores/auth'

// Base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * Creates a full URL by combining the base URL with the provided endpoint path
 * @param {string} path - The API endpoint path
 * @returns {string} - The complete URL
 */
export const apiUrl = (path) => {
  // Remove leading slash from path if present to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return `${API_BASE_URL}/api/v1/${cleanPath}`
}

// Track if we're currently refreshing to prevent multiple refresh attempts
let isRefreshing = false
let refreshSubscribers = []

// Helper function to queue failed requests to retry after token refresh
function subscribeToRefresh(callback) {
  refreshSubscribers.push(callback)
}

// Helper function to retry queued requests after successful token refresh
function onRefreshSuccess() {
  refreshSubscribers.forEach((callback) => callback())
  refreshSubscribers = []
}

/**
 * Make an API request with cookie authentication
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

  // Ensure credentials are included (for cookies)
  const requestOptions = {
    ...options,
    headers,
    credentials: 'include', // Always include cookies
  }

  try {
    const response = await fetch(url, requestOptions)

    // Handle 401 Unauthorized - attempt to refresh token
    if (response.status === 401 && refreshOnAuthError) {
      // Prevent retry on the refresh endpoint itself
      if (url.includes('auth/refresh')) {
        // If refresh fails with 401, we're fully logged out
        authStore.logout()
        throw new Error('Authentication session expired')
      }

      // If another refresh is in progress, queue this request
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeToRefresh(() => {
            resolve(apiRequest(url, options, false)) // Don't try refreshing again
          })
        })
      }

      // Start refreshing process
      isRefreshing = true

      try {
        // Try to refresh the token
        const refreshed = await authStore.refreshAccessToken()

        // Token refresh successful
        isRefreshing = false
        onRefreshSuccess()

        if (refreshed) {
          // Retry the original request
          return apiRequest(url, options, false) // Don't try refreshing again
        } else {
          // Refresh failed, force logout
          authStore.logout()
          throw new Error('Authentication failed: Session expired')
        }
      } catch (refreshError) {
        // Refresh failed
        isRefreshing = false
        refreshSubscribers = [] // Clear any queued requests
        authStore.logout()
        throw refreshError
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
    console.error(`API request to ${url} returned ${error.status || 'error'}:`, error)
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
