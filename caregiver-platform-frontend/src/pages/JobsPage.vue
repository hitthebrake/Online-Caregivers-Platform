<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import api from "../api/axios";
import { useAuthStore } from "../stores/auth";

// Types
type Job = {
  required_caregiving_type: string;
  other_requirements: string;
  job_id: number;
  member_user_id: number;
};

type MemberWithUser = {
  house_rules: string;
  dependent_description: string;
  member_user_id: number;
  user: {
    user_id: number;
    email: string;
    given_name?: string;
    surname?: string;
    city?: string;
    phone_number?: string;
    profile_description?: string;
    user_type?: string;
  };
};

// Auth
const auth = useAuthStore();
auth.loadAuth(); // ensure loaded from localStorage

const isMember = computed(() => auth.user_type === "member");
const isCaregiver = computed(() => auth.user_type === "caregiver");

// State
const loading = ref(false);
const jobs = ref<Job[]>([]);
const error = ref<string | null>(null);

// Create job form (for members)
const newJob = ref({
  required_caregiving_type: "babysitter",
  other_requirements: "",
});

// Member info panel for caregivers
const selectedMember = ref<MemberWithUser | null>(null);
const memberModalOpen = ref(false);

// Pagination/filtering could be added later

// Load jobs depending on role
async function loadJobs() {
  loading.value = true;
  error.value = null;
  try {
    if (isMember.value) {
      // Member sees their own jobs
      const r = await api.get("/user/jobs");
      jobs.value = r.data as Job[];
    } else {
      // Caregiver sees all jobs
      const r = await api.get("/jobs");
      jobs.value = r.data as Job[];
    }
  } catch (e: any) {
    console.error("loadJobs", e);
    error.value = JSON.stringify(e?.response?.data || e.message || "Failed to load jobs");
  } finally {
    loading.value = false;
  }
}

// Create a job (members only)
async function createJob() {
  if (!isMember.value) return alert("Only members can create jobs.");
  try {
    const payload = {
      required_caregiving_type: newJob.value.required_caregiving_type,
      other_requirements: newJob.value.other_requirements,
      member_user_id: auth.user_id,
    };
    await api.post("/jobs", payload);
    alert("Job created successfully");
    // reset form
    newJob.value.other_requirements = "";
    newJob.value.required_caregiving_type = "babysitter";
    // reload jobs
    await loadJobs();
  } catch (e: any) {
    console.error("createJob", e);
    alert("Create job failed: " + JSON.stringify(e?.response?.data || e.message));
  }
}

// Delete job (members only)
async function deleteJob(jobId: number) {
  if (!confirm("Are you sure you want to delete this job?")) return;
  try {
    await api.delete(`/jobs/${jobId}`);
    alert("Job deleted");
    await loadJobs();
  } catch (e: any) {
    console.error("deleteJob", e);
    alert("Delete failed: " + JSON.stringify(e?.response?.data || e.message));
  }
}

// Apply for a job (caregivers only)
async function applyToJob(jobId: number) {
  if (!isCaregiver.value) return alert("Only caregivers can apply.");
  try {
    const payload = {
      caregiver_user_id: auth.user_id,
      job_id: jobId,
    };
    await api.post("/job_applications", payload);
    alert("Applied successfully");
    // optionally refresh something
  } catch (e: any) {
    console.error("applyToJob", e);
    alert("Apply failed: " + JSON.stringify(e?.response?.data || e.message));
  }
}

// Fetch member details for a job (caregiver)
async function viewMember(memberUserId: number) {
  try {
    // According to your description, /members returns an array; filter by member_user_id param.
    // If backend supports query param use it, otherwise fetch all and find (inefficient).
    // We'll try /members?member_user_id=... first and fallback to /members.
    let r;
    try {
      r = await api.get(`/members?member_user_id=${memberUserId}`);
    } catch {
      r = await api.get("/members");
    }

    const list: MemberWithUser[] = r.data;
    const found = list.find((m) => m.member_user_id === memberUserId);
    if (!found) {
      alert("Member info not found");
      return;
    }
    selectedMember.value = found;
    memberModalOpen.value = true;
  } catch (e: any) {
    console.error("viewMember", e);
    alert("Failed to fetch member info: " + JSON.stringify(e?.response?.data || e.message));
  }
}

// init
onMounted(() => {
  loadJobs();
});
</script>

<template>
  <div class="jobs-page">
    <h1>Jobs</h1>

    <div v-if="loading">Loading jobs…</div>
    <div v-if="error" class="error">Error: {{ error }}</div>

    <!-- Member: create job form -->
    <section v-if="isMember" class="create-job">
      <h2>Create a job</h2>
      <div class="form-row">
        <label>Required caregiving type</label>
        <select v-model="newJob.required_caregiving_type">
          <option value="babysitter">babysitter</option>
         <option value="caregiver for elderly">caregiver for elderly</option>
         <option value="playmate for children">playmate for children</option>
        </select>
      </div>

      <div class="form-row">
        <label>Other requirements</label>
        <textarea v-model="newJob.other_requirements" rows="3" />
      </div>

      <button @click="createJob">Create job</button>
    </section>

    <hr />

    <!-- Jobs list -->
    <section class="jobs-list">
      <h2 v-if="isMember">Your jobs</h2>
      <h2 v-else>Available jobs</h2>

      <table class="jobs-table" v-if="jobs.length">
        <thead>
          <tr>
            <th>Type</th>
            <th>Requirements</th>
            <th>Member</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.job_id">
            <td>{{ job.required_caregiving_type }}</td>
            <td>{{ job.other_requirements }}</td>
            <td>
              <button v-if="isCaregiver" @click="viewMember(job.member_user_id)">
                View member
              </button>
              <span v-else>—</span>
            </td>
            <td>
              <button v-if="isMember" @click="deleteJob(job.job_id)">Delete</button>
              <button v-if="isCaregiver" @click="applyToJob(job.job_id)">Apply</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else>
        <p>No jobs found.</p>
      </div>
    </section>

    <!-- Member modal -->
    <div v-if="memberModalOpen" class="modal-backdrop" @click.self="memberModalOpen = false">
      <div class="modal">
        <h3>Member info</h3>
        <div v-if="selectedMember">
          <p><strong>Name:</strong> {{ selectedMember.user.given_name }} {{ selectedMember.user.surname }}</p>
          <p><strong>Email:</strong> {{ selectedMember.user.email }}</p>
          <p><strong>City:</strong> {{ selectedMember.user.city }}</p>
          <p><strong>Phone:</strong> {{ selectedMember.user.phone_number }}</p>
          <p><strong>House rules:</strong> {{ selectedMember.house_rules }}</p>
          <p><strong>Dependent:</strong> {{ selectedMember.dependent_description }}</p>
        </div>

        <div style="margin-top:10px">
          <button @click="memberModalOpen = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.jobs-page {
  max-width: 1100px;
  margin: 32px auto;
  padding: 24px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.12);
}

.jobs-page h1 {
  margin-bottom: 20px;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
}

.jobs-page h2 {
  margin: 20px 0 12px;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.create-job {
  background: #ffffff;
  padding: 18px 16px;
  border-radius: 14px;
  box-shadow: 0 12px 26px rgba(148, 163, 184, 0.28);
  border: 1px solid rgba(148, 163, 184, 0.35);
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.form-row label {
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
}

.jobs-page textarea,
.jobs-page select,
.jobs-page input {
  width: 100%;
  padding: 9px 10px;
  border-radius: 10px;
  border: 1px solid #d4d4d8;
  background-color: #f9fafb;
  font-size: 14px;
  resize: vertical;
  min-height: 40px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
  box-sizing: border-box;
}

.jobs-page textarea:focus,
.jobs-page select:focus,
.jobs-page input:focus {
  border-color: #2563eb;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.jobs-page button {
  border: none;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.12s ease, transform 0.07s ease, box-shadow 0.12s ease,
    opacity 0.15s ease;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35);
}

.jobs-page button:hover:not(:disabled) {
  background-color: #1d4ed8;
  transform: translateY(-1px);
}

.jobs-page button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 5px 12px rgba(37, 99, 235, 0.35);
}

.jobs-page button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.jobs-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 18px;
  background: #ffffff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
}

.jobs-table thead {
  background: linear-gradient(135deg, #0f766e, #14b8a6);
  color: #ecfeff;
}

.jobs-table th,
.jobs-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 14px;
}

.jobs-table th {
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
}

.jobs-table tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.jobs-table tbody tr:hover {
  background-color: #ecfeff;
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

/* modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
}

.modal {
  background: #ffffff;
  padding: 20px 18px;
  border-radius: 18px;
  max-width: 520px;
  width: 92%;
  box-shadow: 0 26px 70px rgba(15, 23, 42, 0.45);
}

.modal h3 {
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.modal p {
  margin: 4px 0;
  color: #374151;
}

.modal button {
  margin-top: 14px;
}

@media (max-width: 768px) {
  .jobs-page {
    margin: 20px 12px;
    padding: 16px;
  }

  .jobs-table {
    display: block;
    overflow-x: auto;
    box-shadow: none;
  }
}
</style>

