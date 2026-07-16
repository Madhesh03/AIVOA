import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// VITE_API_URL is the backend origin (e.g. http://localhost:8000); the REST
// API is always mounted under /api. Keep this the single source of truth so the
// RTK Query base and the SSE chat client (assistantApi) resolve to the same host.
export const API_ORIGIN = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiSlice = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_ORIGIN}/api`,
    prepareHeaders: (headers) => {
      headers.set("Content-Type", "application/json");
      return headers;
    },
  }),
  tagTypes: ["HCP", "Interaction"],
  endpoints: () => ({}),
});
