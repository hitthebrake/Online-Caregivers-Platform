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
/* minimal styles */
.profile-redirect { max-width: 800px; margin: 20px auto; padding: 12px; }
</style>
