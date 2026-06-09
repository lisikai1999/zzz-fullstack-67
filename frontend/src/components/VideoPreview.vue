<template>
  <div class="video-preview">
    <div class="preview-canvas-wrapper">
      <canvas ref="canvasRef" class="preview-canvas"></canvas>
    </div>
    <div v-if="notification" class="notification" @click="notification = ''">
      {{ notification }}
    </div>
    <div class="preview-controls">
      <button @click="togglePlayback">{{ store.isPlaying ? '⏸' : '▶' }}</button>
      <button @click="seekTo(0)">⏮</button>
      <span class="timecode">{{ formatTime(store.playhead) }}</span>
      <div class="controls-right">
        <label class="proxy-toggle">
          <input type="checkbox" v-model="useProxy" @change="onProxyToggle" />
          <span>代理模式</span>
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          v-model.number="volume"
          @input="onVolumeChange"
          class="volume-slider"
          title="音量"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { store } from '../stores/project.js'
import { useRenderer } from '../composables/useRenderer.js'
import { formatTime } from '../utils/time.js'

const canvasRef = ref(null)
const useProxy = ref(true)
const volume = ref(1.0)
const notification = ref('')
let notifyTimer = null

const { renderFrame, togglePlayback, switchProxyMode, seekTo, audio, setNotify } = useRenderer(canvasRef)

setNotify((msg) => {
  notification.value = msg
  clearTimeout(notifyTimer)
  notifyTimer = setTimeout(() => { notification.value = '' }, 4000)
})

function onProxyToggle() {
  switchProxyMode(useProxy.value)
  renderFrame(store.playhead)
}

function onVolumeChange() {
  audio.setMasterVolume(volume.value)
}

watch(() => store.playhead, () => {
  if (!store.isPlaying) {
    renderFrame(store.playhead)
  }
})

watch(() => store.tracks, async () => {
  await audio.preloadTrackAudio(store.tracks)
}, { deep: true })

onMounted(async () => {
  renderFrame(store.playhead)
  if (store.tracks.length > 0) {
    await audio.preloadTrackAudio(store.tracks)
  }
})
</script>

<style scoped>
.video-preview {
  flex: 2;
  display: flex;
  flex-direction: column;
  background: #000;
  min-width: 0;
  position: relative;
}

.preview-canvas-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-canvas {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.notification {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 152, 0, 0.9);
  color: #000;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  z-index: 50;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-8px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.preview-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #111;
}

.preview-controls button {
  background: none;
  border: 1px solid #444;
  color: #fff;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.preview-controls button:hover {
  background: #333;
}

.timecode {
  font-family: monospace;
  font-size: 13px;
  color: #64ffda;
}

.controls-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.proxy-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #aaa;
  cursor: pointer;
}

.proxy-toggle input {
  cursor: pointer;
}

.volume-slider {
  width: 60px;
  cursor: pointer;
}
</style>
