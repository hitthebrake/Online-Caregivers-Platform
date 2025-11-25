<template>
  <nav class="nav">
    <div class="nav-left">
      <router-link to="/profile" class="brand">CarePlatform</router-link>
    </div>

    <ul class="nav-tabs" v-if="isLoggedIn">
      <li>
        <RouterLink to="/profile" class="tab" :class="{ active: isActive('/profile') }">Profile</RouterLink>
      </li>
      <li>
        <RouterLink to="/jobs" class="tab" :class="{ active: isActive('/jobs') }">Jobs</RouterLink>
      </li>
      <li>
        <RouterLink to="/job-applications" class="tab" :class="{ active: isActive('/job-applications') }">Job Applications</RouterLink>
      </li>
      <li>
        <RouterLink to="/appointments" class="tab" :class="{ active: isActive('/appointments') }">Appointments</RouterLink>
      </li>
    </ul>

    <div class="nav-right" v-if="isLoggedIn">
      <span class="user-type">{{ userLabel }}</span>
      <button class="logout-btn" @click="onLogout" :disabled="loggingOut">
        {{ loggingOut ? 'Logging out...' : 'Logout' }}
      </button>
    </div>

    <div class="nav-guest" v-else>
      <RouterLink to="/login" class="tab">Login</RouterLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../api/axios";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const loggingOut = ref(false);

const isLoggedIn = computed(() => !!auth.access_token);

const userLabel = computed(() => {
  if (!auth.user_type) return "";
  return `${auth.user_type === "member" ? "Member" : auth.user_type === "caregiver" ? "Caregiver" : auth.user_type}`;
});

function isActive(path: string) {
  // simple startsWith check so nested routes still highlight parent
  return route.path === path || route.path.startsWith(path + "/");
}

async function onLogout() {
  loggingOut.value = true;
  try {
    // clear auth store (this should remove localStorage inside your store)
    auth.logout();

    // also clear axios default Authorization if you set it
    try {
      // remove auth header so new requests won't include old token
      delete (api.defaults.headers as any).Authorization;
    } catch (e) {
      // ignore
    }

    // redirect to login
    await router.push("/login");
  } catch (err) {
    console.error("Logout error", err);
  } finally {
    loggingOut.value = false;
  }
}
</script>

<style scoped>
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid #e6e6e6;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  font-weight: 700;
  font-size: 1.1rem;
  text-decoration: none;
  color: inherit;
}

.nav-tabs {
  display: flex;
  list-style: none;
  gap: 8px;
  padding: 0;
  margin: 0;
  align-items: center;
}

.tab {
  padding: 8px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  font-weight: 500;
}

.tab:hover { background: rgba(0,0,0,0.03); }

.tab.active {
  background: rgba(0, 120, 212, 0.12);
  color: #0078d4;
  box-shadow: 0 1px 0 rgba(0,0,0,0.04);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-type {
  font-size: 0.95rem;
  color: #444;
  padding-right: 8px;
}

.logout-btn {
  background: #ff5252;
  color: white;
  border: none;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.logout-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.nav-guest .tab {
  margin-left: 8px;
}
@media (max-width: 700px) {
  .nav-tabs { display: none; } /* small screens — hide tabs or implement burger later */
}
</style>
