import { useAuthStore } from "../stores/auth.js"; // <-- ADD THIS
import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

// Use dynamic imports for better code splitting
const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: () => import("../pages/LoginPage.vue") },
  { path: "/signup/caregiver", component: () => import("../pages/SignupCaregiver.vue") },
  { path: "/signup/member", component: () => import("../pages/SignupMember.vue") },
  { path: "/profile", component: () => import("../pages/Profile.vue") },
  { path: "/jobs", component: () => import("../pages/JobsPage.vue") },
  { path: "/job-applications", component: () => import("../pages/JobApplicationsPage.vue") },
  { path: "/appointments", component: () => import("../pages/AppointmentsPage.vue") },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const auth = useAuthStore();
  auth.loadAuth(); // load data from localStorage if not loaded

  // If user goes to /login but is already logged in → redirect to profile
  if (to.path === "/login" && auth.access_token) {
    return next("/profile");
  }

  next();
});

export default router ;