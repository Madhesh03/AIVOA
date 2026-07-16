export enum InteractionType {
  MEETING = "meeting",
  CALL = "call",
  EMAIL = "email",
  CONFERENCE = "conference",
  SAMPLE_DROP = "sample_drop",
}

export enum Channel {
  IN_PERSON = "in_person",
  PHONE = "phone",
  VIDEO = "video",
  EMAIL = "email",
}

export enum Sentiment {
  POSITIVE = "positive",
  NEUTRAL = "neutral",
  NEGATIVE = "negative",
}

export enum Source {
  FORM = "form",
  AI_ASSISTANT = "ai_assistant",
}

export enum Status {
  DRAFT = "draft",
  LOGGED = "logged",
}

export interface HCP {
  id: string;
  name: string;
  specialty?: string;
  organization?: string;
  email?: string;
  phone?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface FollowUpAction {
  action: string;
  due_date?: string;
  priority: "low" | "medium" | "high";
  done: boolean;
}

export interface Interaction {
  id: string;
  hcp_id: string;
  user_id: string;
  interaction_type: InteractionType;
  channel: Channel;
  interaction_date: string;
  subject: string;
  notes?: string;
  sentiment?: Sentiment;
  products?: string[];
  follow_up_actions?: FollowUpAction[];
  ai_summary?: string;
  source: Source;
  status: Status;
  created_at: string;
  updated_at: string;
}

export interface InteractionDraft {
  hcp_id?: string;
  hcp_name?: string;
  interaction_type?: InteractionType;
  channel?: Channel;
  interaction_date?: string;
  subject?: string;
  notes?: string;
  sentiment?: Sentiment;
  products?: string[];
  follow_up_actions?: FollowUpAction[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
