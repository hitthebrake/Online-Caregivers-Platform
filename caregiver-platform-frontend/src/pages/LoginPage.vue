<!-- src/views/Login.vue -->
<template>
  <div class="page login-page">
    <h1>Login</h1>
    <form @submit.prevent="submit">
      <div>
        <label>Email</label>
        <input v-model="email" type="text" required />
      </div>

      <div>
        <label>Password</label>
        <input v-model="password" type="password" required />
      </div>

      <button type="submit" :disabled="loading">Login</button>
    </form>

    <p>
      No account?
      <router-link to="/signup/member">Sign up as member</router-link> |
      <router-link to="/signup/caregiver">Sign up as caregiver</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api/axios";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const email = ref("");
const password = ref("");
const loading = ref(false);

async function submit() {
  loading.value = true;
  try {
    const body = {
      email: email.value,
      password: password.value,
    };

    const r = await api.post("token/", body);
    // example response:
    // { access_token, token_type, user_type, user_id }
    const data = r.data;
    if (!data || !data.access_token) {
      alert("Login failed: invalid server response");
      loading.value = false;
      return;
    }

    auth.saveAuth(data); // saves to store + localStorage

    // redirect to a protected route — change as required
    // e.g. router.push('/dashboard')
    router.push("/profile"); // change to desired route after login
  } catch (err) {
    console.error(err);
    // show server error message if present
    const msg = err?.response?.data?.detail || err?.response?.data || err.message || "Login failed";
    alert(`Login error: ${JSON.stringify(msg)}`);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.page.login-page {
  max-width: 420px;
  margin: 72px auto;
  padding: 32px 28px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.15);
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.login-page h1 {
  margin-bottom: 20px;
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
}

.login-page form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-page form > div {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.login-page label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.login-page input {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background-color: #f8fafc;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
}

.login-page input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.18);
  background-color: #ffffff;
}

.login-page button[type="submit"] {
  margin-top: 4px;
  width: 100%;
  border: none;
  border-radius: 999px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  cursor: pointer;
  transition: transform 0.08s ease, box-shadow 0.08s ease, opacity 0.15s ease;
  box-shadow: 0 12px 25px rgba(37, 99, 235, 0.35);
}

.login-page button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 16px 30px rgba(37, 99, 235, 0.45);
}

.login-page button[type="submit"]:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.35);
}

.login-page button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

@media (max-width: 600px) {
  .page.login-page {
    margin: 40px 16px;
    padding: 24px 20px;
  }
}
</style>

