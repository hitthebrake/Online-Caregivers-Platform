<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import api from "../api/axios";
import { useAuthStore } from "../stores/auth";

// Types
type Address = {
  house_number?: string;
  street?: string;
  town?: string;
};

type Appointment = {
  appointment_date: string;   // e.g. "2025-11-25"
  appointment_time: string;   // e.g. "03:45:21.507Z" or "03:45:21"
  work_hours: number;
  status: "pending" | "confirmed" | "declined" | string;
  appointment_id: number;
  caregiver_user_id: number;
  caregiver_name?: string;
  caregiver_surname?: string;
  caregiver_phone_number?: string;
  caregiver_email?: string;
  member_user_id?: number;
  member_name?: string;
  member_surname?: string;
  member_phone_number?: string;
  member_email?: string;
  member_address?: Address;
};

const auth = useAuthStore();
auth.loadAuth();

const isMember = computed(() => auth.user_type === "member");
const isCaregiver = computed(() => auth.user_type === "caregiver");

const loading = ref(false);
const appointments = ref<Appointment[]>([]);
const error = ref<string | null>(null);

// Per-row updating state
const updatingMap = ref<Record<number, boolean>>({});

// Local status selections (so user chooses new status before pressing Update)
const statusSelections = ref<Record<number, Appointment["status"]>>({});

async function loadAppointments() {
  loading.value = true;
  error.value = null;
  try {
    if (isMember.value) {
      const r = await api.get("/user/member_appointments");
      appointments.value = r.data as Appointment[];
    } else if (isCaregiver.value) {
      const r = await api.get("/user/caregiver_appointments");
      appointments.value = r.data as Appointment[];
    } else {
      appointments.value = [];
    }

    // initialize statusSelections for each appointment
    const map: Record<number, Appointment["status"]> = {};
    appointments.value.forEach((a) => {
      map[a.appointment_id] = a.status;
    });
    statusSelections.value = map;
  } catch (e: any) {
    console.error("loadAppointments", e);
    error.value = JSON.stringify(e?.response?.data || e.message || "Failed to load appointments");
  } finally {
    loading.value = false;
  }
}

/**
 * Update status for an appointment.
 * Calls PUT /appointments/{appointment_id}/{status}
 */
async function updateStatus(appointmentId: number) {
  const newStatus = statusSelections.value[appointmentId];
  if (!newStatus) {
    alert("Please select a status first.");
    return;
  }

  // no change -> skip
  const current = appointments.value.find((a) => a.appointment_id === appointmentId)?.status;
  if (current === newStatus) {
    alert("Status unchanged.");
    return;
  }

  updatingMap.value[appointmentId] = true;
  try {
    // Using PUT per your earlier spec. If backend expects POST use api.post(...)
    await api.put(`/appointments/${appointmentId}/${newStatus}`);
    alert("Status updated");
    // reload appointments to get fresh data
    await loadAppointments();
  } catch (e: any) {
    console.error("updateStatus", e);
    alert("Failed to update status: " + JSON.stringify(e?.response?.data || e.message));
  } finally {
    updatingMap.value[appointmentId] = false;
  }
}

// helper to format time/date for display
function formatDateTime(dateStr: string, timeStr: string) {
  // If timeStr is already an ISO time with Z, show trimmed
  try {
    let dateDisplay = dateStr ?? "";
    let timeDisplay = timeStr ?? "";

    // If timeStr seems ISO full datetime, try to parse and format local time hh:mm
    if (timeStr && timeStr.includes("T")) {
      const d = new Date(timeStr);
      timeDisplay = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } else if (timeStr && timeStr.endsWith("Z")) {
      const d = new Date(timeStr);
      timeDisplay = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } else if (timeStr) {
      // if it's hh:mm:ss.fffZ or hh:mm:ss..., just take hh:mm
      const parts = timeStr.split(":");
      timeDisplay = parts.length >= 2 ? `${parts[0]}:${parts[1]}` : timeStr;
    }

    return `${dateDisplay} ${timeDisplay}`;
  } catch {
    return `${dateStr} ${timeStr}`;
  }
}

onMounted(() => {
  loadAppointments();
});
</script>

<template>
  <div class="appointments-page">
    <h1>Appointments</h1>

    <div v-if="loading">Loading appointments…</div>
    <div v-if="error" class="error">Error: {{ error }}</div>

    <div v-if="appointments.length === 0 && !loading">
      <p>No appointments found.</p>
    </div>

    <table v-if="appointments.length" class="appt-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Date & Time</th>
          <th>Hours</th>
          <th>Status</th>
          <th v-if="isMember">Caregiver</th>
          <th v-if="isCaregiver">Member</th>
          <th>Address</th>
          <th>Action</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="a in appointments" :key="a.appointment_id">
          <td>{{ a.appointment_id }}</td>
          <td>{{ formatDateTime(a.appointment_date, a.appointment_time) }}</td>
          <td>{{ a.work_hours }}</td>

          <td>
            <div>{{ a.status }}</div>
            <!-- control to pick new status -->
            <select v-model="statusSelections[a.appointment_id]">
              <option value="pending">pending</option>
              <option value="confirmed">confirmed</option>
              <option value="declined">declined</option>
            </select>
          </td>

          <td v-if="isMember">
            <div><strong>{{ a.caregiver_name }} {{ a.caregiver_surname }}</strong></div>
            <div>{{ a.caregiver_email }}</div>
            <div>{{ a.caregiver_phone_number }}</div>
          </td>

          <td v-if="isCaregiver">
            <div><strong>{{ a.member_name }} {{ a.member_surname }}</strong></div>
            <div>{{ a.member_email }}</div>
            <div>{{ a.member_phone_number }}</div>
          </td>

          <td>
            <div v-if="a.member_address">
              <div>{{ a.member_address.house_number }} {{ a.member_address.street }}</div>
              <div>{{ a.member_address.town }}</div>
            </div>
            <div v-else>—</div>
          </td>

          <td>
            <button
              :disabled="updatingMap[a.appointment_id]"
              @click="updateStatus(a.appointment_id)"
            >
              {{ updatingMap[a.appointment_id] ? "Updating…" : "Update status" }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.appointments-page {
  max-width: 1100px;
  margin: 32px auto;
  padding: 24px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.12);
}

.appointments-page h1 {
  margin-bottom: 18px;
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
}

.appointments-page p {
  margin: 6px 0;
  color: #475569;
}

.appt-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 18px;
  background: #ffffff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
}

.appt-table thead {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  color: #e5ecff;
}

.appt-table th,
.appt-table td {
  padding: 10px 12px;
  font-size: 14px;
  border-bottom: 1px solid #e2e8f0;
}

.appt-table th {
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
}

.appt-table tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.appt-table tbody tr:hover {
  background-color: #eff6ff;
}

.appointments-page select,
.appointments-page input {
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid #d4d4d8;
  background-color: #f9fafb;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
}

.appointments-page select:focus,
.appointments-page input:focus {
  border-color: #2563eb;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.appointments-page button {
  border: none;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.12s ease, transform 0.07s ease, box-shadow 0.12s ease,
    opacity 0.15s ease;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35);
}

.appointments-page button:hover:not(:disabled) {
  background-color: #1d4ed8;
  transform: translateY(-1px);
}

.appointments-page button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 5px 12px rgba(37, 99, 235, 0.35);
}

.appointments-page button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.error {
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
  font-size: 13px;
}

@media (max-width: 768px) {
  .appointments-page {
    margin: 20px 12px;
    padding: 16px;
  }

  .appt-table {
    display: block;
    overflow-x: auto;
    box-shadow: none;
  }
}
</style>

