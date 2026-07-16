import { z } from "zod";
import { InteractionType, Channel, Sentiment } from "@/types/domain";

export const followUpActionSchema = z.object({
  action: z.string().min(1, "Action is required"),
  due_date: z.string().optional(),
  priority: z.enum(["low", "medium", "high"]),
  done: z.boolean().default(false),
});

export const interactionFormSchema = z.object({
  hcp_id: z.string().uuid("Invalid HCP selected"),
  interaction_type: z.nativeEnum(InteractionType, {
    errorMap: () => ({ message: "Interaction type is required" }),
  }),
  channel: z.nativeEnum(Channel, {
    errorMap: () => ({ message: "Channel is required" }),
  }),
  // Accepts either a full ISO string or the `datetime-local` input format
  // (YYYY-MM-DDTHH:mm). Validated by parseability rather than strict ISO so the
  // native picker value passes.
  interaction_date: z
    .string()
    .min(1, "Date is required")
    .refine((v) => !Number.isNaN(Date.parse(v)), "Invalid date"),
  subject: z.string().min(1, "Subject is required").max(500),
  notes: z.string().optional(),
  sentiment: z
    .string()
    .transform((val) => (val === "" ? undefined : val))
    .pipe(z.nativeEnum(Sentiment).optional()),
  products: z.array(z.string()).optional().default([]),
  follow_up_actions: z.array(followUpActionSchema).optional().default([]),
});

export type InteractionFormData = z.infer<typeof interactionFormSchema>;
