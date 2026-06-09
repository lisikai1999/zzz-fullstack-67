<template>
  <div class="ruler" @mousedown="onRulerClick" ref="rulerRef">
    <canvas ref="canvasRef" class="ruler-canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { store } from '../stores/project.js'
import { useTimeline } from '../composables/useTimeline.js'
import { formatTime } from '../utils/time.js'

const props = defineProps({ scrollLeft: { type: Number, default: 0 } })

const canvasRef = ref(null)
const rulerRef = ref(null)
const { pixelToTime, setPlayhead } = useTimeline()

function drawRuler() {
  const canvas = canvasRef.value
  const ruler = rulerRef.value
  if (!canvas || !ruler) return

  // Use the ruler's visible width for canvas sizing
  const visibleWidth = ruler.clientWidth
  canvas.width = visibleWidth
  canvas.height = 30

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = '#16213e'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const pps = store.zoom * store.pixelsPerSecond

  // Determine appropriate step for current zoom level
  let step = 1
  if (pps < 20) step = 5
  else if (pps < 50) step = 2
  else if (pps > 200) step = 0.5

  const viewStartTime = store.scrollX
  const viewEndTime = store.scrollX + canvas.width / pps
  const startTime = Math.floor(viewStartTime / step) * step

  ctx.strokeStyle = '#444'
  ctx.fillStyle = '#999'
  ctx.font = '10px monospace'
  ctx.textAlign = 'center'

  // Major marks
  for (let t = startTime; t <= viewEndTime; t += step) {
    const x = (t - store.scrollX) * pps + 120
    if (x < 0 || x > canvas.width) continue

    ctx.beginPath()
    ctx.moveTo(x, 20)
    ctx.lineTo(x, 30)
    ctx.stroke()
    ctx.fillText(formatTime(t), x, 14)
  }

  // Minor marks
  for (let t = startTime + step / 2; t <= viewEndTime; t += step) {
    const x = (t - store.scrollX) * pps + 120
    if (x < 0 || x > canvas.width) continue
    ctx.beginPath()
    ctx.moveTo(x, 24)
    ctx.lineTo(x, 30)
    ctx.stroke()
  }

  // Draw playhead indicator on ruler
  const playheadX = (store.playhead - store.scrollX) * pps + 120
  if (playheadX >= 0 && playheadX <= canvas.width) {
    ctx.fillStyle = '#ff5555'
    ctx.beginPath()
    ctx.moveTo(playheadX - 5, 0)
    ctx.lineTo(playheadX + 5, 0)
    ctx.lineTo(playheadX + 5, 4)
    ctx.lineTo(playheadX, 10)
    ctx.lineTo(playheadX - 5, 4)
    ctx.closePath()
    ctx.fill()

    ctx.strokeStyle = '#ff5555'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(playheadX, 10)
    ctx.lineTo(playheadX, 30)
    ctx.stroke()
  }
}

function onRulerClick(e) {
  const rect = rulerRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left - 120
  const time = pixelToTime(x)
  setPlayhead(time)
}

// Redraw on any state change that affects ruler appearance
watch([() => store.zoom, () => store.scrollX, () => store.playhead, () => props.scrollLeft], drawRuler)
onMounted(() => { nextTick(drawRuler) })
</script>

<style scoped>
.ruler {
  height: 30px;
  cursor: pointer;
  border-bottom: 1px solid #333;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
  background: #16213e;
}

.ruler-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
