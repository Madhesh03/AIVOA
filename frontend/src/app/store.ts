import { configureStore } from "@reduxjs/toolkit";
import { apiSlice } from "@/api/apiSlice";
import interactionsReducer from "@/features/interactions/interactionsSlice";
import assistantReducer from "@/features/assistant/assistantSlice";
import uiReducer from "@/features/ui/uiSlice";

export const store = configureStore({
  reducer: {
    [apiSlice.reducerPath]: apiSlice.reducer,
    interactions: interactionsReducer,
    assistant: assistantReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(apiSlice.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
