// src/api/axios.ts
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import axios, { AxiosHeaders } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: "https://online-caregivers-platform.onrender.com/",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  try {
    const raw = localStorage.getItem("auth");
    if (raw) {
      const auth = JSON.parse(raw);
      if (auth?.access_token) {
        const tokenType = auth.token_type ?? "Bearer";
        
        // Create new headers object to avoid type issues
        const headers = new AxiosHeaders(config.headers);
        headers.set('Authorization', `${tokenType} ${auth.access_token}`);
        config.headers = headers;
      }
    }
  } catch (e) {
    // ignore
  }
  return config;
});

export default api;