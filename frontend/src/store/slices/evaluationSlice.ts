import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Evaluation {
  id: number
  tenderId: number
  participantId: number
  score: number
  status: string
  createdAt: string
}

interface EvaluationState {
  evaluations: Evaluation[]
  loading: boolean
  error: string | null
}

const initialState: EvaluationState = {
  evaluations: [],
  loading: false,
  error: null,
}

const evaluationSlice = createSlice({
  name: 'evaluations',
  initialState,
  reducers: {
    setEvaluations: (state, action: PayloadAction<Evaluation[]>) => {
      state.evaluations = action.payload
    },
    addEvaluation: (state, action: PayloadAction<Evaluation>) => {
      state.evaluations.push(action.payload)
    },
  },
})

export const { setEvaluations, addEvaluation } = evaluationSlice.actions
export default evaluationSlice.reducer
