import React from "react";
import "./Select.css";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options: SelectOption[];
  fullWidth?: boolean;
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  helperText,
  options,
  fullWidth = true,
  ...props
}) => {
  return (
    <div className={`select-field ${fullWidth ? "select-field-full-width" : ""}`}>
      {label && <label className="select-field-label">{label}</label>}
      <select className={`select-field-input ${error ? "select-field-error" : ""}`} {...props}>
        <option value="">Select...</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {(error || helperText) && (
        <span className={`select-field-helper ${error ? "select-field-helper-error" : ""}`}>
          {error || helperText}
        </span>
      )}
    </div>
  );
};
