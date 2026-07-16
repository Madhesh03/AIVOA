import { apiSlice } from "@/api/apiSlice";
import { HCP } from "@/types/domain";

interface ListResponse<T> {
  total: number;
  limit: number;
  offset: number;
  items: T[];
}

interface HcpCreateRequest {
  name: string;
  specialty?: string;
  organization?: string;
  email?: string;
  phone?: string;
  notes?: string;
}

interface HcpUpdateRequest {
  name?: string;
  specialty?: string;
  organization?: string;
  email?: string;
  phone?: string;
  notes?: string;
}

export const hcpsApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    listHcps: builder.query<ListResponse<HCP>, { skip?: number; limit?: number }>({
      query: ({ skip = 0, limit = 10 }) => ({
        url: "/hcps",
        params: { skip, limit },
      }),
      providesTags: ["HCP"],
    }),

    getHcp: builder.query<HCP, string>({
      query: (id) => `/hcps/${id}`,
      providesTags: (_result, _error, id) => [{ type: "HCP", id }],
    }),

    searchHcps: builder.query<ListResponse<HCP>, { q: string; skip?: number; limit?: number }>({
      query: ({ q, skip = 0, limit = 10 }) => ({
        url: "/hcps/search",
        params: { q, skip, limit },
      }),
      providesTags: ["HCP"],
    }),

    createHcp: builder.mutation<HCP, HcpCreateRequest>({
      query: (body) => ({
        url: "/hcps",
        method: "POST",
        body,
      }),
      invalidatesTags: ["HCP"],
    }),

    updateHcp: builder.mutation<HCP, { id: string; data: HcpUpdateRequest }>({
      query: ({ id, data }) => ({
        url: `/hcps/${id}`,
        method: "PATCH",
        body: data,
      }),
      invalidatesTags: (_result, _error, { id }) => [{ type: "HCP", id }],
    }),

    deleteHcp: builder.mutation<void, string>({
      query: (id) => ({
        url: `/hcps/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["HCP"],
    }),
  }),
});

export const {
  useListHcpsQuery,
  useGetHcpQuery,
  useSearchHcpsQuery,
  useCreateHcpMutation,
  useUpdateHcpMutation,
  useDeleteHcpMutation,
} = hcpsApi;
