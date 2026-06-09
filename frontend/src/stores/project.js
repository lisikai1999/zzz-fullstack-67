import { reactive, ref } from 'vue'
import { api } from '../api/client.js'

export const store = reactive({
  project: null,
  tracks: [],
  playhead: 0,
  zoom: 1.0,
  scrollX: 0,
  pixelsPerSecond: 100,
  selectedClipId: null,
  selectedTrackId: null,
  isPlaying: false,
  useProxy: true,
})

export async function loadProject(id) {
  const project = await api.getProject(id)
  store.project = { id: project.id, name: project.name, width: project.width, height: project.height, fps: project.fps }
  store.tracks = project.tracks || []
}

export async function createProject(name) {
  const project = await api.createProject({ name })
  await loadProject(project.id)
}

export function getSelectedClip() {
  if (!store.selectedClipId) return null
  for (const track of store.tracks) {
    const clip = track.clips.find(c => c.id === store.selectedClipId)
    if (clip) return clip
  }
  return null
}

export function getAllClipsAtTime(time) {
  const result = []
  for (const track of store.tracks) {
    for (const clip of track.clips) {
      const clipEnd = clip.position + clip.duration
      if (clip.position <= time && time < clipEnd) {
        result.push({ clip, track })
      }
    }
  }
  return result
}

export function timeToPixel(time) {
  return (time - store.scrollX) * store.zoom * store.pixelsPerSecond
}

export function pixelToTime(px) {
  return px / (store.zoom * store.pixelsPerSecond) + store.scrollX
}
