import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { InteractionDraft, Interaction } from "@/types/domain";

interface InteractionsState {
  formDraft: InteractionDraft;
  draftOrigin: "form" | "ai";
  editingId: string | null;
  // ID of a draft interaction the AI already persisted. When set, confirming
  // the form promotes THIS record instead of creating a duplicate.
  aiDraftId: string | null;
  lastSavedId: string | null;
}

const initialState: InteractionsState = {
  formDraft: {},
  draftOrigin: "form",
  editingId: null,
  aiDraftId: null,
  lastSavedId: null,
};

export const interactionsSlice = createSlice({
  name: "interactions",
  initialState,
  reducers: {
    updateFormDraft: (state, action: PayloadAction<Partial<InteractionDraft>>) => {
      state.formDraft = { ...state.formDraft, ...action.payload };
    },
    setFormDraft: (state, action: PayloadAction<InteractionDraft>) => {
      state.formDraft = action.payload;
    },
    applyAiPrefill: (
      state,
      action: PayloadAction<{ draft: InteractionDraft; interactionId?: string | null }>
    ) => {
      state.formDraft = { ...state.formDraft, ...action.payload.draft };
      state.draftOrigin = "ai";
      state.aiDraftId = action.payload.interactionId ?? null;
      // AI prefill targets a fresh log, not an edit of an existing logged record.
      state.editingId = null;
    },
    resetFormDraft: (state) => {
      state.formDraft = {};
      state.draftOrigin = "form";
      state.editingId = null;
      state.aiDraftId = null;
    },
    setEditingId: (state, action: PayloadAction<string | null>) => {
      state.editingId = action.payload;
    },
    setAiDraftId: (state, action: PayloadAction<string | null>) => {
      state.aiDraftId = action.payload;
    },
    setLastSavedId: (state, action: PayloadAction<string | null>) => {
      state.lastSavedId = action.payload;
    },
    loadInteractionForEdit: (state, action: PayloadAction<Interaction>) => {
      const interaction = action.payload;
      state.formDraft = {
        hcp_id: interaction.hcp_id,
        interaction_type: interaction.interaction_type,
        channel: interaction.channel,
        interaction_date: interaction.interaction_date,
        subject: interaction.subject,
        notes: interaction.notes,
        sentiment: interaction.sentiment,
        products: interaction.products,
        follow_up_actions: interaction.follow_up_actions,
      };
      state.editingId = interaction.id;
      state.aiDraftId = null;
      state.draftOrigin = "form";
    },
  },
});

export const {
  updateFormDraft,
  setFormDraft,
  applyAiPrefill,
  resetFormDraft,
  setEditingId,
  setAiDraftId,
  setLastSavedId,
  loadInteractionForEdit,
} = interactionsSlice.actions;

export default interactionsSlice.reducer;
