import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import { AppProvider, clearLegacyState } from './context/AppContext.jsx'
import './styles/theme.css'
import './styles/global.css'
import './styles/auth.css'
import './styles/landing.css'

// Clear old v1 state on app load (migration helper)
clearLegacyState()

function AppWithAuth() {
  const { user } = useAuth()
  return (
    <AppProvider userId={user?.id}>
      <App />
    </AppProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <AppWithAuth />
    </AuthProvider>
  </React.StrictMode>,
)

