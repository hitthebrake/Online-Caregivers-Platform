<script setup lang="ts">
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <div id="app">
    <NavBar />

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
  padding: 20px;
}

/* Remove old header/nav styles unless you need them */
</style>
