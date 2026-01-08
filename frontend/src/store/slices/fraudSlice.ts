import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface FraudDetection {
  id: number
  tenderId: number
  participantId: number
  riskLevel: string
  riskScore: number
  details: string
  createdAt: string
}

interface FraudState {
  fraudDetections: FraudDetection[]
  loading: boolean
  error: string | null
}

const initialState: FraudState = {
  fraudDetections: [],
  loading: false,
  error: null,
}

const fraudSlice = createSlice({
  name: 'fraud',
  initialState,
  reducers: {
    setFraudDetections: (state, action: PayloadAction<FraudDetection[]>) => {
      state.fraudDetections = action.payload
    },
    addFraudDetection: (state, action: PayloadAction<FraudDetection>) => {
      state.fraudDetections.push(action.payload)
    },
  },
})

export const { setFraudDetections, addFraudDetection } = fraudSlice.actions
export default fraudSlice.reducer
