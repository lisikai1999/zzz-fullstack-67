const BASE = '/api'

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (res.status === 204) return null
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  // Projects
  listProjects: () => request('/projects'),
  createProject: (data) => request('/projects', { method: 'POST', body: JSON.stringify(data) }),
  getProject: (id) => request(`/projects/${id}`),
  updateProject: (id, data) => request(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' }),

  // Tracks
  createTrack: (projectId, data) => request(`/projects/${projectId}/tracks`, { method: 'POST', body: JSON.stringify(data) }),
  updateTrack: (id, data) => request(`/tracks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTrack: (id) => request(`/tracks/${id}`, { method: 'DELETE' }),

  // Clips
  createClip: (trackId, data) => request(`/tracks/${trackId}/clips`, { method: 'POST', body: JSON.stringify(data) }),
  updateClip: (id, data) => request(`/clips/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  splitClip: (id, splitTime) => request(`/clips/${id}/split`, { method: 'POST', body: JSON.stringify({ split_time: splitTime }) }),
  deleteClip: (id) => request(`/clips/${id}`, { method: 'DELETE' }),

  // Transitions
  createTransition: (clipId, data) => request(`/clips/${clipId}/transitions`, { method: 'POST', body: JSON.stringify(data) }),
  updateTransition: (id, data) => request(`/transitions/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTransition: (id) => request(`/transitions/${id}`, { method: 'DELETE' }),

  // Keyframes
  listKeyframes: (clipId) => request(`/clips/${clipId}/keyframes`),
  createKeyframe: (clipId, data) => request(`/clips/${clipId}/keyframes`, { method: 'POST', body: JSON.stringify(data) }),
  updateKeyframe: (id, data) => request(`/keyframes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteKeyframe: (id) => request(`/keyframes/${id}`, { method: 'DELETE' }),

  // Media
  uploadMedia: (projectId, file) => {
    const form = new FormData()
    form.append('project_id', projectId)
    form.append('file', file)
    return fetch(`${BASE}/media/upload`, { method: 'POST', body: form }).then(r => r.json())
  },
  getMedia: (id) => request(`/media/${id}`),
  mediaStreamUrl: (id) => `${BASE}/media/${id}/stream`,
  mediaProxyUrl: (id) => `${BASE}/media/${id}/proxy`,
}
