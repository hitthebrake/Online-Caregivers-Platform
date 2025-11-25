
// src/api/axios.ts
import axios from "axios";

const api = axios.create({
  baseURL: "https://online-caregivers-platform.onrender.com/",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem("auth");
    if (raw) {
      const auth = JSON.parse(raw);
      if (auth?.access_token) {
        const tokenType = auth.token_type ?? "Bearer";
        config.headers = {
          ...config.headers,
          Authorization: `${tokenType} ${auth.access_token}`,
        };
      }
    }
  } catch (e) {
    // ignore
  }
  return config;
});

export default api;
