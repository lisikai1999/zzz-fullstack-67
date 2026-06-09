<template>
  <div class="properties-panel">
    <div v-if="!selectedClip" class="empty-state">
      <p>选择一个片段查看属性</p>
    </div>
    <div v-else class="panel-content">
      <h3>片段属性</h3>

      <div class="prop-section">
        <label>位置: {{ selectedClip.position.toFixed(2) }}s</label>
        <label>入点: {{ selectedClip.in_point.toFixed(2) }}s</label>
        <label>出点: {{ selectedClip.out_point.toFixed(2) }}s</label>
        <label>时长: {{ selectedClip.duration.toFixed(2) }}s</label>
        <label>图层: {{ selectedClip.layer }}</label>
      </div>

      <!-- PiP Transform Controls -->
      <div class="prop-section">
        <h4>画中画 / 变换 (片段固有属性)</h4>
        <div class="pip-controls">
          <div class="pip-row">
            <label>位置X:</label>
            <input type="number" v-model.number="pipTransform.pip_x" step="10" @change="applyPipField('pip_x')" />
          </div>
          <div class="pip-row">
            <label>位置Y:</label>
            <input type="number" v-model.number="pipTransform.pip_y" step="10" @change="applyPipField('pip_y')" />
          </div>
          <div class="pip-row">
            <label>缩放X:</label>
            <input type="number" v-model.number="pipTransform.pip_scale_x" step="0.05" min="0.01" max="5" @change="applyPipField('pip_scale_x')" />
          </div>
          <div class="pip-row">
            <label>缩放Y:</label>
            <input type="number" v-model.number="pipTransform.pip_scale_y" step="0.05" min="0.01" max="5" @change="applyPipField('pip_scale_y')" />
          </div>
          <div class="pip-row">
            <label>旋转:</label>
            <input type="number" v-model.number="pipTransform.pip_rotation" step="5" @change="applyPipField('pip_rotation')" />
          </div>
          <div class="pip-row">
            <label>透明度:</label>
            <input type="number" v-model.number="pipTransform.pip_opacity" step="0.1" min="0" max="1" @change="applyPipField('pip_opacity')" />
          </div>
        </div>
        <div class="pip-presets">
          <button @click="applyPipPreset('top-left')">左上</button>
          <button @click="applyPipPreset('top-right')">右上</button>
          <button @click="applyPipPreset('bottom-left')">左下</button>
          <button @click="applyPipPreset('bottom-right')">右下</button>
          <button @click="applyPipPreset('center')">居中</button>
        </div>
      </div>

      <div class="prop-section">
        <h4>转场</h4>
        <div class="transition-controls">
          <select v-model="newTransition.type">
            <option v-for="t in TRANSITION_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
          <select v-model="newTransition.position">
            <option value="start">开始</option>
            <option value="end">结束</option>
          </select>
          <input type="number" v-model.number="newTransition.duration" min="0.1" max="5" step="0.1" />
          <button @click="addTransition">添加</button>
        </div>
        <div v-for="tr in selectedClip.transitions" :key="tr.id" class="transition-item">
          <span>{{ getTransitionLabel(tr.type) }} ({{ tr.position }}) {{ tr.duration }}s</span>
          <button @click="removeTransition(tr.id)">✕</button>
        </div>
      </div>

      <div class="prop-section">
        <h4>关键帧</h4>
        <div class="keyframe-controls">
          <select v-model="newKeyframe.property">
            <option value="scale_x">缩放X</option>
            <option value="scale_y">缩放Y</option>
            <option value="position_x">位置X</option>
            <option value="position_y">位置Y</option>
            <option value="rotation">旋转</option>
            <option value="opacity">透明度</option>
          </select>
          <input type="number" v-model.number="newKeyframe.value" step="0.1" placeholder="值" />
          <select v-model="newKeyframe.easing">
            <option value="linear">线性</option>
            <option value="ease_in">缓入</option>
            <option value="ease_out">缓出</option>
            <option value="ease_in_out">缓入缓出</option>
          </select>
          <button @click="addKeyframe">+ 关键帧</button>
        </div>
        <div class="keyframe-list">
          <div v-for="kf in selectedClip.keyframes" :key="kf.id" class="keyframe-item">
            <span>{{ kf.property }} @ {{ kf.time.toFixed(2) }}s = {{ kf.value }}</span>
            <span class="kf-easing">{{ kf.easing }}</span>
            <button @click="removeKeyframe(kf.id)">✕</button>
          </div>
        </div>
      </div>

      <div class="prop-section">
        <h4>曲线编辑器</h4>
        <KeyframeCurveEditor :clip="selectedClip" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { store, getSelectedClip } from '../stores/project.js'
import { api } from '../api/client.js'
import { TRANSITION_TYPES } from '../utils/transitions.js'
import KeyframeCurveEditor from './KeyframeCurveEditor.vue'

const selectedClip = computed(() => getSelectedClip())

const pipTransform = reactive({
  pip_x: 0,
  pip_y: 0,
  pip_scale_x: 1,
  pip_scale_y: 1,
  pip_rotation: 0,
  pip_opacity: 1,
})

watch(selectedClip, (clip) => {
  if (!clip) return
  pipTransform.pip_x = clip.pip_x ?? 0
  pipTransform.pip_y = clip.pip_y ?? 0
  pipTransform.pip_scale_x = clip.pip_scale_x ?? 1
  pipTransform.pip_scale_y = clip.pip_scale_y ?? 1
  pipTransform.pip_rotation = clip.pip_rotation ?? 0
  pipTransform.pip_opacity = clip.pip_opacity ?? 1
}, { immediate: true })

async function applyPipField(field) {
  const clip = selectedClip.value
  if (!clip) return
  const value = pipTransform[field]
  clip[field] = value
  await api.updateClip(clip.id, { [field]: value })
}

async function applyPipPreset(preset) {
  const w = store.project?.width || 1920
  const h = store.project?.height || 1080
  const scale = 0.3
  const offsetX = (w / 2) * (1 - scale) - 20
  const offsetY = (h / 2) * (1 - scale) - 20

  switch (preset) {
    case 'top-left':
      pipTransform.pip_x = -offsetX
      pipTransform.pip_y = -offsetY
      break
    case 'top-right':
      pipTransform.pip_x = offsetX
      pipTransform.pip_y = -offsetY
      break
    case 'bottom-left':
      pipTransform.pip_x = -offsetX
      pipTransform.pip_y = offsetY
      break
    case 'bottom-right':
      pipTransform.pip_x = offsetX
      pipTransform.pip_y = offsetY
      break
    case 'center':
      pipTransform.pip_x = 0
      pipTransform.pip_y = 0
      break
  }
  pipTransform.pip_scale_x = scale
  pipTransform.pip_scale_y = scale

  const clip = selectedClip.value
  if (!clip) return
  clip.pip_x = pipTransform.pip_x
  clip.pip_y = pipTransform.pip_y
  clip.pip_scale_x = pipTransform.pip_scale_x
  clip.pip_scale_y = pipTransform.pip_scale_y
  await api.updateClip(clip.id, {
    pip_x: pipTransform.pip_x,
    pip_y: pipTransform.pip_y,
    pip_scale_x: pipTransform.pip_scale_x,
    pip_scale_y: pipTransform.pip_scale_y,
  })
}

const newTransition = reactive({
  type: 'fade_in',
  duration: 0.5,
  position: 'start',
})

const newKeyframe = reactive({
  property: 'opacity',
  value: 1,
  easing: 'linear',
})

function getTransitionLabel(type) {
  const t = TRANSITION_TYPES.find(tt => tt.value === type)
  return t?.label || type
}

async function addTransition() {
  const clip = selectedClip.value
  if (!clip) return
  const tr = await api.createTransition(clip.id, {
    type: newTransition.type,
    duration: newTransition.duration,
    position: newTransition.position,
  })
  clip.transitions.push(tr)
}

async function removeTransition(id) {
  const clip = selectedClip.value
  if (!clip) return
  await api.deleteTransition(id)
  clip.transitions = clip.transitions.filter(t => t.id !== id)
}

async function addKeyframe() {
  const clip = selectedClip.value
  if (!clip) return
  const relTime = Math.max(0, store.playhead - clip.position)
  const kf = await api.createKeyframe(clip.id, {
    time: relTime,
    property: newKeyframe.property,
    value: newKeyframe.value,
    easing: newKeyframe.easing,
  })
  clip.keyframes.push(kf)
}

async function removeKeyframe(id) {
  const clip = selectedClip.value
  if (!clip) return
  await api.deleteKeyframe(id)
  clip.keyframes = clip.keyframes.filter(k => k.id !== id)
}
</script>

<style scoped>
.properties-panel {
  flex: 1;
  min-width: 280px;
  max-width: 350px;
  overflow-y: auto;
  background: #16213e;
  border-left: 1px solid #2a2a4a;
  padding: 12px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-size: 13px;
}

.panel-content h3 {
  font-size: 14px;
  margin-bottom: 12px;
  color: #64ffda;
}

.prop-section {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2a2a4a;
}

.prop-section h4 {
  font-size: 12px;
  margin-bottom: 8px;
  color: #aaa;
}

.prop-section label {
  display: block;
  font-size: 11px;
  color: #ccc;
  margin-bottom: 4px;
}

.transition-controls, .keyframe-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.transition-controls select,
.transition-controls input,
.keyframe-controls select,
.keyframe-controls input {
  padding: 3px 6px;
  background: #2a2a4a;
  border: 1px solid #444;
  color: #e0e0e0;
  border-radius: 3px;
  font-size: 11px;
}

.transition-controls input,
.keyframe-controls input {
  width: 50px;
}

.transition-controls button,
.keyframe-controls button {
  padding: 3px 8px;
  background: #64ffda;
  color: #1a1a2e;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
}

.transition-item, .keyframe-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  padding: 4px 0;
}

.transition-item button, .keyframe-item button {
  background: none;
  border: none;
  color: #ff5555;
  cursor: pointer;
  font-size: 12px;
}

.kf-easing {
  color: #888;
  font-size: 10px;
}

.pip-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.pip-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pip-row label {
  font-size: 10px;
  color: #aaa;
  width: 42px;
  flex-shrink: 0;
  margin-bottom: 0 !important;
}

.pip-row input {
  width: 70px;
  padding: 3px 5px;
  background: #2a2a4a;
  border: 1px solid #444;
  color: #e0e0e0;
  border-radius: 3px;
  font-size: 11px;
}

.pip-presets {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.pip-presets button {
  padding: 3px 8px;
  background: #2a2a4a;
  color: #e0e0e0;
  border: 1px solid #444;
  border-radius: 3px;
  cursor: pointer;
  font-size: 10px;
}

.pip-presets button:hover {
  background: #3a3a5a;
  border-color: #64ffda;
}
</style>
