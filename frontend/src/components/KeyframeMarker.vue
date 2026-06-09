<template>
  <div
    class="keyframe-marker"
    :style="markerStyle"
    :title="`${keyframe.property}: ${keyframe.value} @ ${keyframe.time.toFixed(2)}s`"
    @mousedown.stop="onDragStart"
  >◆</div>
</template>

<script setup>
import { computed } from 'vue'
import { store } from '../stores/project.js'
import { useDrag } from '../composables/useDrag.js'
import { api } from '../api/client.js'

const props = defineProps({ keyframe: Object, clip: Object })

const markerStyle = computed(() => {
  const clipDuration = props.clip.out_point - props.clip.in_point
  const pct = clipDuration > 0 ? (props.keyframe.time / clipDuration) * 100 : 0
  return { left: `${pct}%` }
})

let startTime = 0
const { onStart: onDragStart } = useDrag({
  onStart() {
    startTime = props.keyframe.time
  },
  onMove(_, dx) {
    const clipDuration = props.clip.out_point - props.clip.in_point
    const dt = (dx / (store.zoom * store.pixelsPerSecond))
    props.keyframe.time = Math.max(0, Math.min(clipDuration, startTime + dt))
  },
  onEnd() {
    api.updateKeyframe(props.keyframe.id, { time: props.keyframe.time })
  },
})
</script>

<style scoped>
.keyframe-marker {
  position: absolute;
  bottom: 0;
  font-size: 8px;
  color: #ffd700;
  cursor: pointer;
  transform: translateX(-50%);
  line-height: 1;
  user-select: none;
}

.keyframe-marker:hover {
  color: #fff;
  transform: translateX(-50%) scale(1.3);
}
</style>
