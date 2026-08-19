import { useEffect } from 'react'
import { useApp, STEPS } from './context/AppContext.jsx'
import { useAuth } from './context/AuthContext.jsx'
import ProgressStepper from './components/ProgressStepper.jsx'
import { MockDataBanner } from './components/MockDataBanner.jsx'
import LoadingScreen from './components/LoadingState.jsx'
import ProfileForm from './pages/ProfileForm.jsx'
import RiskQuestionnaire from './pages/RiskQuestionnaire.jsx'
import GoalInput from './pages/GoalInput.jsx'
import PlanComparison from './pages/PlanComparison.jsx'
import PlanDetail from './pages/PlanDetail.jsx'
import Chatbot from './pages/Chatbot.jsx'
import AuthLanding from './pages/AuthLanding.jsx'

const STEP_COMPONENTS = {
  profile: ProfileForm,
  risk: RiskQuestionnaire,
  goal: GoalInput,
  plans: PlanComparison,
  planDetail: PlanDetail,
  chatbot: Chatbot,
}

// PlanDetail is a sub-view of the "Plans" stage, not its own stepper entry.
const STEPPER_KEY_OVERRIDES = { planDetail: 'plans' }

export default function App() {
  const { isAuthenticated, user, logout } = useAuth()
  const { state, dispatch } = useApp()
  
  // Route guard: enforce onboarding flow
  // New users or users without completed profile must start at profile
  const hasProfile = state.profile.result?.profileId != null
  const hasRisk = state.risk.result?.riskScore != null
  const hasGoal = state.goal.result?.goalId != null
  const hasPlans = state.plans.length > 0
  
  // Redirect logic: enforce sequential completion
  let enforcedStep = state.step
  if (!hasProfile && state.step !== 'profile') {
    enforcedStep = 'profile'
  } else if (hasProfile && !hasRisk && state.step !== 'profile' && state.step !== 'risk') {
    enforcedStep = 'risk'
  } else if (hasProfile && hasRisk && !hasGoal && !['profile', 'risk', 'goal'].includes(state.step)) {
    enforcedStep = 'goal'
  } else if (hasProfile && hasRisk && hasGoal && !hasPlans && state.step === 'plans') {
    // Plans page will show "generate plans" button, that's fine
  } else if (state.step === 'planDetail' && !hasPlans) {
    enforcedStep = 'goal'
  } else if (state.step === 'chatbot' && !hasProfile) {
    enforcedStep = 'profile'
  }
  
  // Apply redirect if needed
  if (enforcedStep !== state.step) {
    setTimeout(() => dispatch({ type: 'GO_TO_STEP', step: enforcedStep }), 0)
  }
  
  const ActivePage = STEP_COMPONENTS[enforcedStep] || ProfileForm
  const stepperCurrentKey = STEPPER_KEY_OVERRIDES[enforcedStep] || enforcedStep

  useEffect(() => {
    if (!user?.id) return
    if (state.ownerUserId === null) {
      dispatch({ type: 'SET_OWNER', userId: user.id })
    } else if (String(state.ownerUserId) !== String(user.id)) {
      dispatch({ type: 'RESET_FOR_USER', userId: user.id })
    }
  }, [dispatch, state.ownerUserId, user?.id])

  function handleStepClick(stepKey) {
    // Allow navigation only to completed steps or the next step
    const stepIndex = STEPS.findIndex(s => s.key === stepKey)
    const currentIndex = STEPS.findIndex(s => s.key === enforcedStep)
    
    if (stepKey === 'profile' || state.completedSteps.includes(stepKey) || stepIndex <= currentIndex + 1) {
      dispatch({ type: 'GO_TO_STEP', step: stepKey })
    }
  }

  function handleLogout() {
    dispatch({ type: 'RESET' })
    logout()
  }

  if (!isAuthenticated) {
    return (
      <>
        <MockDataBanner />
        <AuthLanding />
      </>
    )
  }

  if (state.ownerUserId !== null && String(state.ownerUserId) !== String(user.id)) {
    return <LoadingScreen />
  }

  return (
    <div className="app-shell">
      <MockDataBanner />
      <header className="app-header">
        <div className="app-header__inner">
          <div className="brand">
            <span className="brand__mark" aria-hidden="true">
              FA
            </span>
            Finance Advisor
          </div>
          <ProgressStepper
            steps={STEPS}
            currentKey={stepperCurrentKey}
            completedKeys={state.completedSteps}
            onStepClick={handleStepClick}
          />
          <div className="auth-header-user">
            <div className="auth-header-user__info">
              <span className="auth-header-user__name">{user?.name || 'Client'}</span>
              <span className="auth-header-user__role">Client Portal</span>
            </div>
            <button
              type="button"
              className="auth-btn-signout"
              onClick={handleLogout}
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <ActivePage />
      </main>

      <footer className="app-footer">
        AI-Powered Finance Planning System — illustrative demo only, not financial advice.
      </footer>
    </div>
  )
}

