import React, { useState, useEffect, useRef } from "react";
import { useSendChatMessage, StreamEvent } from "../assistantApi";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import {
  addMessage,
  setStatus,
  setError,
  clearMessages,
  setActiveTool,
  setLastAiPrefill,
  setConversationId,
} from "../assistantSlice";
import { applyAiPrefill } from "@/features/interactions/interactionsSlice";
import { showToast } from "@/features/ui/uiSlice";
import "./ChatPanel.css";

export const ChatPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const messages = useAppSelector((state) => state.assistant.messages);
  const status = useAppSelector((state) => state.assistant.status);
  const activeTool = useAppSelector((state) => state.assistant.activeTool);
  const error = useAppSelector((state) => state.assistant.error);
  const conversationId = useAppSelector((state) => state.assistant.conversationId);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const sendChatMessage = useSendChatMessage();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize conversation ID on first mount
  useEffect(() => {
    if (!conversationId) {
      const newId = `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      dispatch(setConversationId(newId));
    }
  }, [conversationId, dispatch]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    dispatch(addMessage({ role: "user", content: userMessage }));
    setInput("");
    dispatch(setStatus("streaming"));
    setIsLoading(true);

    let assistantMessage = "";

    try {
      await sendChatMessage(
        { message: userMessage, user_id: "user_123", conversation_id: conversationId || undefined },
        (event: StreamEvent) => {
          switch (event.type) {
            case "token":
              // The backend emits the assistant's reply as a single token event.
              assistantMessage += event.data.content || "";
              break;

            case "tool_start":
              dispatch(setActiveTool(event.data.tool));
              break;

            case "tool_result": {
              dispatch(setActiveTool(null));

              if (event.data.form_prefill) {
                const prefill = event.data.form_prefill;
                dispatch(setLastAiPrefill(prefill));
                dispatch(
                  applyAiPrefill({
                    draft: prefill,
                    interactionId: event.data.interaction_id ?? null,
                  })
                );
                dispatch(
                  showToast({
                    type: "success",
                    message: "✨ Form pre-filled from AI — review and confirm to log.",
                  })
                );
              } else if (event.data.success) {
                dispatch(
                  showToast({
                    type: "success",
                    message: event.data.result?.message || "Action completed",
                  })
                );
              } else if (event.data.error) {
                dispatch(
                  showToast({ type: "error", message: `Tool error: ${event.data.error}` })
                );
              }
              break;
            }

            case "error":
              dispatch(setError(event.data.error || "Unknown error"));
              break;

            case "done":
            default:
              break;
          }
        }
      );

      if (assistantMessage.trim()) {
        dispatch(addMessage({ role: "assistant", content: assistantMessage.trim() }));
      }
      dispatch(setStatus("idle"));
    } catch (err: any) {
      dispatch(setError(err?.message || "Failed to send message"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    dispatch(clearMessages());
    setInput("");
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h3 className="chat-title">AI Assistant</h3>
        <button
          className="chat-clear-btn"
          onClick={handleClearChat}
          title="Clear chat history"
        >
          ⟳
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">🤖</div>
            <p className="chat-empty-text">
              Describe your HCP interaction in natural language and I'll help you create a structured log.
            </p>
            <p className="chat-empty-hint">
              Example: "Met Dr. Rao today about Onco-X. She was very positive. Follow up in 2 weeks."
            </p>
          </div>
        ) : (
          messages.map((message, idx) => (
            <div key={idx} className={`chat-message chat-message-${message.role}`}>
              <div className="chat-message-content">
                {message.content
                  .replace(/\*\*/g, "")
                  .replace(/\*([^*]+)\*/g, (_, text) => text)
                  .split("\n")
                  .map((line, i) => (
                    line.trim() && <div key={i}>{line}</div>
                  ))}
              </div>
            </div>
          ))
        )}

        {activeTool && (
          <div className="chat-tool-activity">
            <span className="chat-tool-icon">⚡</span>
            <span className="chat-tool-text">{activeTool}</span>
            <span className="chat-tool-status">processing...</span>
          </div>
        )}

        {error && (
          <div className="chat-error-message">
            <span className="chat-error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <div className="chat-input-wrapper">
          <input
            type="text"
            className="chat-input"
            placeholder="Describe your HCP interaction..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading || status === "error"}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={!input.trim() || isLoading}
            title="Send message"
          >
            {isLoading ? "↻" : "➤"}
          </button>
        </div>
      </form>
    </div>
  );
};
