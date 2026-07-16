import { useCallback } from "react";
import { API_ORIGIN } from "@/api/apiSlice";

export interface StreamEvent {
  type: "token" | "tool_start" | "tool_result" | "done" | "error";
  data: any;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  user_id: string;
}

const API_BASE_URL = API_ORIGIN;

export function useSendChatMessage() {
  return useCallback(
    async (
      request: ChatRequest,
      onEvent: (event: StreamEvent) => void
    ): Promise<void> => {
      const response = await fetch(`${API_BASE_URL}/api/assistant/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to send message");
      }

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const streamEvent: StreamEvent = JSON.parse(line.slice(6));
                onEvent(streamEvent);

                if (streamEvent.type === "done" || streamEvent.type === "error") {
                  return;
                }
              } catch {
                // Ignore parse errors
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    },
    []
  );
}
