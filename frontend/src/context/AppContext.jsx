import { createContext, useContext, useEffect, useMemo, useReducer } from 'react'

/**
 * Single source of truth for the planning journey: profile, risk
 * assessment, goal, generated plans, selected plan, and chat history. Kept
 * as plain React Context + useReducer (no Redux) per the hackathon-MVP
 * scope. State is mirrored to localStorage so a page refresh mid-demo
 * doesn't lose progress.
 */

export const STEPS = [
  { key: 'profile', label: 'Profile' },
  { key: 'risk', label: 'Risk' },
  { key: 'goal', label: 'Goal' },
  { key: 'plans', label: 'Plans' },
  { key: 'chatbot', label: 'Chat' },
]

const STORAGE_KEY = 'finance-advisor-state-v1'

const initialState = {
  step: 'profile',
  completedSteps: [],
  profile: { input: null, result: null },
  risk: { answers: {}, result: null },
  goal: { input: null, result: null },
  plans: [],
  comparison: null,
  selectedPlan: null,
  viewingPlanName: null,
  chat: { conversationId: null, messages: [], draft: '' },
}

function loadInitialState() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return initialState
    const parsed = JSON.parse(raw)
    return { ...initialState, ...parsed }
  } catch {
    return initialState
  }
}

function reducer(state, action) {
  switch (action.type) {
    case 'GO_TO_STEP':
      return { ...state, step: action.step }
    case 'COMPLETE_STEP': {
      if (state.completedSteps.includes(action.step)) return state
      return { ...state, completedSteps: [...state.completedSteps, action.step] }
    }
    case 'SET_PROFILE':
      return { ...state, profile: { input: action.input, result: action.result } }
    case 'SET_RISK_ANSWERS':
      return { ...state, risk: { ...state.risk, answers: action.answers } }
    case 'SET_RISK_RESULT':
      return { ...state, risk: { ...state.risk, result: action.result } }
    case 'SET_GOAL':
      return { ...state, goal: { input: action.input, result: action.result } }
    case 'SET_PLANS':
      return { ...state, plans: action.plans }
    case 'SET_COMPARISON':
      return { ...state, comparison: action.comparison }
    case 'SET_SELECTED_PLAN':
      return { ...state, selectedPlan: action.plan }
    case 'SET_VIEWING_PLAN':
      return { ...state, viewingPlanName: action.planName }
    case 'SET_CHAT_CONVERSATION_ID':
      return { ...state, chat: { ...state.chat, conversationId: action.conversationId } }
    case 'ADD_CHAT_MESSAGE':
      return { ...state, chat: { ...state.chat, messages: [...state.chat.messages, action.message] } }
    case 'SET_CHAT_MESSAGES':
      return { ...state, chat: { ...state.chat, messages: action.messages } }
    case 'SET_CHAT_DRAFT':
      return { ...state, chat: { ...state.chat, draft: action.draft } }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

const AppStateContext = createContext(null)

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, loadInitialState)

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Storage may be unavailable (private browsing, quota) — non-fatal for the demo.
    }
  }, [state])

  const value = useMemo(() => ({ state, dispatch }), [state])

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>
}

export function useApp() {
  const ctx = useContext(AppStateContext)
  if (!ctx) throw new Error('useApp must be used within an AppProvider')
  return ctx
}
