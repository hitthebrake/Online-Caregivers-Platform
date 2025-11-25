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
  // caregiver profile fields:
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

// Member: incoming applications
const incoming = ref<IncomingApplication[]>([]);

// Appointment modal state (for member)
const appointmentModalOpen = ref(false);
const appointmentForm = ref({
  appointment_date: "", // yyyy-mm-dd
  appointment_time: "", // hh:mm:ss or ISO time
  work_hours: 1,
  status: "pending",
  caregiver_user_id: 0,
  member_user_id: auth.user_id ?? 0,
});

// Caregiver: own applications and job map
const myApplications = ref<MyApplication[]>([]);
const myJobs = ref<Job[]>([]);
const jobMap = ref<Record<number, Job>>({}); // job_id -> Job

// helpers
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

// Load incoming applications for member
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

// Open appointment form for a particular caregiver (member)
function openAppointmentFormFor(app: IncomingApplication) {
  resetAppointmentForm();
  appointmentForm.value.caregiver_user_id = app.caregiver_user_id;
  appointmentForm.value.member_user_id = auth.user_id ?? 0;
  // default appointment_date to today
  appointmentForm.value.appointment_date = new Date().toISOString().slice(0, 10);
  // default time to current time hh:mm:ss
  const now = new Date();
  appointmentForm.value.appointment_time = now.toTimeString().split(" ")[0];
  appointmentModalOpen.value = true;
}

// Submit appointment (member)
async function submitAppointment() {
  try {
    // minimal validation
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
    // reload incoming list in case status changed server-side
    await loadIncoming();
  } catch (e: any) {
    console.error("submitAppointment", e);
    alert("Create appointment failed: " + JSON.stringify(e?.response?.data || e.message));
  }
}

// Caregiver: load own applications and jobs
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
    // build job map
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

// Caregiver: delete application
async function deleteApplication(jobId: number, caregiverUserId: number) {
  if (!confirm("Delete this application?")) return;
  try {
    await api.delete(`/job_applications/${jobId}/${caregiverUserId}`);
    alert("Application deleted");
    // refresh
    await loadCaregiverData();
  } catch (e: any) {
    console.error("deleteApplication", e);
    alert("Delete failed: " + JSON.stringify(e?.response?.data || e.message));
  }
}

// initial load
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
          <option value="confirmed">confirmed</option>
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
                Member ID: {{ jobMap[app.job_id].member_user_id }}
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
.applications-page { max-width: 1000px; margin: 20px auto; padding: 12px; }
.apps-table { width: 100%; border-collapse: collapse; margin-top: 12px; }
.apps-table th, .apps-table td { border: 1px solid #eee; padding: 10px; text-align: left; vertical-align: top; }
.apps-table th { background: #f5f5f5; }
button { padding: 6px 10px; margin-right: 6px; cursor: pointer; }

/* modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index: 80; }
.modal { background: white; padding: 16px; border-radius: 8px; max-width: 520px; width: 92%; box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
.modal-actions { display:flex; gap:8px; margin-top:12px; }
.error { color: red; }
</style>
