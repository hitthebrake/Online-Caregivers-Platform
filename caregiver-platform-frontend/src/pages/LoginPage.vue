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
/* minimal styles - replace with your UI framework */
.page { max-width: 420px; margin: 40px auto; padding: 20px; }
form > div { margin-bottom: 12px; }
button { padding: 8px 16px; }
</style>
