<template>
  <div class="timeline" ref="timelineRef">
    <div class="timeline-toolbar">
      <button @click="addTrack('video')">+ 视频轨</button>
      <button @click="addTrack('audio')">+ 音频轨</button>
      <div class="zoom-control">
        <span>缩放:</span>
        <input type="range" min="0.1" max="5" step="0.1" v-model.number="store.zoom" />
        <span>{{ Math.round(store.zoom * 100) }}%</span>
      </div>
    </div>
    <div class="timeline-scroll-area" ref="scrollArea" @wheel="onWheel" @scroll="onScroll">
      <div class="timeline-scroll-content" :style="{ width: totalWidth + 'px' }">
        <TimelineRuler :scrollLeft="currentScrollLeft" />
        <div class="timeline-tracks">
          <TimelineTrack
            v-for="track in sortedTracks"
            :key="track.id"
            :track="track"
          />
          <div v-if="sortedTracks.length === 0" class="empty-hint">
            暂无轨道，点击上方按钮添加
          </div>
        </div>
      </div>
      <!-- Playhead line: positioned relative to scroll content, accounts for scroll offset -->
      <div class="playhead-line" :style="{ left: playheadScreenPx + 'px' }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { store } from '../stores/project.js'
import { useTimeline } from '../composables/useTimeline.js'
import { api } from '../api/client.js'
import TimelineRuler from './TimelineRuler.vue'
import TimelineTrack from './TimelineTrack.vue'

const { timeToPixel, setScrollFromPixel } = useTimeline()
const timelineRef = ref(null)
const scrollArea = ref(null)
const currentScrollLeft = ref(0)

const sortedTracks = computed(() =>
  [...store.tracks].sort((a, b) => a.order - b.order)
)

const totalWidth = computed(() => {
  let maxEnd = 30
  for (const track of store.tracks) {
    for (const clip of track.clips) {
      const end = clip.position + (clip.out_point - clip.in_point)
      if (end > maxEnd) maxEnd = end
    }
  }
  return (maxEnd + 10) * store.zoom * store.pixelsPerSecond + 120
})

// Playhead position on screen = time-to-pixel in scrollable content, minus current scroll offset
// The playhead-line is inside the scroll-area (position: absolute relative to it)
// So it needs to account for scroll position to stay at the correct visual spot
const playheadScreenPx = computed(() => {
  const contentPx = store.playhead * store.zoom * store.pixelsPerSecond + 120
  return contentPx - currentScrollLeft.value
})

function onWheel(event) {
  if (event.ctrlKey || event.metaKey) {
    event.preventDefault()
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    store.zoom = Math.max(0.1, Math.min(10, store.zoom * delta))
  } else {
    // Both shift+wheel vertical and native horizontal deltaX
    const scrollEl = scrollArea.value
    if (scrollEl) {
      const dx = event.deltaX || (event.shiftKey ? event.deltaY : 0)
      if (dx !== 0) {
        scrollEl.scrollLeft += dx
        event.preventDefault()
      }
    }
  }
}

function onScroll() {
  const el = scrollArea.value
  if (el) {
    currentScrollLeft.value = el.scrollLeft
    setScrollFromPixel(el.scrollLeft)
  }
}

// When zoom changes, keep the scroll in sync
watch(() => store.zoom, () => {
  nextTick(() => {
    const el = scrollArea.value
    if (el) {
      el.scrollLeft = store.scrollX * store.zoom * store.pixelsPerSecond
      currentScrollLeft.value = el.scrollLeft
    }
  })
})

async function addTrack(type) {
  if (!store.project) return
  const name = type === 'video' ? `视频 ${store.tracks.length + 1}` : `音频 ${store.tracks.length + 1}`
  const track = await api.createTrack(store.project.id, {
    name,
    type,
    order: store.tracks.length,
  })
  store.tracks.push({ ...track, clips: [] })
}
</script>

<style scoped>
.timeline {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e3f;
  position: relative;
}

.timeline-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #16213e;
  border-bottom: 1px solid #2a2a4a;
  flex-shrink: 0;
}

.timeline-toolbar button {
  padding: 4px 10px;
  background: #2a2a4a;
  color: #e0e0e0;
  border: 1px solid #444;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.timeline-toolbar button:hover {
  background: #3a3a5a;
}

.zoom-control {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #aaa;
}

.zoom-control input[type="range"] {
  width: 100px;
}

.timeline-scroll-area {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
  position: relative;
}

.timeline-scroll-content {
  min-width: 100%;
  min-height: 100%;
}

.timeline-tracks {
  min-height: 100px;
}

.empty-hint {
  padding: 40px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.playhead-line {
  position: sticky;
  left: var(--playhead-left, 120px);
  top: 0;
  bottom: 0;
  width: 2px;
  background: #ff5555;
  pointer-events: none;
  z-index: 100;
  position: absolute;
}
</style>
