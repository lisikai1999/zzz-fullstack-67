export function framesToSeconds(frames, fps = 30) {
  return frames / fps
}

export function secondsToFrames(seconds, fps = 30) {
  return Math.round(seconds * fps)
}

export function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 100)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${String(ms).padStart(2, '0')}`
}

export function snapToGrid(time, fps = 30) {
  return Math.round(time * fps) / fps
}
