import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    access_token: null as string | null,
    token_type: null as string | null,
    user_type: null as string | null,
    user_id: null as number | null
  }),

  actions: {
    saveAuth(data: {
      access_token: string;
      token_type: string;
      user_type: string;
      user_id: number;
    }) {
      this.access_token = data.access_token;
      this.token_type = data.token_type;
      this.user_type = data.user_type;
      this.user_id = data.user_id;

      localStorage.setItem("auth", JSON.stringify(data));
    },

    loadAuth() {
      const saved = localStorage.getItem("auth");
      if (saved) {
        Object.assign(this, JSON.parse(saved));
      }
    },

    logout() {
      localStorage.removeItem("auth");
      this.access_token = null;
      this.token_type = null;
      this.user_type = null;
      this.user_id = null;
    }
  }
});
