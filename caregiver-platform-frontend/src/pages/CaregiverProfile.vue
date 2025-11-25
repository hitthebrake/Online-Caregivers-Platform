<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "../api/axios";

const props = defineProps<{ user: any }>();

const loading = ref(false);
const caregiverData = ref({
  photo: "",
  gender: "",
  caregiving_type: "babysitter",
  hourly_rate: 0,
  caregiver_user_id: props.user.user_id,
});

async function loadCaregiver() {
  loading.value = true;
  try {
    const r = await api.get("caregivers/my_caregiver_data");
    Object.assign(caregiverData.value, r.data);
  } catch (e: any) {
    console.error("loadCaregiver", e);
    alert("Failed to load caregiver data: " + JSON.stringify(e?.response?.data || e.message));
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadCaregiver();
});

async function updateCaregiver() {
  loading.value = true;
  try {
    const payload = {
      ...caregiverData.value,
      caregiver_user_id: props.user.user_id,
    };
    await api.put("caregivers/my_caregiver_data", payload);
    alert("Caregiver data updated");
  } catch (e: any) {
    console.error("updateCaregiver", e);
    alert("Update failed: " + JSON.stringify(e?.response?.data || e.message));
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="caregiver-profile">
    <h3>Basic info</h3>
    <div>
      <p><strong>Email:</strong> {{ props.user.email }}</p>
      <p><strong>Name:</strong> {{ props.user.given_name }} {{ props.user.surname }}</p>
      <p><strong>City:</strong> {{ props.user.city }}</p>
      <p><strong>Phone:</strong> {{ props.user.phone_number }}</p>
      <p><strong>About:</strong> {{ props.user.profile_description }}</p>
    </div>

    <hr />

    <h3>Caregiver data</h3>
    <div>
      <label>Photo (URL)</label>
      <input v-model="caregiverData.photo" />

      <label>Gender</label>
      <input v-model="caregiverData.gender" />

      <label>Caregiving type</label>
      <select v-model="caregiverData.caregiving_type">
        <option value="babysitter">babysitter</option>
        <option value="caregiver for elderly">caregiver for elderly</option>
        <option value="playmate for children">playmate for children</option>
      </select>

      <label>Hourly rate</label>
      <input type="number" v-model.number="caregiverData.hourly_rate" />

      <button @click="updateCaregiver">Update caregiver data</button>
    </div>
  </div>
</template>

<style scoped>
.caregiver-profile {
  max-width: 780px;
  margin: 24px auto;
  padding: 20px 18px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16);
}

.caregiver-profile h3 {
  margin-top: 6px;
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.caregiver-profile p {
  margin: 3px 0;
  color: #4b5563;
}

.caregiver-profile hr {
  margin: 16px 0;
  border: none;
  border-top: 1px dashed #e2e8f0;
}

.caregiver-profile form,
.caregiver-profile div {
  width: 100%;
}

.caregiver-profile label {
  display: block;
  margin-top: 10px;
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 13px;
  color: #475569;
}

.caregiver-profile input,
.caregiver-profile select,
.caregiver-profile textarea {
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

.caregiver-profile input:focus,
.caregiver-profile select:focus,
.caregiver-profile textarea:focus {
  border-color: #2563eb;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.caregiver-profile button {
  margin-top: 14px;
  border: none;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.12s ease, transform 0.07s ease, box-shadow 0.12s ease,
    opacity 0.15s ease;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.35);
}

.caregiver-profile button:hover:not(:disabled) {
  background-color: #1d4ed8;
  transform: translateY(-1px);
}

.caregiver-profile button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 6px 12px rgba(37, 99, 235, 0.35);
}

.caregiver-profile button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}
</style>

