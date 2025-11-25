<!-- src/views/SignupMember.vue -->
<template>
  <div class="page signup-page">
    <h1>Sign up — Member</h1>
    <form @submit.prevent="submit">
      <input v-model="given_name" placeholder="Given name" required />
      <input v-model="surname" placeholder="Surname" />
      <input v-model="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <input v-model="city" placeholder="City" />
      <input v-model="phone_number" placeholder="Phone number" />
      <input v-model="house_number" placeholder="House number" />
      <input v-model="street" placeholder="Street" />
      <input v-model="town" placeholder="Town" />
      <input v-model="house_rules" placeholder="House rules" />
      <input v-model="dependent_description" placeholder="Dependent description" />
      <textarea v-model="profile_description" placeholder="Profile description"></textarea>

      <button type="submit" :disabled="loading">Sign up</button>
    </form>

    <p><router-link to="/login">Back to Login</router-link></p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api/axios";
import { useRouter } from "vue-router";

const router = useRouter();
const loading = ref(false);

const given_name = ref("");
const surname = ref("");
const email = ref("");
const password = ref("");
const city = ref("");
const phone_number = ref("");
const house_number = ref("");
const street = ref("");
const town = ref("");
const house_rules = ref("");
const dependent_description = ref("");
const profile_description = ref("");

async function submit() {
  loading.value = true;
  try {
    const body = {
      house_number: house_number.value,
      street: street.value,
      town: town.value,
      email: email.value,
      given_name: given_name.value,
      surname: surname.value,
      city: city.value,
      phone_number: phone_number.value,
      profile_description: profile_description.value,
      password: password.value,
      house_rules: house_rules.value,
      dependent_description: dependent_description.value,
    };

    const r = await api.post("members/", body);
    // If response successful, redirect to login (token/)
    alert("Signup successful. Please login.");
    router.push("/login"); // token/ corresponds to login route
  } catch (err) {
    console.error(err);
    const msg = err?.response?.data || err.message || "Signup failed";
    alert(`Signup error: ${JSON.stringify(msg)}`);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.signup-page {
  max-width: 520px;
  margin: 40px auto;
  padding: 28px 24px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.16);
}

.signup-page h1 {
  margin-bottom: 16px;
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
}

.signup-page h2 {
  margin: 10px 0 6px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.signup-page form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

.signup-page label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 3px;
}

.signup-page input,
.signup-page select,
.signup-page textarea {
  width: 100%;
  padding: 9px 10px;
  border-radius: 10px;
  border: 1px solid #d4d4d8;
  background-color: #f9fafb;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  resize: vertical;
  min-height: 40px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
}

.signup-page input:focus,
.signup-page select:focus,
.signup-page textarea:focus {
  border-color: #2563eb;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.signup-page button[type="submit"] {
  margin-top: 6px;
  border: none;
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.12s ease, transform 0.07s ease, box-shadow 0.12s ease,
    opacity 0.15s ease;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.4);
}

.signup-page button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-1px);
}

.signup-page button[type="submit"]:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 9px 20px rgba(37, 99, 235, 0.35);
}

.signup-page button[type="submit"]:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.signup-page p {
  margin-top: 10px;
  font-size: 13px;
  text-align: center;
  color: #4b5563;
}

.signup-page a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}

.signup-page a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .signup-page {
    margin: 24px 12px;
    padding: 22px 18px;
  }
}
</style>

