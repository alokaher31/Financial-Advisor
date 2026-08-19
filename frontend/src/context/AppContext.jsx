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

const STORAGE_KEY_PREFIX = 'finance-advisor-state-v2-user-'

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

function getStorageKey(userId) {
  // User-specific storage key to prevent cross-user data leakage
  if (!userId) return null
  return `${STORAGE_KEY_PREFIX}${userId}`
}

function loadInitialState(userId) {
  if (!userId) return initialState
  
  try {
    const storageKey = getStorageKey(userId)
    const raw = window.localStorage.getItem(storageKey)
    if (!raw) return initialState
    const parsed = JSON.parse(raw)
    return { ...initialState, ...parsed }
  } catch {
    return initialState
  }
}

// Clear app state for a specific user
export function clearUserState(userId) {
  if (!userId) return
  try {
    const storageKey = getStorageKey(userId)
    window.localStorage.removeItem(storageKey)
  } catch {
    // Ignore
  }
}

// Clear all old v1 state (migration helper)
export function clearLegacyState() {
  try {
    window.localStorage.removeItem('finance-advisor-state-v1')
  } catch {
    // Ignore
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

export function AppProvider({ children, userId }) {
  const [state, dispatch] = useReducer(reducer, undefined, () => loadInitialState(userId))

  // Reset state when userId changes (user switched accounts)
  useEffect(() => {
    const newState = loadInitialState(userId)
    dispatch({ type: 'RESET' })
    // Load the new user's state
    Object.keys(newState).forEach(key => {
      if (key === 'step') {
        dispatch({ type: 'GO_TO_STEP', step: newState.step })
      } else if (key === 'completedSteps') {
        newState.completedSteps.forEach(step => {
          dispatch({ type: 'COMPLETE_STEP', step })
        })
      } else if (key === 'profile') {
        dispatch({ type: 'SET_PROFILE', input: newState.profile.input, result: newState.profile.result })
      } else if (key === 'risk') {
        dispatch({ type: 'SET_RISK_ANSWERS', answers: newState.risk.answers })
        dispatch({ type: 'SET_RISK_RESULT', result: newState.risk.result })
      } else if (key === 'goal') {
        dispatch({ type: 'SET_GOAL', input: newState.goal.input, result: newState.goal.result })
      } else if (key === 'plans') {
        dispatch({ type: 'SET_PLANS', plans: newState.plans })
      } else if (key === 'comparison') {
        dispatch({ type: 'SET_COMPARISON', comparison: newState.comparison })
      } else if (key === 'selectedPlan') {
        dispatch({ type: 'SET_SELECTED_PLAN', plan: newState.selectedPlan })
      }
    })
  }, [userId])

  useEffect(() => {
    if (!userId) return
    
    try {
      const storageKey = getStorageKey(userId)
      window.localStorage.setItem(storageKey, JSON.stringify(state))
    } catch {
      // Storage may be unavailable (private browsing, quota) — non-fatal for the demo.
    }
  }, [state, userId])

  const value = useMemo(() => ({ state, dispatch }), [state])

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>
}

export function useApp() {
  const ctx = useContext(AppStateContext)
  if (!ctx) throw new Error('useApp must be used within an AppProvider')
  return ctx
}
