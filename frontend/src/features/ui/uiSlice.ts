import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface UIState {
  activePanel: "form" | "chat" | "split";
  showInteractionDetail: boolean;
  selectedInteractionId: string | null;
  toast: {
    type: "success" | "error" | "info" | "warning";
    message: string;
  } | null;
}

const initialState: UIState = {
  activePanel: "split",
  showInteractionDetail: false,
  selectedInteractionId: null,
  toast: null,
};

export const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    setActivePanel: (state, action: PayloadAction<"form" | "chat" | "split">) => {
      state.activePanel = action.payload;
    },
    setShowInteractionDetail: (state, action: PayloadAction<boolean>) => {
      state.showInteractionDetail = action.payload;
    },
    setSelectedInteractionId: (state, action: PayloadAction<string | null>) => {
      state.selectedInteractionId = action.payload;
    },
    showToast: (
      state,
      action: PayloadAction<{ type: "success" | "error" | "info" | "warning"; message: string }>
    ) => {
      state.toast = action.payload;
    },
    clearToast: (state) => {
      state.toast = null;
    },
  },
});

export const {
  setActivePanel,
  setShowInteractionDetail,
  setSelectedInteractionId,
  showToast,
  clearToast,
} = uiSlice.actions;

export default uiSlice.reducer;
