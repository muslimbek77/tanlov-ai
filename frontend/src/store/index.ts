import { configureStore } from "@reduxjs/toolkit";
import tenderReducer from "./slices/tenderSlice";

export const store = configureStore({
  reducer: {
    tenders: tenderReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
