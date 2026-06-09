<template>
  <div class="transition-marker" :class="transition.position" :title="label">
    <span class="marker-icon">⬥</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TRANSITION_TYPES } from '../utils/transitions.js'

const props = defineProps({ transition: Object, clip: Object })

const label = computed(() => {
  const t = TRANSITION_TYPES.find(tt => tt.value === props.transition.type)
  return `${t?.label || props.transition.type} (${props.transition.duration}s)`
})
</script>

<style scoped>
.transition-marker {
  position: absolute;
  top: 2px;
  font-size: 10px;
  color: #ff9800;
  cursor: pointer;
}

.transition-marker.start {
  left: 2px;
}

.transition-marker.end {
  right: 2px;
}

.marker-icon {
  user-select: none;
}
</style>
