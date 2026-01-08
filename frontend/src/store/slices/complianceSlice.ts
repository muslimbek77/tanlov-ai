import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ComplianceCheck {
  id: number
  tenderId: number
  participantId: number
  status: string
  score: number
  details: string
  createdAt: string
}

interface ComplianceState {
  complianceChecks: ComplianceCheck[]
  loading: boolean
  error: string | null
}

const initialState: ComplianceState = {
  complianceChecks: [],
  loading: false,
  error: null,
}

const complianceSlice = createSlice({
  name: 'compliance',
  initialState,
  reducers: {
    setComplianceChecks: (state, action: PayloadAction<ComplianceCheck[]>) => {
      state.complianceChecks = action.payload
    },
    addComplianceCheck: (state, action: PayloadAction<ComplianceCheck>) => {
      state.complianceChecks.push(action.payload)
    },
  },
})

export const { setComplianceChecks, addComplianceCheck } = complianceSlice.actions
export default complianceSlice.reducer
