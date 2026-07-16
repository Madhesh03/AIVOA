import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { ChatMessage, InteractionDraft } from "@/types/domain";

interface AssistantState {
  conversationId: string | null;
  messages: ChatMessage[];
  status: "idle" | "streaming" | "error";
  streamingMessageId: string | null;
  activeTool: string | null;
  error: string | null;
  lastAiPrefill: InteractionDraft | null;
}

const initialState: AssistantState = {
  conversationId: null,
  messages: [],
  status: "idle",
  streamingMessageId: null,
  activeTool: null,
  error: null,
  lastAiPrefill: null,
};

export const assistantSlice = createSlice({
  name: "assistant",
  initialState,
  reducers: {
    setConversationId: (state, action: PayloadAction<string>) => {
      state.conversationId = action.payload;
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    appendToLastMessage: (state, action: PayloadAction<string>) => {
      if (state.messages.length > 0) {
        const lastMessage = state.messages[state.messages.length - 1];
        lastMessage.content += action.payload;
      }
    },
    setStatus: (state, action: PayloadAction<"idle" | "streaming" | "error">) => {
      state.status = action.payload;
    },
    setActiveTool: (state, action: PayloadAction<string | null>) => {
      state.activeTool = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      if (action.payload) {
        state.status = "error";
      }
    },
    setLastAiPrefill: (state, action: PayloadAction<InteractionDraft | null>) => {
      state.lastAiPrefill = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [];
      state.conversationId = null;
    },
    resetAssistant: (state) => {
      Object.assign(state, initialState);
    },
  },
});

export const {
  setConversationId,
  addMessage,
  appendToLastMessage,
  setStatus,
  setActiveTool,
  setError,
  setLastAiPrefill,
  clearMessages,
  resetAssistant,
} = assistantSlice.actions;

export default assistantSlice.reducer;
