import React from "react";
import "./TextField.css";

type CommonProps = {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  multiline?: boolean;
  rows?: number;
};

type TextFieldProps = CommonProps &
  Omit<React.InputHTMLAttributes<HTMLInputElement>, keyof CommonProps> &
  Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, keyof CommonProps>;

export const TextField: React.FC<TextFieldProps> = ({
  label,
  error,
  helperText,
  fullWidth = true,
  multiline = false,
  rows = 3,
  ...props
}) => {
  const inputClassName = `text-field-input ${error ? "text-field-error" : ""}`;

  return (
    <div className={`text-field ${fullWidth ? "text-field-full-width" : ""}`}>
      {label && <label className="text-field-label">{label}</label>}
      {multiline ? (
        <textarea
          className={inputClassName}
          rows={rows}
          {...(props as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
        />
      ) : (
        <input
          className={inputClassName}
          {...(props as React.InputHTMLAttributes<HTMLInputElement>)}
        />
      )}
      {(error || helperText) && (
        <span className={`text-field-helper ${error ? "text-field-helper-error" : ""}`}>
          {error || helperText}
        </span>
      )}
    </div>
  );
};
