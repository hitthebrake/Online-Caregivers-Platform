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
.page { max-width: 720px; margin: 20px auto; padding: 16px; }
input, textarea { display:block; width:100%; margin-bottom:8px; padding:8px; }
button{ padding:8px 14px; }
</style>
