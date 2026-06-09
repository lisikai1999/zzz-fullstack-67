import { ref } from 'vue'
import { store, getAllClipsAtTime } from '../stores/project.js'
import { api } from '../api/client.js'

export function useAudio() {
  let audioCtx = null
  let masterGain = null
  const audioBuffers = ref({})
  const activeSourceNodes = ref({})
  let scheduledBaseTime = 0
  let scheduledCtxTime = 0

  function getAudioContext() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)()
      masterGain = audioCtx.createGain()
      masterGain.connect(audioCtx.destination)
    }
    return audioCtx
  }

  async function loadAudioBuffer(mediaId) {
    if (audioBuffers.value[mediaId]) return audioBuffers.value[mediaId]

    const ctx = getAudioContext()
    const url = api.mediaStreamUrl(mediaId)
    try {
      const response = await fetch(url)
      const arrayBuffer = await response.arrayBuffer()
      const buffer = await ctx.decodeAudioData(arrayBuffer)
      audioBuffers.value[mediaId] = buffer
      return buffer
    } catch (e) {
      console.warn(`Failed to decode audio for media ${mediaId}:`, e)
      return null
    }
  }

  async function preloadTrackAudio(tracks) {
    const audioTracks = tracks.filter(t => t.type === 'audio')
    for (const track of audioTracks) {
      for (const clip of track.clips) {
        await loadAudioBuffer(clip.media_id)
      }
    }
  }

  function stopAudioPlayback() {
    for (const nodeSet of Object.values(activeSourceNodes.value)) {
      try {
        nodeSet.gainNode.gain.setValueAtTime(0, audioCtx ? audioCtx.currentTime : 0)
        nodeSet.source.stop(audioCtx ? audioCtx.currentTime + 0.02 : 0)
      } catch {}
    }
    activeSourceNodes.value = {}
  }

  function setMasterVolume(value) {
    if (masterGain) {
      masterGain.gain.value = Math.max(0, Math.min(1, value))
    }
  }

  function scheduleFullPlayback(startTime) {
    stopAudioPlayback()
    const ctx = getAudioContext()
    if (ctx.state === 'suspended') ctx.resume()

    scheduledBaseTime = startTime
    scheduledCtxTime = ctx.currentTime

    for (const track of store.tracks) {
      if (track.type !== 'audio' || track.muted) continue

      for (const clip of track.clips) {
        const buffer = audioBuffers.value[clip.media_id]
        if (!buffer) continue

        const clipStart = clip.position
        const clipEnd = clip.position + (clip.out_point - clip.in_point)

        if (clipEnd <= startTime) continue

        const source = ctx.createBufferSource()
        source.buffer = buffer

        const gainNode = ctx.createGain()
        gainNode.gain.value = 1.0
        source.connect(gainNode)
        gainNode.connect(masterGain)

        let offset = clip.in_point
        let when = 0

        if (clipStart >= startTime) {
          when = clipStart - startTime
        } else {
          offset = clip.in_point + (startTime - clipStart)
        }

        const duration = clip.out_point - offset
        if (duration > 0) {
          source.start(ctx.currentTime + when, offset, duration)
          activeSourceNodes.value[`${clip.id}_${Date.now()}`] = { source, gainNode }
        }
      }
    }
  }

  function seekReschedule(newTime) {
    // Crossfade: ramp old sources to 0 over 30ms, then schedule new ones
    const ctx = getAudioContext()
    if (!ctx) return

    const fadeTime = 0.03
    const now = ctx.currentTime

    // Fade out current sources quickly
    for (const nodeSet of Object.values(activeSourceNodes.value)) {
      try {
        nodeSet.gainNode.gain.setValueAtTime(nodeSet.gainNode.gain.value, now)
        nodeSet.gainNode.gain.linearRampToValueAtTime(0, now + fadeTime)
        nodeSet.source.stop(now + fadeTime + 0.01)
      } catch {}
    }
    activeSourceNodes.value = {}

    // Schedule new sources from the seek position after the short fade
    scheduledBaseTime = newTime
    scheduledCtxTime = now + fadeTime

    for (const track of store.tracks) {
      if (track.type !== 'audio' || track.muted) continue

      for (const clip of track.clips) {
        const buffer = audioBuffers.value[clip.media_id]
        if (!buffer) continue

        const clipStart = clip.position
        const clipEnd = clip.position + (clip.out_point - clip.in_point)

        if (clipEnd <= newTime) continue

        const source = ctx.createBufferSource()
        source.buffer = buffer

        const gainNode = ctx.createGain()
        gainNode.gain.setValueAtTime(0, now)
        gainNode.gain.linearRampToValueAtTime(1.0, now + fadeTime)
        source.connect(gainNode)
        gainNode.connect(masterGain)

        let offset = clip.in_point
        let when = 0

        if (clipStart >= newTime) {
          when = clipStart - newTime
        } else {
          offset = clip.in_point + (newTime - clipStart)
        }

        const duration = clip.out_point - offset
        if (duration > 0) {
          source.start(scheduledCtxTime + when, offset, duration)
          activeSourceNodes.value[`${clip.id}_${Date.now()}`] = { source, gainNode }
        }
      }
    }
  }

  return {
    loadAudioBuffer,
    preloadTrackAudio,
    stopAudioPlayback,
    scheduleFullPlayback,
    seekReschedule,
    setMasterVolume,
    audioBuffers,
  }
}
