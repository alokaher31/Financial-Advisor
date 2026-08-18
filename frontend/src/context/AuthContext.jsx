import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AUTH_STORAGE_KEY = 'finance_advisor_user_session'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(AUTH_STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (parsed && parsed.email) {
          setUser(parsed)
        }
      }
    } catch {
      // Storage access failure is non-fatal
    } finally {
      setIsLoading(false)
    }
  }, [])

  function clearError() {
    setError(null)
  }

  async function login({ email, password, rememberMe = true }) {
    setIsLoading(true)
    setError(null)

    // Simulate standard client-side authentication flow
    await new Promise((resolve) => setTimeout(resolve, 350))

    if (!email || !password) {
      setError('Please provide both email address and password.')
      setIsLoading(false)
      return { success: false }
    }

    const trimmedEmail = email.trim().toLowerCase()
    const derivedName = trimmedEmail.split('@')[0]
    const formattedName =
      derivedName.charAt(0).toUpperCase() + derivedName.slice(1)

    const authenticatedUser = {
      id: `usr_${Date.now()}`,
      name: formattedName || 'Client User',
      email: trimmedEmail,
      loginAt: new Date().toISOString(),
    }

    setUser(authenticatedUser)
    if (rememberMe) {
      try {
        window.localStorage.setItem(
          AUTH_STORAGE_KEY,
          JSON.stringify(authenticatedUser),
        )
      } catch {
        // Ignore localStorage quota errors
      }
    }
    setIsLoading(false)
    return { success: true, user: authenticatedUser }
  }

  async function signup({ name, email, password, confirmPassword }) {
    setIsLoading(true)
    setError(null)

    await new Promise((resolve) => setTimeout(resolve, 400))

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

    const trimmedEmail = email.trim().toLowerCase()
    const registeredUser = {
      id: `usr_${Date.now()}`,
      name: name.trim(),
      email: trimmedEmail,
      loginAt: new Date().toISOString(),
    }

    setUser(registeredUser)
    try {
      window.localStorage.setItem(
        AUTH_STORAGE_KEY,
        JSON.stringify(registeredUser),
      )
    } catch {
      // Ignore localStorage error
    }
    setIsLoading(false)
    return { success: true, user: registeredUser }
  }

  function loginAsDemo() {
    setIsLoading(true)
    setError(null)

    const demoUser = {
      id: 'usr_demo_client',
      name: 'Alexander Wright',
      email: 'alexander.wright@advisory.internal',
      role: 'Private Wealth Client',
      loginAt: new Date().toISOString(),
    }

    setUser(demoUser)
    try {
      window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(demoUser))
    } catch {
      // Ignore
    }
    setIsLoading(false)
    return { success: true, user: demoUser }
  }

  function logout() {
    setUser(null)
    setError(null)
    try {
      window.localStorage.removeItem(AUTH_STORAGE_KEY)
    } catch {
      // Ignore
    }
  }

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      error,
      login,
      signup,
      loginAsDemo,
      logout,
      clearError,
    }),
    [user, isLoading, error],
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
