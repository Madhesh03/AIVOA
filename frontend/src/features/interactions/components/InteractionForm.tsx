import React, { useEffect, useMemo, useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { InteractionType, Channel, HCP, Sentiment, InteractionDraft } from "@/types/domain";
import {
  useCreateInteractionMutation,
  useUpdateInteractionMutation,
  useConfirmInteractionMutation,
} from "../interactionsApi";
import { useAppDispatch, useAppSelector } from "@/app/hooks";
import { resetFormDraft, setLastSavedId } from "../interactionsSlice";
import { showToast } from "@/features/ui/uiSlice";
import { Button } from "@/components/Button";
import { TextField } from "@/components/TextField";
import { Select } from "@/components/Select";
import { HCPAutocomplete } from "@/components/HCPAutocomplete";
import { interactionFormSchema, InteractionFormData } from "../validation";
import "./InteractionForm.css";

interface InteractionFormProps {
  onSuccess?: () => void;
}

// Convert an arbitrary ISO/date string into the value a <input type="datetime-local">
// expects (YYYY-MM-DDTHH:mm) in the viewer's local time.
const toDatetimeLocal = (value?: string): string => {
  const date = value ? new Date(value) : new Date();
  const parsed = Number.isNaN(date.getTime()) ? new Date() : date;
  const tzOffsetMs = parsed.getTimezoneOffset() * 60000;
  return new Date(parsed.getTime() - tzOffsetMs).toISOString().slice(0, 16);
};

const buildDefaults = (draft: InteractionDraft): InteractionFormData => ({
  hcp_id: draft.hcp_id || "",
  interaction_type: draft.interaction_type || InteractionType.MEETING,
  channel: draft.channel || Channel.IN_PERSON,
  interaction_date: toDatetimeLocal(draft.interaction_date),
  subject: draft.subject || "",
  notes: draft.notes || "",
  sentiment: draft.sentiment,
  products: draft.products || [],
  follow_up_actions: draft.follow_up_actions || [],
});

export const InteractionForm: React.FC<InteractionFormProps> = ({ onSuccess }) => {
  const dispatch = useAppDispatch();
  const formDraft = useAppSelector((state) => state.interactions.formDraft);
  const editingId = useAppSelector((state) => state.interactions.editingId);
  const aiDraftId = useAppSelector((state) => state.interactions.aiDraftId);
  const draftOrigin = useAppSelector((state) => state.interactions.draftOrigin);

  const [selectedHcp, setSelectedHcp] = useState<HCP | null>(null);
  const [createInteraction, { isLoading: isCreating }] = useCreateInteractionMutation();
  const [updateInteraction, { isLoading: isUpdating }] = useUpdateInteractionMutation();
  const [confirmInteraction, { isLoading: isConfirming }] = useConfirmInteractionMutation();

  const isSaving = isCreating || isUpdating || isConfirming;

  const defaultValues = useMemo(() => buildDefaults(formDraft), [formDraft]);

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<InteractionFormData>({
    resolver: zodResolver(interactionFormSchema),
    defaultValues,
  });

  // Reactively repopulate the form whenever the shared draft changes — this is
  // what lets the AI assistant fill the form from a chat message.
  useEffect(() => {
    reset(buildDefaults(formDraft));
  }, [formDraft, reset]);

  const onSubmit = async (data: InteractionFormData) => {
    // A record the AI already persisted (aiDraftId) or one being edited is
    // updated in place; a brand-new manual entry is created. Either way we then
    // confirm it so form submissions land as `logged`, never a stray duplicate.
    const targetId = editingId ?? aiDraftId;
    const payload = {
      interaction_type: data.interaction_type,
      channel: data.channel,
      interaction_date: new Date(data.interaction_date).toISOString(),
      subject: data.subject,
      notes: data.notes,
      sentiment: data.sentiment,
      products: data.products,
      follow_up_actions: data.follow_up_actions,
    };

    try {
      let savedId: string;
      if (targetId) {
        await updateInteraction({ id: targetId, data: payload }).unwrap();
        savedId = targetId;
      } else {
        const result = await createInteraction({
          ...payload,
          hcp_id: data.hcp_id,
          user_id: "user_123",
        }).unwrap();
        savedId = result.id;
      }

      await confirmInteraction(savedId).unwrap();
      dispatch(setLastSavedId(savedId));
      dispatch(
        showToast({
          type: "success",
          message: editingId ? "Interaction updated" : "Interaction logged",
        })
      );
      dispatch(resetFormDraft());
      setSelectedHcp(null);
      reset(buildDefaults({}));
      onSuccess?.();
    } catch (error: any) {
      dispatch(
        showToast({
          type: "error",
          message: error?.data?.detail || "Failed to save interaction",
        })
      );
    }
  };

  const handleClear = () => {
    dispatch(resetFormDraft());
    setSelectedHcp(null);
    reset(buildDefaults({}));
    dispatch(showToast({ type: "info", message: "Form cleared" }));
  };

  return (
    <form className="interaction-form" onSubmit={handleSubmit(onSubmit)}>
      <div className="interaction-form-header">
        <h2 className="interaction-form-title">
          {editingId ? "Edit Interaction" : "Log Interaction"}
        </h2>
        <span className={`interaction-form-badge ${draftOrigin === "ai" ? "badge-ai" : ""}`}>
          {draftOrigin === "ai" ? "✨ AI-filled" : "● draft"}
        </span>
      </div>

      <div className="interaction-form-group">
        <HCPAutocomplete
          value={selectedHcp?.name || formDraft.hcp_name || ""}
          onChange={(hcp) => {
            setSelectedHcp(hcp);
            setValue("hcp_id", hcp.id, { shouldValidate: true });
          }}
          label="Healthcare Professional"
          error={errors.hcp_id?.message}
        />
      </div>

      <div className="interaction-form-row">
        <div className="interaction-form-col">
          <Controller
            name="interaction_type"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="Interaction Type"
                options={[
                  { value: InteractionType.MEETING, label: "Meeting" },
                  { value: InteractionType.CALL, label: "Call" },
                  { value: InteractionType.EMAIL, label: "Email" },
                  { value: InteractionType.CONFERENCE, label: "Conference" },
                  { value: InteractionType.SAMPLE_DROP, label: "Sample Drop" },
                ]}
                error={errors.interaction_type?.message}
              />
            )}
          />
        </div>

        <div className="interaction-form-col">
          <Controller
            name="channel"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="Channel"
                options={[
                  { value: Channel.IN_PERSON, label: "In-person" },
                  { value: Channel.PHONE, label: "Phone" },
                  { value: Channel.VIDEO, label: "Video" },
                  { value: Channel.EMAIL, label: "Email" },
                ]}
                error={errors.channel?.message}
              />
            )}
          />
        </div>
      </div>

      <div className="interaction-form-row">
        <div className="interaction-form-col">
          <Controller
            name="interaction_date"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Date"
                type="datetime-local"
                error={errors.interaction_date?.message}
              />
            )}
          />
        </div>
      </div>

      <div className="interaction-form-group">
        <Controller
          name="subject"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Subject"
              placeholder="Brief description of the interaction"
              error={errors.subject?.message}
            />
          )}
        />
      </div>

      <div className="interaction-form-group">
        <Controller
          name="notes"
          control={control}
          render={({ field }) => (
            <TextField
              {...field}
              label="Notes"
              multiline
              rows={4}
              placeholder="Detailed notes about the interaction..."
              error={errors.notes?.message}
            />
          )}
        />
      </div>

      <div className="interaction-form-row">
        <div className="interaction-form-col">
          <Controller
            name="sentiment"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                label="Sentiment"
                options={[
                  { value: Sentiment.POSITIVE, label: "Positive" },
                  { value: Sentiment.NEUTRAL, label: "Neutral" },
                  { value: Sentiment.NEGATIVE, label: "Negative" },
                ]}
                error={errors.sentiment?.message}
              />
            )}
          />
        </div>

        <div className="interaction-form-col">
          <Controller
            name="products"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Products (comma-separated)"
                placeholder="e.g., Product-A, Product-B"
                value={Array.isArray(field.value) ? field.value.join(", ") : ""}
                onChange={(e) =>
                  field.onChange(
                    e.target.value
                      .split(",")
                      .map((p) => p.trim())
                      .filter(Boolean)
                  )
                }
                error={errors.products?.message}
              />
            )}
          />
        </div>
      </div>

      <div className="interaction-form-actions">
        <Button
          type="button"
          variant="secondary"
          onClick={handleClear}
          disabled={isSaving}
        >
          Clear
        </Button>
        <Button type="submit" loading={isSaving}>
          {editingId ? "Update Interaction" : "Confirm & Log"}
        </Button>
      </div>
    </form>
  );
};
