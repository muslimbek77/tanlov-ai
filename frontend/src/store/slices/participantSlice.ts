import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Participant {
  id: number
  name: string
  email: string
  phone: string
  company: string
  status: string
}

interface ParticipantState {
  participants: Participant[]
  loading: boolean
  error: string | null
}

const initialState: ParticipantState = {
  participants: [],
  loading: false,
  error: null,
}

const participantSlice = createSlice({
  name: 'participants',
  initialState,
  reducers: {
    setParticipants: (state, action: PayloadAction<Participant[]>) => {
      state.participants = action.payload
    },
    addParticipant: (state, action: PayloadAction<Participant>) => {
      state.participants.push(action.payload)
    },
  },
})

export const { setParticipants, addParticipant } = participantSlice.actions
export default participantSlice.reducer
