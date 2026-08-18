import { useRef, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

export default function AuthLanding() {
  const { login, signup, loginAsDemo, error: contextError, clearError, isLoading } =
    useAuth()

  const authSectionRef = useRef(null)

  const [activeTab, setActiveTab] = useState('login') // 'login' | 'signup'
  const [formErrors, setFormErrors] = useState({})
  const [infoMessage, setInfoMessage] = useState('')

  // Login form state
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(true)

  // Sign up form state
  const [signupName, setSignupName] = useState('')
  const [signupEmail, setSignupEmail] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  const [signupConfirmPassword, setSignupConfirmPassword] = useState('')
  const [agreeTerms, setAgreeTerms] = useState(false)

  function handleTabChange(tab) {
    setActiveTab(tab)
    setFormErrors({})
    setInfoMessage('')
    clearError()
  }

  function goToAuth(tab) {
    handleTabChange(tab)
    authSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  function validateEmail(email) {
    return /\S+@\S+\.\S+/.test(email)
  }

  async function handleLoginSubmit(e) {
    e.preventDefault()
    setFormErrors({})
    setInfoMessage('')
    clearError()

    const errors = {}
    if (!loginEmail.trim()) {
      errors.loginEmail = 'Email address is required.'
    } else if (!validateEmail(loginEmail)) {
      errors.loginEmail = 'Please enter a valid email address.'
    }

    if (!loginPassword) {
      errors.loginPassword = 'Password is required.'
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    await login({
      email: loginEmail,
      password: loginPassword,
      rememberMe,
    })
  }

  async function handleSignupSubmit(e) {
    e.preventDefault()
    setFormErrors({})
    setInfoMessage('')
    clearError()

    const errors = {}
    if (!signupName.trim()) {
      errors.signupName = 'Full name is required.'
    }

    if (!signupEmail.trim()) {
      errors.signupEmail = 'Email address is required.'
    } else if (!validateEmail(signupEmail)) {
      errors.signupEmail = 'Please enter a valid email address.'
    }

    if (!signupPassword) {
      errors.signupPassword = 'Password is required.'
    } else if (signupPassword.length < 8) {
      errors.signupPassword = 'Password must be at least 8 characters long.'
    }

    if (!signupConfirmPassword) {
      errors.signupConfirmPassword = 'Confirm your password.'
    } else if (signupPassword !== signupConfirmPassword) {
      errors.signupConfirmPassword = 'Passwords do not match.'
    }

    if (!agreeTerms) {
      errors.agreeTerms = 'You must acknowledge the platform terms to continue.'
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    await signup({
      name: signupName,
      email: signupEmail,
      password: signupPassword,
      confirmPassword: signupConfirmPassword,
    })
  }

  function handleForgotPassword(e) {
    e.preventDefault()
    setInfoMessage(
      'Password recovery instructions will be dispatched to your registered email address upon verification.',
    )
  }

  return (
    <div className="auth-landing-root">
      <header className="auth-navbar">
        <div className="auth-navbar__inner">
          <div className="auth-brand">
            <span className="auth-brand__name">Financial Advisory Platform</span>
            <span className="auth-brand__tagline">Client Advisory Portal</span>
          </div>

          <div className="auth-navbar__actions">
            <button
              type="button"
              className="auth-navbar__link-btn"
              onClick={() => goToAuth('login')}
            >
              Sign In
            </button>
            <button
              type="button"
              className="auth-navbar__cta"
              onClick={() => goToAuth('signup')}
            >
              Get Started
            </button>
          </div>
        </div>
      </header>

      <main className="landing-main">
        <section className="landing-hero">
          <div className="landing-hero__intro">
            <h1 className="landing-hero__title">
              Plan your wealth with clarity, not guesswork.
            </h1>
          </div>

          <div className="auth-container" id="auth-section" ref={authSectionRef}>
          <div className="auth-card">
            <div className="auth-card__header">
              <span className="auth-card__badge">Account Access</span>
              <h1 className="auth-card__title">
                {activeTab === 'login' ? 'Client Sign In' : 'Create an Account'}
              </h1>
              <p className="auth-card__description">
                {activeTab === 'login'
                  ? 'Access your customized financial plan, projections, and advisor consultation.'
                  : 'Register your profile to begin your customized financial planning journey.'}
              </p>
            </div>

            <div className="auth-tabs">
              <button
                type="button"
                className={`auth-tab ${activeTab === 'login' ? 'auth-tab--active' : ''}`}
                onClick={() => handleTabChange('login')}
              >
                Sign In
              </button>
              <button
                type="button"
                className={`auth-tab ${activeTab === 'signup' ? 'auth-tab--active' : ''}`}
                onClick={() => handleTabChange('signup')}
              >
                Create Account
              </button>
            </div>

            {contextError && (
              <div className="auth-alert auth-alert--error" style={{ marginBottom: '16px' }}>
                {contextError}
              </div>
            )}

            {infoMessage && (
              <div className="auth-alert auth-alert--info" style={{ marginBottom: '16px' }}>
                {infoMessage}
              </div>
            )}

            {activeTab === 'login' ? (
              <form className="auth-form" onSubmit={handleLoginSubmit} noValidate>
                <div className="auth-field">
                  <label className="auth-field__label" htmlFor="login-email">
                    Email Address
                  </label>
                  <input
                    id="login-email"
                    type="email"
                    className={`auth-input ${formErrors.loginEmail ? 'auth-input--error' : ''}`}
                    placeholder="name@example.com"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    autoComplete="email"
                  />
                  {formErrors.loginEmail && (
                    <span className="auth-field__error-text">
                      {formErrors.loginEmail}
                    </span>
                  )}
                </div>

                <div className="auth-field">
                  <div className="auth-field__label-row">
                    <label className="auth-field__label" htmlFor="login-password">
                      Password
                    </label>
                    <button
                      type="button"
                      className="auth-field__forgot"
                      onClick={handleForgotPassword}
                    >
                      Forgot password?
                    </button>
                  </div>
                  <input
                    id="login-password"
                    type="password"
                    className={`auth-input ${formErrors.loginPassword ? 'auth-input--error' : ''}`}
                    placeholder="Enter your password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    autoComplete="current-password"
                  />
                  {formErrors.loginPassword && (
                    <span className="auth-field__error-text">
                      {formErrors.loginPassword}
                    </span>
                  )}
                </div>

                <label className="auth-checkbox-label">
                  <input
                    type="checkbox"
                    className="auth-checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Remember me on this browser</span>
                </label>

                <button
                  type="submit"
                  className="auth-btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? 'Authenticating...' : 'Sign In to Portal'}
                </button>

                <div className="auth-divider">
                  <span>OR</span>
                </div>

                <button
                  type="button"
                  className="auth-btn-secondary"
                  onClick={loginAsDemo}
                  disabled={isLoading}
                >
                  Continue as Demo Client
                </button>
              </form>
            ) : (
              <form className="auth-form" onSubmit={handleSignupSubmit} noValidate>
                <div className="auth-field">
                  <label className="auth-field__label" htmlFor="signup-name">
                    Full Name
                  </label>
                  <input
                    id="signup-name"
                    type="text"
                    className={`auth-input ${formErrors.signupName ? 'auth-input--error' : ''}`}
                    placeholder="First and Last Name"
                    value={signupName}
                    onChange={(e) => setSignupName(e.target.value)}
                    autoComplete="name"
                  />
                  {formErrors.signupName && (
                    <span className="auth-field__error-text">
                      {formErrors.signupName}
                    </span>
                  )}
                </div>

                <div className="auth-field">
                  <label className="auth-field__label" htmlFor="signup-email">
                    Email Address
                  </label>
                  <input
                    id="signup-email"
                    type="email"
                    className={`auth-input ${formErrors.signupEmail ? 'auth-input--error' : ''}`}
                    placeholder="name@example.com"
                    value={signupEmail}
                    onChange={(e) => setSignupEmail(e.target.value)}
                    autoComplete="email"
                  />
                  {formErrors.signupEmail && (
                    <span className="auth-field__error-text">
                      {formErrors.signupEmail}
                    </span>
                  )}
                </div>

                <div className="auth-field">
                  <label className="auth-field__label" htmlFor="signup-password">
                    Password
                  </label>
                  <input
                    id="signup-password"
                    type="password"
                    className={`auth-input ${formErrors.signupPassword ? 'auth-input--error' : ''}`}
                    placeholder="Minimum 8 characters"
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
                    autoComplete="new-password"
                  />
                  {formErrors.signupPassword && (
                    <span className="auth-field__error-text">
                      {formErrors.signupPassword}
                    </span>
                  )}
                  <span className="auth-field__hint">
                    Use at least 8 characters with a mix of letters and numbers.
                  </span>
                </div>

                <div className="auth-field">
                  <label className="auth-field__label" htmlFor="signup-confirm">
                    Confirm Password
                  </label>
                  <input
                    id="signup-confirm"
                    type="password"
                    className={`auth-input ${formErrors.signupConfirmPassword ? 'auth-input--error' : ''}`}
                    placeholder="Re-enter your password"
                    value={signupConfirmPassword}
                    onChange={(e) => setSignupConfirmPassword(e.target.value)}
                    autoComplete="new-password"
                  />
                  {formErrors.signupConfirmPassword && (
                    <span className="auth-field__error-text">
                      {formErrors.signupConfirmPassword}
                    </span>
                  )}
                </div>

                <label className="auth-checkbox-label">
                  <input
                    type="checkbox"
                    className="auth-checkbox"
                    checked={agreeTerms}
                    onChange={(e) => setAgreeTerms(e.target.checked)}
                  />
                  <span>
                    I acknowledge the platform privacy guidelines and advisory disclosure terms.
                  </span>
                </label>
                {formErrors.agreeTerms && (
                  <span className="auth-field__error-text">
                    {formErrors.agreeTerms}
                  </span>
                )}

                <button
                  type="submit"
                  className="auth-btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? 'Creating Account...' : 'Create Account'}
                </button>
              </form>
            )}

            <div className="auth-footer-notice">
              Authorized financial advisory workspace. Strictly confidential.
            </div>
          </div>
          </div>
        </section>
      </main>

      <footer className="auth-landing-footer">
        Financial Planning Platform. Informational and analytical purposes only.
      </footer>
    </div>
  )
}
