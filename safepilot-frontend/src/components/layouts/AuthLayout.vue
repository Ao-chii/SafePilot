<!--
  认证页面布局 - 简洁版本
-->
<template>
  <v-app>
    <v-main class="auth-layout">
      <v-container 
        fluid 
        fill-height
        class="d-flex align-center justify-center"
      >
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
// 简化的认证布局组件
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>