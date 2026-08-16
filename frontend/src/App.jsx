import { useApp, STEPS } from './context/AppContext.jsx'
import ProgressStepper from './components/ProgressStepper.jsx'
import ProfileForm from './pages/ProfileForm.jsx'
import RiskQuestionnaire from './pages/RiskQuestionnaire.jsx'
import GoalInput from './pages/GoalInput.jsx'
import PlanComparison from './pages/PlanComparison.jsx'
import PlanDetail from './pages/PlanDetail.jsx'
import Chatbot from './pages/Chatbot.jsx'

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
  const { state, dispatch } = useApp()
  const ActivePage = STEP_COMPONENTS[state.step] || ProfileForm
  const stepperCurrentKey = STEPPER_KEY_OVERRIDES[state.step] || state.step

  function handleStepClick(stepKey) {
    dispatch({ type: 'GO_TO_STEP', step: stepKey })
  }

  return (
    <div className="app-shell">
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
