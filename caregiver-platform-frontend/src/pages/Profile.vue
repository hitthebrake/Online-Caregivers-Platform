<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "../api/axios";
import MemberProfile from "./MemberProfile.vue";
import CaregiverProfile from "./CaregiverProfile.vue";
import { useRouter } from "vue-router";

const loading = ref(true);
const error = ref<string | null>(null);
const user = ref<any | null>(null);
const router = useRouter();

onMounted(async () => {
  try {
    const resp = await api.get("user/me");
    user.value = resp.data;
  } catch (err: any) {
    // if unauthorized -> redirect to login
    console.error(err);
    const msg = err?.response?.data || err?.message || "Failed to fetch user";
    error.value = JSON.stringify(msg);
    // optionally redirect to login if 401
    if (err?.response?.status === 401) router.push("/login");
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="profile-redirect">
    <div v-if="loading">Loading profile…</div>
    <div v-else-if="error">
      <p>Error: {{ error }}</p>
      <router-link to="/login">Back to login</router-link>
    </div>
    <div v-else-if="user">
      <h2>{{ user.given_name }} {{ user.surname }} — {{ user.user_type }}</h2>

      <div v-if="user.user_type === 'member'">
        <MemberProfile :user="user" />
      </div>

      <div v-else>
        <CaregiverProfile :user="user" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-redirect {
  max-width: 880px;
  margin: 32px auto;
  padding: 24px 22px;
  border-radius: 20px;
  background: radial-gradient(circle at top left, #e0f2fe, #f9fafb);
  border: 1px solid rgba(148, 163, 184, 0.45);
  box-shadow: 0 26px 70px rgba(15, 23, 42, 0.14);
}

.profile-redirect h2 {
  margin-bottom: 18px;
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
}

.profile-redirect p {
  margin: 4px 0;
  color: #4b5563;
}

.profile-redirect a {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
}

.profile-redirect a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .profile-redirect {
    margin: 20px 12px;
    padding: 18px 16px;
  }
}
</style>

