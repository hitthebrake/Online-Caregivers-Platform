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
.caregiver-profile { max-width:720px; margin:12px auto; padding:8px; }
label { display:block; margin-top:8px; font-weight:600; }
input, select { width:100%; padding:8px; margin-top:4px; box-sizing:border-box; }
button { margin-top:10px; padding:8px 12px; }
</style>
