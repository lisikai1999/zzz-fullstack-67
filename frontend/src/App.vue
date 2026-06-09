<template>
  <div class="app">
    <header class="app-header">
      <h1>视频剪辑工具</h1>
      <div class="project-controls">
        <button v-if="!store.project" @click="handleNewProject">新建项目</button>
        <span v-else class="project-name">{{ store.project.name }}</span>
      </div>
    </header>
    <div class="app-body">
      <div class="top-section">
        <VideoPreview />
        <PropertiesPanel />
      </div>
      <div class="bottom-section">
        <Timeline />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { store, loadProject, createProject } from './stores/project.js'
import { api } from './api/client.js'
import VideoPreview from './components/VideoPreview.vue'
import PropertiesPanel from './components/PropertiesPanel.vue'
import Timeline from './components/Timeline.vue'

onMounted(async () => {
  const projects = await api.listProjects()
  if (projects.length > 0) {
    await loadProject(projects[0].id)
  }
})

async function handleNewProject() {
  const name = prompt('项目名称:', '未命名项目')
  if (name) {
    await createProject(name)
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #1a1a2e;
  color: #e0e0e0;
  overflow: hidden;
  height: 100vh;
}

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: #16213e;
  border-bottom: 1px solid #2a2a4a;
}

.app-header h1 {
  font-size: 16px;
  font-weight: 600;
  color: #64ffda;
}

.project-controls button {
  padding: 6px 12px;
  background: #64ffda;
  color: #1a1a2e;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.project-name {
  font-size: 14px;
  color: #aaa;
}

.app-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-section {
  display: flex;
  height: 45%;
  min-height: 200px;
  border-bottom: 2px solid #2a2a4a;
}

.bottom-section {
  flex: 1;
  overflow: hidden;
}
</style>
