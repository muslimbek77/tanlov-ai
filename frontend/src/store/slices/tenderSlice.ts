import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'

interface Tender {
  id: number
  title: string
  status: string
  budget: number
  deadline: string
  participants: number
  category: string
}

interface TenderState {
  tenders: Tender[]
  loading: boolean
  error: string | null
}

const initialState: TenderState = {
  tenders: [],
  loading: false,
  error: null,
}

const tenderSlice = createSlice({
  name: 'tenders',
  initialState,
  reducers: {
    setTenders: (state, action: PayloadAction<Tender[]>) => {
      state.tenders = action.payload
    },
    addTender: (state, action: PayloadAction<Tender>) => {
      state.tenders.push(action.payload)
    },
    updateTender: (state, action: PayloadAction<Tender>) => {
      const index = state.tenders.findIndex(t => t.id === action.payload.id)
      if (index !== -1) {
        state.tenders[index] = action.payload
      }
    },
    deleteTender: (state, action: PayloadAction<number>) => {
      state.tenders = state.tenders.filter(t => t.id !== action.payload)
    },
  },
})

export const { setTenders, addTender, updateTender, deleteTender } = tenderSlice.actions
export default tenderSlice.reducer
