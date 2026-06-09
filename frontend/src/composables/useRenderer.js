import { ref } from 'vue'
import { store, getAllClipsAtTime } from '../stores/project.js'
import { interpolateAllProperties } from '../utils/interpolation.js'
import { computeTransitionAlpha, getWipeClipRegion, isWipeTransition } from '../utils/transitions.js'
import { api } from '../api/client.js'
import { useAudio } from './useAudio.js'

export function useRenderer(canvasRef) {
  const videoElements = ref({})
  const proxyFallbacks = ref({})
  let animFrameId = null
  const audio = useAudio()
  let notifyFn = null

  function setNotify(fn) {
    notifyFn = fn
  }

  function getOrCreateVideo(mediaId) {
    if (!videoElements.value[mediaId]) {
      const video = document.createElement('video')
      video.crossOrigin = 'anonymous'
      video.preload = 'auto'
      video.muted = true
      _setVideoSrc(video, mediaId)
      videoElements.value[mediaId] = video
    }
    return videoElements.value[mediaId]
  }

  function _setVideoSrc(video, mediaId) {
    if (store.useProxy && !proxyFallbacks.value[mediaId]) {
      video.src = api.mediaProxyUrl(mediaId)
      video.onerror = () => {
        proxyFallbacks.value[mediaId] = true
        video.src = api.mediaStreamUrl(mediaId)
        video.onerror = null
        if (notifyFn) {
          notifyFn(`代理文件缺失，媒体 #${mediaId} 已回退至原始源`)
        }
      }
    } else {
      video.src = api.mediaStreamUrl(mediaId)
    }
  }

  function switchProxyMode(useProxy) {
    store.useProxy = useProxy
    if (!useProxy) {
      proxyFallbacks.value = {}
    }
    for (const [mediaId, video] of Object.entries(videoElements.value)) {
      _setVideoSrc(video, parseInt(mediaId))
    }
  }

  function renderFrame(time) {
    const canvas = canvasRef.value
    if (!canvas || !store.project) return

    const ctx = canvas.getContext('2d')
    const { width, height } = store.project

    canvas.width = width
    canvas.height = height
    ctx.clearRect(0, 0, width, height)
    ctx.fillStyle = '#000'
    ctx.fillRect(0, 0, width, height)

    const visibleClips = getAllClipsAtTime(time)
      .filter(({ track }) => track.type === 'video' && !track.muted)
      .sort((a, b) => a.track.order - b.track.order)

    for (const { clip } of visibleClips) {
      const relativeTime = time - clip.position
      const sourceTime = clip.in_point + relativeTime
      const clipDuration = clip.out_point - clip.in_point

      // Keyframe-animated transforms (additive deltas)
      const kfTransforms = interpolateAllProperties(clip.keyframes || [], relativeTime)

      // Intrinsic PiP base transform (clip's own property)
      const baseX = (clip.pip_x || 0) + kfTransforms.position_x
      const baseY = (clip.pip_y || 0) + kfTransforms.position_y
      const baseScaleX = (clip.pip_scale_x ?? 1) * kfTransforms.scale_x
      const baseScaleY = (clip.pip_scale_y ?? 1) * kfTransforms.scale_y
      const baseRotation = (clip.pip_rotation || 0) + kfTransforms.rotation
      const baseOpacity = (clip.pip_opacity ?? 1) * kfTransforms.opacity

      const wipeInfo = getActiveWipe(clip, relativeTime, clipDuration)

      ctx.save()

      if (wipeInfo) {
        const region = getWipeClipRegion({ width, height }, wipeInfo.direction, wipeInfo.progress)
        ctx.beginPath()
        ctx.rect(region.x, region.y, region.w, region.h)
        ctx.clip()
      }

      const transitionAlpha = computeTransitionAlpha(clip, relativeTime)
      ctx.globalAlpha = baseOpacity * transitionAlpha
      ctx.translate(width / 2 + baseX, height / 2 + baseY)
      ctx.rotate((baseRotation * Math.PI) / 180)
      ctx.scale(baseScaleX, baseScaleY)

      const video = getOrCreateVideo(clip.media_id)
      try {
        if (Math.abs(video.currentTime - sourceTime) > 0.1) {
          video.currentTime = sourceTime
        }
        ctx.drawImage(video, -width / 2, -height / 2, width, height)
      } catch {
        ctx.fillStyle = '#333'
        ctx.fillRect(-width / 2, -height / 2, width, height)
        ctx.fillStyle = '#888'
        ctx.font = '24px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(`片段 #${clip.id}`, 0, 0)
      }

      ctx.restore()
    }

    ctx.fillStyle = 'rgba(255,255,255,0.7)'
    ctx.font = '14px monospace'
    ctx.textAlign = 'left'
    ctx.fillText(formatTimecode(time), 10, 20)
  }

  function getActiveWipe(clip, relativeTime, clipDuration) {
    if (!clip.transitions) return null
    for (const tr of clip.transitions) {
      if (!isWipeTransition(tr.type)) continue
      if (tr.position === 'start' && relativeTime < tr.duration) {
        return { direction: tr.type, progress: relativeTime / tr.duration }
      }
      if (tr.position === 'end') {
        const timeFromEnd = clipDuration - relativeTime
        if (timeFromEnd < tr.duration) {
          return { direction: tr.type, progress: timeFromEnd / tr.duration }
        }
      }
    }
    return null
  }

  function startPlayback() {
    store.isPlaying = true
    let lastTime = performance.now()

    audio.scheduleFullPlayback(store.playhead)

    function tick(now) {
      if (!store.isPlaying) return
      const delta = (now - lastTime) / 1000
      lastTime = now
      store.playhead += delta
      renderFrame(store.playhead)
      animFrameId = requestAnimationFrame(tick)
    }

    animFrameId = requestAnimationFrame(tick)
  }

  function stopPlayback() {
    store.isPlaying = false
    audio.stopAudioPlayback()
    if (animFrameId) {
      cancelAnimationFrame(animFrameId)
      animFrameId = null
    }
  }

  function seekTo(time) {
    store.playhead = Math.max(0, time)
    if (store.isPlaying) {
      audio.seekReschedule(store.playhead)
    }
    renderFrame(store.playhead)
  }

  function togglePlayback() {
    if (store.isPlaying) stopPlayback()
    else startPlayback()
  }

  return { renderFrame, startPlayback, stopPlayback, togglePlayback, switchProxyMode, seekTo, audio, setNotify }
}

function formatTimecode(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  const f = Math.floor((seconds % 1) * 30)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}:${String(f).padStart(2, '0')}`
}
