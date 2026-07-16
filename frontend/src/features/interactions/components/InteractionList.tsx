import React, { useState } from "react";
import { useListInteractionsQuery } from "../interactionsApi";
import { Interaction, Source } from "@/types/domain";
import { Card } from "@/components/Card";
import { Button } from "@/components/Button";
import "./InteractionList.css";

interface InteractionListProps {
  onSelectInteraction?: (interaction: Interaction) => void;
}

export const InteractionList: React.FC<InteractionListProps> = ({ onSelectInteraction }) => {
  const [skip, setSkip] = useState(0);
  const limit = 10;
  const { data, isLoading, error } = useListInteractionsQuery({ skip, limit });

  const handlePrevious = () => {
    setSkip(Math.max(0, skip - limit));
  };

  const handleNext = () => {
    if (data && skip + limit < data.total) {
      setSkip(skip + limit);
    }
  };

  if (isLoading) {
    return (
      <div className="interaction-list">
        <div className="interaction-list-header">
          <h3 className="interaction-list-title">Recent Interactions</h3>
        </div>
        <div className="interaction-list-items">
          {Array.from({ length: 3 }).map((_, idx) => (
            <div key={idx} className="skeleton" style={{ height: 84, marginBottom: 12 }} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="interaction-list-error">
        <span aria-hidden>⚠️</span> Failed to load interactions. Is the backend running?
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="interaction-list-empty">
        <div style={{ fontSize: 28, marginBottom: 8 }} aria-hidden>
          🗒️
        </div>
        No interactions logged yet. Use the form or the AI assistant to add one.
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case "positive":
        return "sentiment-positive";
      case "negative":
        return "sentiment-negative";
      default:
        return "sentiment-neutral";
    }
  };

  return (
    <div className="interaction-list">
      <div className="interaction-list-header">
        <h3 className="interaction-list-title">Recent Interactions</h3>
        <div className="interaction-list-pagination">
          <Button
            variant="ghost"
            size="small"
            onClick={handlePrevious}
            disabled={skip === 0}
          >
            ← Previous
          </Button>
          <span className="interaction-list-page-info">
            {Math.floor(skip / limit) + 1} / {Math.ceil(data.total / limit)}
          </span>
          <Button
            variant="ghost"
            size="small"
            onClick={handleNext}
            disabled={skip + limit >= data.total}
          >
            Next →
          </Button>
        </div>
      </div>

      <div className="interaction-list-items">
        {data.items.map((interaction) => (
          <Card
            key={interaction.id}
            clickable
            onClick={() => onSelectInteraction?.(interaction)}
            className="interaction-list-item"
          >
            <div className="interaction-list-item-header">
              <div className="interaction-list-item-info">
                <div className="interaction-list-item-subject">{interaction.subject}</div>
                <div className="interaction-list-item-meta">
                  <span className="meta-badge meta-type">{interaction.interaction_type}</span>
                  <span className="meta-badge meta-channel">{interaction.channel}</span>
                  <span className={`meta-badge meta-sentiment ${getSentimentColor(interaction.sentiment)}`}>
                    {interaction.sentiment || "unset"}
                  </span>
                </div>
              </div>
              <div className="interaction-list-item-status">
                <span className={`status-badge status-${interaction.status}`}>
                  {interaction.status}
                </span>
                {interaction.source === Source.AI_ASSISTANT && (
                  <span className="source-badge">✨ AI</span>
                )}
              </div>
            </div>
            {interaction.notes && (
              <p className="interaction-list-item-notes">{interaction.notes.substring(0, 100)}...</p>
            )}
            {interaction.products && interaction.products.length > 0 && (
              <div className="interaction-list-item-products">
                {interaction.products.map((product, idx) => (
                  <span key={idx} className="product-tag">
                    {product}
                  </span>
                ))}
              </div>
            )}
            <div className="interaction-list-item-footer">
              <span className="interaction-list-item-date">
                {formatDate(interaction.interaction_date)}
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
