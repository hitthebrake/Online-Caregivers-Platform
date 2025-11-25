<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import api from "../api/axios";
import { useAuthStore } from "../stores/auth";

type Job = {
  required_caregiving_type: string;
  other_requirements: string;
  job_id: number;
  member_user_id: number;
};

type IncomingApplication = {
  job: Job;
  caregiver_user_id: number;
  date_applied: string;

  email?: string;
  given_name?: string;
  surname?: string;
  city?: string;
  phone_number?: string;
  profile_description?: string;
  photo?: string;
  gender?: string;
  caregiving_type?: string;
  hourly_rate?: number;
};

type MyApplication = {
  caregiver_user_id: number;
  job_id: number;
  date_applied: string;
};

const auth = useAuthStore();
auth.loadAuth();

const isMember = computed(() => auth.user_type === "member");
const isCaregiver = computed(() => auth.user_type === "caregiver");

const loading = ref(false);
const error = ref<string | null>(null);

const incoming = ref<IncomingApplication[]>([]);

const appointmentModalOpen = ref(false);
const appointmentForm = ref({
  appointment_date: "",
  appointment_time: "",
  work_hours: 1,
  status: "pending",
  caregiver_user_id: 0,
  member_user_id: auth.user_id ?? 0,
});

const myApplications = ref<MyApplication[]>([]);
const myJobs = ref<Job[]>([]);
const jobMap = ref<Record<number, Job>>({}); // job_id -> Job

function resetAppointmentForm() {
  appointmentForm.value = {
    appointment_date: "",
    appointment_time: "",
    work_hours: 1,
    status: "pending",
    caregiver_user_id: 0,
    member_user_id: auth.user_id ?? 0,
  };
}

async function loadIncoming() {
  loading.value = true;
  error.value = null;
  try {
    const r = await api.get("/user/job_applications");
    incoming.value = r.data as IncomingApplication[];
  } catch (e: any) {
    console.error("loadIncoming", e);
    error.value = JSON.stringify(e?.response?.data || e.message || "Failed to load incoming applications");
  } finally {
    loading.value = false;
  }
}

function openAppointmentFormFor(app: IncomingApplication) {
  resetAppointmentForm();
  appointmentForm.value.caregiver_user_id = app.caregiver_user_id;
  appointmentForm.value.member_user_id = auth.user_id ?? 0;

  appointmentForm.value.appointment_date = new Date().toISOString().slice(0, 10);

  const now = new Date();
  const timeString = now.toTimeString().split(" ")[0];
  appointmentForm.value.appointment_time = timeString || '12:00';
  appointmentModalOpen.value = true;
}

async function submitAppointment() {
  try {

    if (!appointmentForm.value.appointment_date || !appointmentForm.value.appointment_time) {
      return alert("Please provide date and time");
    }
    const payload = {
      appointment_date: appointmentForm.value.appointment_date,
      appointment_time: appointmentForm.value.appointment_time,
      work_hours: appointmentForm.value.work_hours,
      status: appointmentForm.value.status,
      caregiver_user_id: appointmentForm.value.caregiver_user_id,
      member_user_id: appointmentForm.value.member_user_id,
    };
    await api.post("/appointments", payload);
    alert("Appointment created successfully");
    appointmentModalOpen.value = false;

    await loadIncoming();
  } catch (e: any) {
    console.error("submitAppointment", e);
    alert("Create appointment failed: " + JSON.stringify(e?.response?.data || e.message));
  }
}


async function loadCaregiverData() {
  loading.value = true;
  error.value = null;
  try {
    const [appResp, jobsResp] = await Promise.all([
      api.get("/user/my_applications"),
      api.get("/jobs"),
    ]);
    myApplications.value = appResp.data as MyApplication[];
    myJobs.value = jobsResp.data as Job[];

    const map: Record<number, Job> = {};
    myJobs.value.forEach((j) => (map[j.job_id] = j));
    jobMap.value = map;
  } catch (e: any) {
    console.error("loadCaregiverData", e);
    error.value = JSON.stringify(e?.response?.data || e.message || "Failed to load caregiver data");
  } finally {
    loading.value = false;
  }
}


async function deleteApplication(jobId: number, caregiverUserId: number) {
  if (!confirm("Delete this application?")) return;
  try {
    await api.delete(`/job_applications/${jobId}/${caregiverUserId}`);
    alert("Application deleted");

    await loadCaregiverData();
  } catch (e: any) {
    console.error("deleteApplication", e);
    alert("Delete failed: " + JSON.stringify(e?.response?.data || e.message));
  }
}


onMounted(() => {
  if (isMember.value) {
    loadIncoming();
  } else if (isCaregiver.value) {
    loadCaregiverData();
  } else {
    // neither — nothing to do
  }
});
</script>

<template>
  <div class="applications-page">
    <h1>Job Applications</h1>

    <div v-if="loading">Loading…</div>
    <div v-if="error" class="error">Error: {{ error }}</div>

    <!-- MEMBER VIEW -->
    <section v-if="isMember">
      <h2>Incoming applications</h2>

      <div v-if="!incoming.length">
        <p>No incoming applications.</p>
      </div>

      <table v-else class="apps-table">
        <thead>
          <tr>
            <th>Applied on</th>
            <th>Caregiver</th>
            <th>Type</th>
            <th>Requirements</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in incoming" :key="`${app.job.job_id}-${app.caregiver_user_id}`">
            <td>{{ app.date_applied }}</td>
            <td>
              <div><strong>{{ app.given_name }} {{ app.surname }}</strong></div>
              <div>{{ app.email }}</div>
              <div>{{ app.city }} • {{ app.phone_number }}</div>
            </td>
            <td>{{ app.job.required_caregiving_type }}</td>
            <td>{{ app.job.other_requirements }}</td>
            <td>
              <button @click="openAppointmentFormFor(app)">Create appointment</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- APPOINTMENT MODAL (MEMBER) -->
    <div v-if="appointmentModalOpen" class="modal-backdrop" @click.self="appointmentModalOpen = false">
      <div class="modal">
        <h3>Create appointment</h3>

        <label>Date</label>
        <input type="date" v-model="appointmentForm.appointment_date" />

        <label>Time</label>
        <input type="time" v-model="appointmentForm.appointment_time" />

        <label>Work hours</label>
        <input type="number" v-model.number="appointmentForm.work_hours" min="1" />

        <label>Status</label>
        <select v-model="appointmentForm.status">
          <option value="pending">pending</option>
          <option value="accepted">accepted</option>
          <option value="cancelled">cancelled</option>
        </select>

        <div class="modal-actions">
          <button @click="submitAppointment">Submit</button>
          <button @click="appointmentModalOpen = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- CAREGIVER VIEW -->
    <section v-else-if="isCaregiver">
      <h2>Your applications</h2>

      <div v-if="!myApplications.length">
        <p>You have not applied to any jobs.</p>
      </div>

      <table v-else class="apps-table">
        <thead>
          <tr>
            <th>Applied on</th>
            <th>Job Type</th>
            <th>Requirements</th>
            <th>Member (owner)</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in myApplications" :key="`${app.job_id}-${app.caregiver_user_id}`">
            <td>{{ app.date_applied }}</td>
            <td>{{ jobMap[app.job_id]?.required_caregiving_type ?? "-" }}</td>
            <td>{{ jobMap[app.job_id]?.other_requirements ?? "-" }}</td>
            <td>
              <div v-if="jobMap[app.job_id]">
                Member ID: {{ jobMap[app.job_id]?.member_user_id }}
              </div>
              <div v-else>—</div>
            </td>
            <td>
              <button @click="deleteApplication(app.job_id, app.caregiver_user_id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.applications-page {
  max-width: 1100px;
  margin: 32px auto;
  padding: 24px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.12);
}

.applications-page h1 {
  margin-bottom: 18px;
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
}

.applications-page h2 {
  margin: 18px 0 10px;
  font-size: 19px;
  font-weight: 600;
  color: #111827;
}

.apps-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  background: #ffffff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
}

.apps-table thead {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: #eef2ff;
}

.apps-table th,
.apps-table td {
  padding: 9px 11px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 14px;
}

.apps-table th {
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
}

.apps-table tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.apps-table tbody tr:hover {
  background-color: #eef2ff;
}

.applications-page button {
  border: none;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.12s ease, transform 0.07s ease, box-shadow 0.12s ease,
    opacity 0.15s ease;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35);
}

.applications-page button:hover:not(:disabled) {
  background-color: #1d4ed8;
  transform: translateY(-1px);
}

.applications-page button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 5px 12px rgba(37, 99, 235, 0.35);
}

.applications-page button:disabled {
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
  .applications-page {
    margin: 20px 12px;
    padding: 16px;
  }

  .apps-table {
    display: block;
    overflow-x: auto;
    box-shadow: none;
  }
}
</style>

