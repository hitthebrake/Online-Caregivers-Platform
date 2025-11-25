<!-- src/views/SignupCaregiver.vue -->
<template>
  <div class="page signup-page">
    <h1>Sign up — Caregiver</h1>
    <form @submit.prevent="submit">
      <input v-model="given_name" placeholder="Given name" required />
      <input v-model="surname" placeholder="Surname" />
      <input v-model="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <input v-model="city" placeholder="City" />
      <input v-model="phone_number" placeholder="Phone number" />
      <input v-model="photo" placeholder="Photo URL" />
      <select v-model="gender">
        <option value="">Select gender</option>
        <option>male</option>
        <option>female</option>
        <option>other</option>
      </select>
      <select v-model="caregiving_type" required>
        <option value="babysitter">babysitter</option>
        <option value="caregiver for elderly">caregiver for elderly</option>
        <option value="playmate for children">playmate for children</option>
      </select>
      <input v-model.number="hourly_rate" placeholder="Hourly rate" />

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
const photo = ref("");
const gender = ref("");
const caregiving_type = ref("babysitter");
const hourly_rate = ref(0);
const profile_description = ref("");

async function submit() {
  loading.value = true;
  try {
    const body = {
      email: email.value,
      given_name: given_name.value,
      surname: surname.value,
      city: city.value,
      phone_number: phone_number.value,
      profile_description: profile_description.value,
      password: password.value,
      photo: photo.value,
      gender: gender.value,
      caregiving_type: caregiving_type.value,
      hourly_rate: hourly_rate.value,
    };

    const r = await api.post("caregivers/", body);
    alert("Signup successful. Please login.");
    router.push("/login");
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
input, textarea, select { display:block; width:100%; margin-bottom:8px; padding:8px; }
button{ padding:8px 14px; }
</style>
