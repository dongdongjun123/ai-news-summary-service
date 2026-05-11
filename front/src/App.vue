<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* 전역 리셋 */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
  background: #f9fafb;
  color: #111827;
}
</style>
