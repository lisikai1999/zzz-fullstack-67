<template>
  <div class="timeline-track" :class="{ muted: track.muted }">
    <div class="track-header">
      <span class="track-name">{{ track.name }}</span>
      <span class="track-type">{{ track.type === 'video' ? '🎬' : '🎵' }}</span>
      <button class="track-btn" @click="toggleMute" :title="track.muted ? '取消静音' : '静音'">
        {{ track.muted ? '🔇' : '🔊' }}
      </button>
    </div>
    <div class="track-clips" ref="clipsRef" @mousedown="onTrackClick" @dragover.prevent @drop="onDrop">
      <TimelineClip
        v-for="clip in track.clips"
        :key="clip.id"
        :clip="clip"
        :track="track"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { store } from '../stores/project.js'
import { api } from '../api/client.js'
import { useTimeline } from '../composables/useTimeline.js'
import TimelineClip from './TimelineClip.vue'

const props = defineProps({ track: Object })
const clipsRef = ref(null)
const { pixelToTime } = useTimeline()

function toggleMute() {
  props.track.muted = !props.track.muted
  api.updateTrack(props.track.id, { muted: props.track.muted })
}

function onTrackClick(e) {
  if (e.target === clipsRef.value) {
    store.selectedClipId = null
  }
}

function onDrop(e) {
  const clipId = parseInt(e.dataTransfer.getData('clipId'))
  if (!clipId) return
  const fromTrackId = parseInt(e.dataTransfer.getData('trackId'))
  if (fromTrackId === props.track.id) return

  // Move clip to this track
  api.updateClip(clipId, { track_id: props.track.id }).then(() => {
    // Update local state
    let movedClip = null
    for (const t of store.tracks) {
      const idx = t.clips.findIndex(c => c.id === clipId)
      if (idx !== -1) {
        movedClip = t.clips.splice(idx, 1)[0]
        break
      }
    }
    if (movedClip) {
      movedClip.track_id = props.track.id
      props.track.clips.push(movedClip)
    }
  })
}
</script>

<style scoped>
.timeline-track {
  display: flex;
  border-bottom: 1px solid #2a2a4a;
  min-height: 60px;
}

.timeline-track.muted {
  opacity: 0.5;
}

.track-header {
  width: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #1a1a3e;
  border-right: 1px solid #2a2a4a;
  font-size: 12px;
}

.track-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.track-type {
  font-size: 14px;
}

.track-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  padding: 2px;
}

.track-clips {
  flex: 1;
  position: relative;
  min-height: 50px;
}
</style>
