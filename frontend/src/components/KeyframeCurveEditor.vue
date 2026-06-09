<template>
  <div class="curve-editor">
    <div class="curve-toolbar">
      <select v-model="selectedProperty">
        <option value="opacity">透明度</option>
        <option value="scale_x">缩放X</option>
        <option value="scale_y">缩放Y</option>
        <option value="position_x">位置X</option>
        <option value="position_y">位置Y</option>
        <option value="rotation">旋转</option>
      </select>
      <span class="hint">点击曲线区域添加关键帧</span>
    </div>
    <canvas
      ref="canvasRef"
      class="curve-canvas"
      @mousedown="onCanvasClick"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, nextTick } from 'vue'
import { store } from '../stores/project.js'
import { api } from '../api/client.js'
import { applyEasing } from '../utils/interpolation.js'

const props = defineProps({ clip: Object })
const emit = defineEmits(['keyframeAdded'])
const canvasRef = ref(null)
const selectedProperty = ref('opacity')

const filteredKeyframes = computed(() => {
  if (!props.clip?.keyframes) return []
  return props.clip.keyframes
    .filter(k => k.property === selectedProperty.value)
    .sort((a, b) => a.time - b.time)
})

const clipDuration = computed(() => props.clip.out_point - props.clip.in_point)

function getValueRange() {
  const kfs = filteredKeyframes.value
  if (kfs.length === 0) {
    return { minVal: 0, maxVal: 1 }
  }
  const values = kfs.map(k => k.value)
  let minVal = Math.min(...values, 0)
  let maxVal = Math.max(...values, 1)
  if (maxVal - minVal < 0.01) {
    minVal -= 1
    maxVal += 1
  }
  return { minVal, maxVal }
}

function drawCurve() {
  const canvas = canvasRef.value
  if (!canvas) return

  const parent = canvas.parentElement
  canvas.width = parent.clientWidth - 4
  canvas.height = 140

  const ctx = canvas.getContext('2d')
  const W = canvas.width
  const H = canvas.height
  const kfs = filteredKeyframes.value
  const { minVal, maxVal } = getValueRange()
  const valRange = maxVal - minVal

  ctx.fillStyle = '#0d1117'
  ctx.fillRect(0, 0, W, H)

  // Grid
  ctx.strokeStyle = '#1c2333'
  ctx.lineWidth = 0.5
  for (let i = 0; i <= 4; i++) {
    const y = (i / 4) * H
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(W, y)
    ctx.stroke()
  }
  for (let i = 0; i <= 8; i++) {
    const x = (i / 8) * W
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, H)
    ctx.stroke()
  }

  if (kfs.length === 0) {
    ctx.fillStyle = '#555'
    ctx.font = '11px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('点击添加关键帧', W / 2, H / 2)
    return
  }

  function timeToX(t) { return (t / clipDuration.value) * W }
  function valToY(v) { return H - ((v - minVal) / valRange) * H }

  // Draw interpolated curve
  ctx.strokeStyle = '#64ffda'
  ctx.lineWidth = 2
  ctx.beginPath()
  const steps = Math.max(W, 100)
  for (let i = 0; i <= steps; i++) {
    const t = (i / steps) * clipDuration.value
    const val = interpolateAt(kfs, t)
    const x = timeToX(t)
    const y = valToY(val)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.stroke()

  // Draw keyframe points as diamonds
  for (const kf of kfs) {
    const x = timeToX(kf.time)
    const y = valToY(kf.value)

    ctx.fillStyle = '#ffd700'
    ctx.beginPath()
    ctx.moveTo(x, y - 6)
    ctx.lineTo(x + 6, y)
    ctx.lineTo(x, y + 6)
    ctx.lineTo(x - 6, y)
    ctx.closePath()
    ctx.fill()

    ctx.strokeStyle = '#000'
    ctx.lineWidth = 1
    ctx.stroke()
  }

  // Axis labels
  ctx.fillStyle = '#666'
  ctx.font = '9px monospace'
  ctx.textAlign = 'left'
  ctx.fillText(`${maxVal.toFixed(2)}`, 2, 10)
  ctx.fillText(`${minVal.toFixed(2)}`, 2, H - 2)
  ctx.textAlign = 'right'
  ctx.fillText(`${clipDuration.value.toFixed(1)}s`, W - 2, H - 2)
}

function interpolateAt(kfs, time) {
  if (kfs.length === 0) return 0
  if (time <= kfs[0].time) return kfs[0].value
  if (time >= kfs[kfs.length - 1].time) return kfs[kfs.length - 1].value

  for (let i = 0; i < kfs.length - 1; i++) {
    if (time >= kfs[i].time && time < kfs[i + 1].time) {
      const t = (time - kfs[i].time) / (kfs[i + 1].time - kfs[i].time)
      const easedT = applyEasing(t, kfs[i + 1].easing)
      return kfs[i].value + (kfs[i + 1].value - kfs[i].value) * easedT
    }
  }
  return kfs[kfs.length - 1].value
}

async function onCanvasClick(event) {
  const canvas = canvasRef.value
  if (!canvas || !props.clip) return

  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  const W = canvas.width
  const H = canvas.height

  const time = (x / W) * clipDuration.value
  const { minVal, maxVal } = getValueRange()
  const valRange = maxVal - minVal
  const value = maxVal - (y / H) * valRange

  const clampedTime = Math.max(0, Math.min(clipDuration.value, time))
  const roundedValue = Math.round(value * 100) / 100

  try {
    const kf = await api.createKeyframe(props.clip.id, {
      time: clampedTime,
      property: selectedProperty.value,
      value: roundedValue,
      easing: 'linear',
    })
    props.clip.keyframes.push(kf)
    nextTick(drawCurve)
  } catch (e) {
    console.error('Failed to add keyframe:', e)
  }
}

watch([filteredKeyframes, selectedProperty], () => { nextTick(drawCurve) }, { deep: true })
onMounted(() => { nextTick(drawCurve) })
</script>

<style scoped>
.curve-editor {
  margin-top: 4px;
}

.curve-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.curve-toolbar select {
  padding: 3px 6px;
  background: #2a2a4a;
  border: 1px solid #444;
  color: #e0e0e0;
  border-radius: 3px;
  font-size: 11px;
}

.hint {
  font-size: 10px;
  color: #666;
}

.curve-canvas {
  width: 100%;
  height: 140px;
  border: 1px solid #333;
  border-radius: 4px;
  cursor: crosshair;
  display: block;
}
</style>
