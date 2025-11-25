import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../pages/LoginPage.vue";
import SignupMember from "../pages/SignupMember.vue";
import SignupCaregiver from "../pages/SignupCaregiver.vue";
import Profile from "../pages/Profile.vue";
import JobsPage from "../pages/JobsPage.vue";
import JobApplicationsPage from "../pages/JobApplicationsPage.vue";
import AppointmentsPage from "../pages/AppointmentsPage.vue";
import { useAuthStore } from "../stores/auth"; // <-- ADD THIS

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginPage },
  { path: "/signup/caregiver", component: SignupCaregiver },
  { path: "/signup/member", component: SignupMember },
  { path: "/profile", component: Profile },
    { path: "/jobs", component: JobsPage },
    { path: "/job-applications", component: JobApplicationsPage },
    { path: "/appointments", component: AppointmentsPage },

];

export const router = createRouter({
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
