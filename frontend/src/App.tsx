import { useEffect, useState } from "react";
import { Provider } from "react-redux";
import { store } from "@/app/store";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import { clearToast } from "@/features/ui/uiSlice";
import { InteractionForm } from "@/features/interactions/components/InteractionForm";
import { InteractionList } from "@/features/interactions/components/InteractionList";
import { ChatPanel } from "@/features/assistant/components/ChatPanel";
import { Modal } from "@/components/Modal";
import "./App.css";

function AppContent() {
  const dispatch = useAppDispatch();
  const toast = useAppSelector((state) => state.ui.toast);
  const [showInteractions, setShowInteractions] = useState(true);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        dispatch(clearToast());
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toast, dispatch]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-left">
          <h1 className="app-title">HCP Interactions</h1>
          <p className="app-subtitle">AI-First CRM Module</p>
        </div>
        <div className="app-header-right">
          <button
            onClick={() => setShowInteractions(true)}
            style={{
              padding: "var(--spacing-sm) var(--spacing-md)",
              backgroundColor: "var(--color-primary)",
              color: "white",
              border: "none",
              borderRadius: "var(--border-radius-md)",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
              marginRight: "var(--spacing-lg)",
            }}
          >
            📋 Recent
          </button>
          <div className="app-status">
            <span className="status-dot"></span>
            <span className="status-text">Connected</span>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="app-container">
          <div className="split-view">
            <div className="split-view-left">
              <InteractionForm />
            </div>

            <div className="split-view-divider"></div>

            <div className="split-view-right">
              <ChatPanel />
            </div>
          </div>

          <Modal
            isOpen={showInteractions}
            onClose={() => setShowInteractions(false)}
            title="Recent Interactions"
          >
            <InteractionList />
          </Modal>
        </div>
      </main>

      {toast && (
        <div className={`app-toast app-toast-${toast.type}`}>
          <span className="app-toast-message">{toast.message}</span>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}
