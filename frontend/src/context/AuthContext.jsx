import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AUTH_STORAGE_KEY = 'finance_advisor_token'
const USER_STORAGE_KEY = 'finance_advisor_user'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Check for existing token and user on mount
    const checkAuth = async () => {
      try {
        const storedToken = window.localStorage.getItem(AUTH_STORAGE_KEY)
        const storedUser = window.localStorage.getItem(USER_STORAGE_KEY)
        
        if (storedToken && storedUser) {
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
          
          // Verify token is still valid by calling /me endpoint
          try {
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
              headers: {
                'Authorization': `Bearer ${storedToken}`
              }
            })
            
            if (!response.ok) {
              // Token invalid, clear storage
              window.localStorage.removeItem(AUTH_STORAGE_KEY)
              window.localStorage.removeItem(USER_STORAGE_KEY)
              setToken(null)
              setUser(null)
            } else {
              const userData = await response.json()
              setUser(userData)
              window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData))
            }
          } catch (err) {
            console.error('Token verification failed:', err)
            // Keep user logged in even if verification fails (offline mode)
          }
        }
      } catch (err) {
        console.error('Auth initialization error:', err)
      } finally {
        setIsLoading(false)
      }
    }
    
    checkAuth()
  }, [])

  function clearError() {
    setError(null)
  }

  async function login({ email, password, rememberMe = true }) {
    setIsLoading(true)
    setError(null)

    if (!email || !password) {
      setError('Please provide both email address and password.')
      setIsLoading(false)
      return { success: false }
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login/json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || errorData.message || 'Login failed. Please check your credentials.'
        setError(errorMessage)
        setIsLoading(false)
        return { success: false }
      }

      const data = await response.json()
      const { access_token } = data

      // Get user info
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })

      if (!userResponse.ok) {
        setError('Failed to fetch user information.')
        setIsLoading(false)
        return { success: false }
      }

      const userData = await userResponse.json()
      const authenticatedUser = {
        id: userData.id,
        name: userData.name,
        email: userData.email,
        loginAt: new Date().toISOString()
      }

      setToken(access_token)
      setUser(authenticatedUser)

      if (rememberMe) {
        try {
          window.localStorage.setItem(AUTH_STORAGE_KEY, access_token)
          window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authenticatedUser))
        } catch (err) {
          console.error('Failed to save to localStorage:', err)
        }
      }

      setIsLoading(false)
      return { success: true, user: authenticatedUser }

    } catch (err) {
      console.error('Login error:', err)
      setError('Unable to connect to server. Please try again.')
      setIsLoading(false)
      return { success: false }
    }
  }

  async function signup({ name, email, password, confirmPassword }) {
    setIsLoading(true)
    setError(null)

    if (!name || !email || !password) {
      setError('All fields are required.')
      setIsLoading(false)
      return { success: false }
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      setIsLoading(false)
      return { success: false }
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.')
      setIsLoading(false)
      return { success: false }
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim().toLowerCase(),
          password
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        let errorMessage = 'Registration failed. Please try again.'
        
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(e => e.msg).join(', ')
          } else {
            errorMessage = errorData.detail
          }
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
        
        setError(errorMessage)
        setIsLoading(false)
        return { success: false }
      }

      const data = await response.json()
      const { access_token } = data

      // Get user info
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })

      if (!userResponse.ok) {
        setError('Registration successful, but failed to fetch user information.')
        setIsLoading(false)
        return { success: false }
      }

      const userData = await userResponse.json()
      const registeredUser = {
        id: userData.id,
        name: userData.name,
        email: userData.email,
        loginAt: new Date().toISOString()
      }

      setToken(access_token)
      setUser(registeredUser)

      try {
        window.localStorage.setItem(AUTH_STORAGE_KEY, access_token)
        window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(registeredUser))
      } catch (err) {
        console.error('Failed to save to localStorage:', err)
      }

      setIsLoading(false)
      return { success: true, user: registeredUser }

    } catch (err) {
      console.error('Signup error:', err)
      setError('Unable to connect to server. Please try again.')
      setIsLoading(false)
      return { success: false }
    }
  }

  function loginAsDemo() {
    setIsLoading(true)
    setError(null)

    // For demo mode, create a mock user but use real backend if available
    const demoUser = {
      id: 'demo_user',
      name: 'Alexander Wright',
      email: 'alexander.wright@advisory.internal',
      role: 'Private Wealth Client',
      loginAt: new Date().toISOString(),
    }

    setUser(demoUser)
    setToken('demo_token') // Demo token for demo mode
    try {
      window.localStorage.setItem(AUTH_STORAGE_KEY, 'demo_token')
      window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(demoUser))
    } catch {
      // Ignore
    }
    setIsLoading(false)
    return { success: true, user: demoUser }
  }

  function logout() {
    setUser(null)
    setToken(null)
    setError(null)
    try {
      window.localStorage.removeItem(AUTH_STORAGE_KEY)
      window.localStorage.removeItem(USER_STORAGE_KEY)
    } catch {
      // Ignore
    }
  }

  // Helper function to get current token
  function getToken() {
    return token
  }

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      isLoading,
      error,
      login,
      signup,
      loginAsDemo,
      logout,
      clearError,
      getToken,
    }),
    [user, token, isLoading, error],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
