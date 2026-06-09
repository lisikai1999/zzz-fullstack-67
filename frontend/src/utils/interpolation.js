export function linear(t) {
  return t
}

export function easeIn(t) {
  return t * t
}

export function easeOut(t) {
  return t * (2 - t)
}

export function easeInOut(t) {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t
}

const EASING_MAP = {
  linear,
  ease_in: easeIn,
  ease_out: easeOut,
  ease_in_out: easeInOut,
}

export function applyEasing(t, type) {
  const fn = EASING_MAP[type] || linear
  return fn(Math.max(0, Math.min(1, t)))
}

export function interpolateValue(v1, v2, t, easing = 'linear') {
  const easedT = applyEasing(t, easing)
  return v1 + (v2 - v1) * easedT
}

export function interpolateKeyframes(keyframes, property, time) {
  const kfs = keyframes
    .filter(k => k.property === property)
    .sort((a, b) => a.time - b.time)

  if (kfs.length === 0) return getDefault(property)
  if (time <= kfs[0].time) return kfs[0].value
  if (time >= kfs[kfs.length - 1].time) return kfs[kfs.length - 1].value

  for (let i = 0; i < kfs.length - 1; i++) {
    if (time >= kfs[i].time && time < kfs[i + 1].time) {
      const t = (time - kfs[i].time) / (kfs[i + 1].time - kfs[i].time)
      return interpolateValue(kfs[i].value, kfs[i + 1].value, t, kfs[i + 1].easing)
    }
  }
  return kfs[kfs.length - 1].value
}

function getDefault(property) {
  switch (property) {
    case 'scale_x':
    case 'scale_y':
    case 'opacity':
      return 1
    case 'position_x':
    case 'position_y':
    case 'rotation':
      return 0
    default:
      return 0
  }
}

export function interpolateAllProperties(keyframes, time) {
  return {
    scale_x: interpolateKeyframes(keyframes, 'scale_x', time),
    scale_y: interpolateKeyframes(keyframes, 'scale_y', time),
    position_x: interpolateKeyframes(keyframes, 'position_x', time),
    position_y: interpolateKeyframes(keyframes, 'position_y', time),
    rotation: interpolateKeyframes(keyframes, 'rotation', time),
    opacity: interpolateKeyframes(keyframes, 'opacity', time),
  }
}
