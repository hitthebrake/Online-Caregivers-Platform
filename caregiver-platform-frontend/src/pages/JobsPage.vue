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
.jobs-page { max-width: 900px; margin: 20px auto; padding: 12px; }
.create-job { background: #fafafa; padding: 12px; border-radius: 8px; margin-bottom: 12px; }
.form-row { margin-bottom: 10px; }
textarea, select, input { width: 100%; padding: 8px; box-sizing: border-box; }
.jobs-table { width: 100%; border-collapse: collapse; margin-top: 12px; }
.jobs-table th, .jobs-table td { border: 1px solid #eee; padding: 8px; text-align: left; }
.jobs-table th { background: #f3f3f3; }
button { padding: 6px 10px; margin-right: 6px; cursor: pointer; }
.error { color: red; }

/* modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; }
.modal { background: white; padding: 16px; border-radius: 8px; max-width: 520px; width: 90%; box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
</style>
