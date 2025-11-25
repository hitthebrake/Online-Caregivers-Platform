<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import api from "../api/axios";
import { useAuthStore } from "../stores/auth";

interface UserMe {
  user_id: number;
  email: string;
  given_name?: string;
  surname?: string;
  city?: string;
  phone_number?: string;
  profile_description?: string;
  user_type?: string;
}

const props = defineProps<{ user: UserMe }>();
const auth = useAuthStore();

const loading = ref(false);
const err = ref<string | null>(null);

// Member-specific
const memberData = ref({
  house_rules: "",
  dependent_description: "",
  member_user_id: props.user.user_id,
});

const addressData = ref({
  house_number: "",
  street: "",
  town: "",
  member_user_id: props.user.user_id,
});

const hasAddress = ref<boolean | null>(null); // null = unknown

async function loadMember() {
  loading.value = true;
  err.value = null;
  try {
    const r = await api.get("members/my_member_data");
    Object.assign(memberData.value, r.data);
  } catch (e: any) {
    console.error("loadMember", e);
    err.value = JSON.stringify(e?.response?.data || e.message || "Failed to load member data");
  } finally {
    loading.value = false;
  }
}

async function loadAddress() {
  try {
    const r = await api.get("members/my_address_data");
    if (r.status === 200 && r.data) {
      Object.assign(addressData.value, r.data);
      hasAddress.value = true;
    } else {
      hasAddress.value = false;
    }
  } catch (e: any) {
    // if 404 -> no address, else show error
    if (e?.response?.status === 404) {
      hasAddress.value = false;
      return;
    }
    console.error("loadAddress", e);
    // treat as no address if not found
    hasAddress.value = false;
  }
}

onMounted(async () => {
  // load both
  await Promise.all([loadMember(), loadAddress()]);
});

async function updateMember() {
  loading.value = true;
  try {
    const payload = {
      ...memberData.value,
      member_user_id: props.user.user_id,
    };
    await api.put("members/my_member_data", payload);
    alert("Member data updated successfully");
  } catch (e: any) {
    console.error("updateMember", e);
    alert("Update member failed: " + JSON.stringify(e?.response?.data || e.message));
  } finally {
    loading.value = false;
  }
}

async function updateAddress() {
  loading.value = true;
  try {
    const payload = {
      ...addressData.value,
      member_user_id: props.user.user_id,
    };
    if (hasAddress.value) {
      await api.put("members/my_address_data", payload);
      alert("Address updated successfully");
    } else {
      // try POST when address doesn't exist
      await api.post("members/my_address_data", payload);
      hasAddress.value = true;
      alert("Address created successfully");
    }
  } catch (e: any) {
    console.error("updateAddress", e);
    alert("Update address failed: " + JSON.stringify(e?.response?.data || e.message));
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="member-profile">
    <h3>Basic info</h3>
    <div>
      <p><strong>Email:</strong> {{ props.user.email }}</p>
      <p><strong>Name:</strong> {{ props.user.given_name }} {{ props.user.surname }}</p>
      <p><strong>City:</strong> {{ props.user.city }}</p>
      <p><strong>Phone:</strong> {{ props.user.phone_number }}</p>
      <p><strong>About:</strong> {{ props.user.profile_description }}</p>
    </div>

    <hr />

    <h3>Member data</h3>
    <div>
      <label>House rules</label>
      <textarea v-model="memberData.house_rules" rows="3"></textarea>

      <label>Dependent description</label>
      <textarea v-model="memberData.dependent_description" rows="3"></textarea>

      <button @click="updateMember">Update member data</button>
    </div>

    <hr />

    <h3>Address</h3>
    <div>
      <label>House number</label>
      <input v-model="addressData.house_number" />

      <label>Street</label>
      <input v-model="addressData.street" />

      <label>Town</label>
      <input v-model="addressData.town" />

      <div style="margin-top:8px">
        <button @click="updateAddress">
          {{ hasAddress ? "Update address" : "Create address" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.member-profile {
  max-width: 780px;
  margin: 24px auto;
  padding: 20px 18px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid rgba(148, 163, 184, 0.4);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16);
}

.member-profile h3 {
  margin-top: 6px;
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.member-profile p {
  margin: 3px 0;
  color: #4b5563;
}

.member-profile hr {
  margin: 16px 0;
  border: none;
  border-top: 1px dashed #e2e8f0;
}

.member-profile label {
  display: block;
  margin-top: 10px;
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 13px;
  color: #475569;
}

.member-profile input,
.member-profile textarea {
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

.member-profile input:focus,
.member-profile textarea:focus {
  border-color: #2563eb;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.member-profile button {
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

.member-profile button:hover:not(:disabled) {
  background-color: #1d4ed8;
  transform: translateY(-1px);
}

.member-profile button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 6px 12px rgba(37, 99, 235, 0.35);
}

.member-profile button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}
</style>

