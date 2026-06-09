import { store } from '../stores/project.js'

export function useTimeline() {
  function setPlayhead(time) {
    store.playhead = Math.max(0, time)
  }

  function timeToPixel(time) {
    return (time - store.scrollX) * store.zoom * store.pixelsPerSecond
  }

  function pixelToTime(px) {
    return px / (store.zoom * store.pixelsPerSecond) + store.scrollX
  }

  function setScrollFromPixel(scrollLeft) {
    store.scrollX = scrollLeft / (store.zoom * store.pixelsPerSecond)
  }

  function getPixelsPerSecond() {
    return store.zoom * store.pixelsPerSecond
  }

  return { setPlayhead, timeToPixel, pixelToTime, setScrollFromPixel, getPixelsPerSecond }
}
