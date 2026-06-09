export function computeTransitionAlpha(clip, relativeTime) {
  const clipDuration = clip.out_point - clip.in_point
  let alpha = 1.0

  if (!clip.transitions) return alpha

  for (const tr of clip.transitions) {
    if (tr.position === 'start' && relativeTime < tr.duration) {
      const progress = relativeTime / tr.duration
      alpha *= applyTransitionCurve(progress, tr.type)
    }
    if (tr.position === 'end') {
      const timeFromEnd = clipDuration - relativeTime
      if (timeFromEnd < tr.duration) {
        const progress = timeFromEnd / tr.duration
        alpha *= applyTransitionCurve(progress, tr.type)
      }
    }
  }

  return alpha
}

function applyTransitionCurve(progress, type) {
  switch (type) {
    case 'fade_in':
    case 'fade_out':
      return progress
    case 'dissolve':
      return progress * progress * (3 - 2 * progress)
    case 'wipe_left':
    case 'wipe_right':
      return 1.0
    default:
      return progress
  }
}

export function isWipeTransition(type) {
  return type === 'wipe_left' || type === 'wipe_right'
}

export function getWipeClipRegion(size, direction, progress) {
  const { width, height } = size
  if (direction === 'wipe_left') {
    return { x: 0, y: 0, w: width * progress, h: height }
  }
  return { x: width * (1 - progress), y: 0, w: width * progress, h: height }
}

export const TRANSITION_TYPES = [
  { value: 'fade_in', label: '淡入' },
  { value: 'fade_out', label: '淡出' },
  { value: 'dissolve', label: '叠化' },
  { value: 'wipe_left', label: '左擦除' },
  { value: 'wipe_right', label: '右擦除' },
]
