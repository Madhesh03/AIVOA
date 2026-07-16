import React, { useState, useEffect } from "react";
import { useSearchHcpsQuery } from "@/features/hcps/hcpsApi";
import { HCP } from "@/types/domain";
import "./HCPAutocomplete.css";

interface HCPAutocompleteProps {
  value: string;
  onChange: (hcp: HCP) => void;
  onInputChange?: (input: string) => void;
  error?: string;
  label?: string;
}

export const HCPAutocomplete: React.FC<HCPAutocompleteProps> = ({
  value,
  onChange,
  onInputChange,
  error,
  label,
}) => {
  const [input, setInput] = useState(value);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { data: searchResults, isLoading } = useSearchHcpsQuery(
    { q: input, limit: 5 },
    { skip: input.length < 2 }
  );

  // Keep the visible input in sync when the value is set externally
  // (e.g. AI prefill or loading an interaction for edit).
  useEffect(() => {
    setInput(value);
  }, [value]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInput(newValue);
    onInputChange?.(newValue);
    setShowSuggestions(true);
  };

  const handleSelectHcp = (hcp: HCP) => {
    setInput(hcp.name);
    onChange(hcp);
    setShowSuggestions(false);
  };

  return (
    <div className="hcp-autocomplete">
      {label && <label className="hcp-autocomplete-label">{label}</label>}
      <div className="hcp-autocomplete-input-wrapper">
        <input
          className={`hcp-autocomplete-input ${error ? "hcp-autocomplete-error" : ""}`}
          type="text"
          value={input}
          onChange={handleInputChange}
          onFocus={() => setShowSuggestions(true)}
          placeholder="Search healthcare professionals..."
        />
        {isLoading && <span className="hcp-autocomplete-spinner">⟳</span>}
      </div>
      {error && <span className="hcp-autocomplete-error-text">{error}</span>}
      {showSuggestions && input.length >= 2 && searchResults && (
        <div className="hcp-autocomplete-suggestions">
          {searchResults.items.length > 0 ? (
            searchResults.items.map((hcp) => (
              <button
                key={hcp.id}
                className="hcp-autocomplete-suggestion-item"
                onClick={() => handleSelectHcp(hcp)}
                type="button"
              >
                <div className="hcp-autocomplete-suggestion-name">{hcp.name}</div>
                {hcp.specialty && (
                  <div className="hcp-autocomplete-suggestion-specialty">{hcp.specialty}</div>
                )}
              </button>
            ))
          ) : (
            <div className="hcp-autocomplete-no-results">No healthcare professionals found</div>
          )}
        </div>
      )}
    </div>
  );
};
