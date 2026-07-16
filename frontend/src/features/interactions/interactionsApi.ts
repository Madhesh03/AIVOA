import { apiSlice } from "@/api/apiSlice";
import {
  Channel,
  FollowUpAction,
  Interaction,
  InteractionType,
  Sentiment,
} from "@/types/domain";

interface ListResponse<T> {
  total: number;
  limit: number;
  offset: number;
  items: T[];
}

interface InteractionCreateRequest {
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
}

interface InteractionUpdateRequest {
  interaction_type?: InteractionType;
  channel?: Channel;
  interaction_date?: string;
  subject?: string;
  notes?: string;
  sentiment?: Sentiment;
  products?: string[];
  follow_up_actions?: FollowUpAction[];
}

export const interactionsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listInteractions: builder.query<ListResponse<Interaction>, { skip?: number; limit?: number }>({
      query: ({ skip = 0, limit = 10 }) => ({
        url: "/interactions",
        params: { skip, limit },
      }),
      providesTags: ["Interaction"],
    }),

    getInteraction: builder.query<Interaction, string>({
      query: (id) => `/interactions/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Interaction", id }],
    }),

    listInteractionsByHcp: builder.query<
      ListResponse<Interaction>,
      { hcpId: string; skip?: number; limit?: number }
    >({
      query: ({ hcpId, skip = 0, limit = 10 }) => ({
        url: `/interactions/hcp/${hcpId}`,
        params: { skip, limit },
      }),
      providesTags: ["Interaction"],
    }),

    searchInteractions: builder.query<
      ListResponse<Interaction>,
      {
        q?: string;
        hcpId?: string;
        interactionType?: string;
        fromDate?: string;
        toDate?: string;
        skip?: number;
        limit?: number;
      }
    >({
      query: ({ q = "", hcpId, interactionType, fromDate, toDate, skip = 0, limit = 10 }) => {
        const params: Record<string, any> = { q, skip, limit };
        if (hcpId) params.hcp_id = hcpId;
        if (interactionType) params.interaction_type = interactionType;
        if (fromDate) params.from_date = fromDate;
        if (toDate) params.to_date = toDate;
        return { url: "/interactions/search", params };
      },
      providesTags: ["Interaction"],
    }),

    createInteraction: builder.mutation<Interaction, InteractionCreateRequest>({
      query: (body) => ({
        url: "/interactions",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Interaction"],
    }),

    updateInteraction: builder.mutation<Interaction, { id: string; data: InteractionUpdateRequest }>(
      {
        query: ({ id, data }) => ({
          url: `/interactions/${id}`,
          method: "PATCH",
          body: data,
        }),
        invalidatesTags: (_result, _error, { id }) => [{ type: "Interaction", id }],
      }
    ),

    confirmInteraction: builder.mutation<Interaction, string>({
      query: (id) => ({
        url: `/interactions/${id}/confirm`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, id) => [{ type: "Interaction", id }],
    }),

    deleteInteraction: builder.mutation<void, string>({
      query: (id) => ({
        url: `/interactions/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Interaction"],
    }),
  }),
});

export const {
  useListInteractionsQuery,
  useGetInteractionQuery,
  useListInteractionsByHcpQuery,
  useSearchInteractionsQuery,
  useCreateInteractionMutation,
  useUpdateInteractionMutation,
  useConfirmInteractionMutation,
  useDeleteInteractionMutation,
} = interactionsApi;
