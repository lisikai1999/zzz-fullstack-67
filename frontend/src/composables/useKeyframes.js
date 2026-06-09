import { interpolateAllProperties } from '../utils/interpolation.js'

export function useKeyframes() {
  function getTransformAtTime(keyframes, time) {
    return interpolateAllProperties(keyframes || [], time)
  }

  return { getTransformAtTime }
}
