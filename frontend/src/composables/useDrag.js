import { ref } from 'vue'

export function useDrag(options = {}) {
  const isDragging = ref(false)
  const startX = ref(0)
  const startY = ref(0)
  const deltaX = ref(0)
  const deltaY = ref(0)

  function onStart(event) {
    isDragging.value = true
    startX.value = event.clientX
    startY.value = event.clientY
    deltaX.value = 0
    deltaY.value = 0

    if (options.onStart) options.onStart(event)

    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onEnd)
    event.preventDefault()
  }

  function onMove(event) {
    if (!isDragging.value) return
    deltaX.value = event.clientX - startX.value
    deltaY.value = event.clientY - startY.value

    if (options.onMove) options.onMove(event, deltaX.value, deltaY.value)
  }

  function onEnd(event) {
    if (!isDragging.value) return
    isDragging.value = false

    if (options.onEnd) options.onEnd(event, deltaX.value, deltaY.value)

    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onEnd)
  }

  return { isDragging, startX, startY, deltaX, deltaY, onStart }
}
