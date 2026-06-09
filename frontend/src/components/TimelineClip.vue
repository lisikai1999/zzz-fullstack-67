<template>
  <div
    class="timeline-clip"
    :class="{ selected: store.selectedClipId === clip.id }"
    :style="clipStyle"
    @mousedown.stop="onClipMouseDown"
    @dblclick="onSplit"
    @contextmenu.prevent="onContextMenu"
    draggable="true"
    @dragstart="onDragStart"
  >
    <!-- Left trim handle -->
    <div class="trim-handle trim-left" @mousedown.stop="onTrimStart('left', $event)"></div>

    <!-- Clip body -->
    <div class="clip-body">
      <span class="clip-label">{{ clip.media_id }}</span>
      <!-- Keyframe markers -->
      <div class="keyframe-markers">
        <KeyframeMarker
          v-for="kf in clip.keyframes"
          :key="kf.id"
          :keyframe="kf"
          :clip="clip"
        />
      </div>
      <!-- Transition markers -->
      <TransitionMarker
        v-for="tr in clip.transitions"
        :key="tr.id"
        :transition="tr"
        :clip="clip"
      />
    </div>

    <!-- Right trim handle -->
    <div class="trim-handle trim-right" @mousedown.stop="onTrimStart('right', $event)"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { store } from '../stores/project.js'
import { useTimeline } from '../composables/useTimeline.js'
import { useDrag } from '../composables/useDrag.js'
import { api } from '../api/client.js'
import KeyframeMarker from './KeyframeMarker.vue'
import TransitionMarker from './TransitionMarker.vue'

const props = defineProps({ clip: Object, track: Object })
const { timeToPixel, pixelToTime } = useTimeline()

const clipStyle = computed(() => {
  const left = timeToPixel(props.clip.position)
  const width = props.clip.duration * store.zoom * store.pixelsPerSecond
  const color = props.track.type === 'video' ? '#4a90d9' : '#6fcf97'
  return {
    left: `${left}px`,
    width: `${Math.max(width, 4)}px`,
    backgroundColor: color,
  }
})

function onClipMouseDown(e) {
  store.selectedClipId = props.clip.id
  startMove(e)
}

let moveStartPos = 0
const { onStart: startMove } = useDrag({
  onStart() {
    moveStartPos = props.clip.position
  },
  onMove(_, dx) {
    const dt = dx / (store.zoom * store.pixelsPerSecond)
    props.clip.position = Math.max(0, moveStartPos + dt)
  },
  onEnd() {
    api.updateClip(props.clip.id, { position: props.clip.position })
  },
})

function onTrimStart(side, event) {
  const startIn = props.clip.in_point
  const startOut = props.clip.out_point
  const startPos = props.clip.position

  const { onStart } = useDrag({
    onMove(_, dx) {
      const dt = dx / (store.zoom * store.pixelsPerSecond)
      if (side === 'left') {
        const newIn = Math.max(0, startIn + dt)
        if (newIn < props.clip.out_point) {
          props.clip.in_point = newIn
          props.clip.position = startPos + (newIn - startIn)
          props.clip.duration = props.clip.out_point - props.clip.in_point
        }
      } else {
        const newOut = Math.max(props.clip.in_point + 0.1, startOut + dt)
        props.clip.out_point = newOut
        props.clip.duration = newOut - props.clip.in_point
      }
    },
    onEnd() {
      api.updateClip(props.clip.id, {
        position: props.clip.position,
        in_point: props.clip.in_point,
        out_point: props.clip.out_point,
      })
    },
  })
  onStart(event)
}

function onSplit() {
  const splitTime = store.playhead
  const clipEnd = props.clip.position + props.clip.duration
  if (splitTime <= props.clip.position || splitTime >= clipEnd) return

  api.splitClip(props.clip.id, splitTime).then(([clip1, clip2]) => {
    const idx = props.track.clips.findIndex(c => c.id === props.clip.id)
    if (idx !== -1) {
      props.track.clips.splice(idx, 1, clip1, clip2)
    }
  })
}

function onDragStart(e) {
  e.dataTransfer.setData('clipId', String(props.clip.id))
  e.dataTransfer.setData('trackId', String(props.track.id))
}

function onContextMenu() {
  // Could show context menu for delete, add transition, etc.
  if (confirm('删除此片段?')) {
    api.deleteClip(props.clip.id).then(() => {
      const idx = props.track.clips.findIndex(c => c.id === props.clip.id)
      if (idx !== -1) props.track.clips.splice(idx, 1)
    })
  }
}
</script>

<style scoped>
.timeline-clip {
  position: absolute;
  top: 4px;
  bottom: 4px;
  border-radius: 4px;
  cursor: grab;
  display: flex;
  align-items: stretch;
  min-width: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  transition: box-shadow 0.1s;
}

.timeline-clip.selected {
  box-shadow: 0 0 0 2px #64ffda, 0 2px 6px rgba(100,255,218,0.3);
}

.timeline-clip:active {
  cursor: grabbing;
}

.trim-handle {
  width: 6px;
  cursor: ew-resize;
  background: rgba(255,255,255,0.2);
  flex-shrink: 0;
}

.trim-handle:hover {
  background: rgba(255,255,255,0.5);
}

.trim-left {
  border-radius: 4px 0 0 4px;
}

.trim-right {
  border-radius: 0 4px 4px 0;
}

.clip-body {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 2px 4px;
}

.clip-label {
  font-size: 10px;
  color: rgba(255,255,255,0.8);
  white-space: nowrap;
}

.keyframe-markers {
  position: absolute;
  bottom: 2px;
  left: 0;
  right: 0;
  height: 8px;
}
</style>
