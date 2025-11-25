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
  padding: 10px 18px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.35);
  background: linear-gradient(135deg, #0f172a, #111827);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.brand {
  font-weight: 800;
  font-size: 20px;
  letter-spacing: 0.03em;
  color: #e5e7eb;
  text-decoration: none;
}

.brand:hover {
  color: #ffffff;
}

.nav-tabs {
  display: flex;
  align-items: center;
  gap: 6px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-tabs li {
  margin: 0;
}

.tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-decoration: none;
  color: #e5e7eb;
  background: transparent;
  border: 1px solid transparent;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease,
    transform 0.07s ease, box-shadow 0.12s ease;
}

.tab:hover {
  background: rgba(31, 41, 55, 0.9);
  border-color: rgba(148, 163, 184, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.5);
}

.tab.active {
  background: #f97316;
  color: #111827;
  border-color: #fed7aa;
  box-shadow: 0 10px 24px rgba(248, 113, 113, 0.45);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logout-btn {
  border: none;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  background: #f97316;
  color: #111827;
  cursor: pointer;
  transition: background-color 0.15s ease, transform 0.07s ease, box-shadow 0.12s ease,
    opacity 0.15s ease;
  box-shadow: 0 10px 24px rgba(248, 113, 113, 0.45);
}

.logout-btn:hover:not(:disabled) {
  background: #ea580c;
  transform: translateY(-1px);
}

.logout-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 6px 12px rgba(248, 113, 113, 0.4);
}

.logout-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.nav-guest .tab {
  margin-left: 6px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.6);
  background: rgba(31, 41, 55, 0.8);
}

.nav-guest .tab:hover {
  background: rgba(55, 65, 81, 0.9);
}

@media (max-width: 700px) {
  .nav {
    padding-inline: 12px;
  }

  .nav-tabs {
    display: none;
  }
}
</style>
