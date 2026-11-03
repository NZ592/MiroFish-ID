<template>
  <nav class="workflow-nav" aria-label="Alur Kerja Simulasi">
    <button
      v-for="step in steps"
      :key="step.number"
      class="nav-step-btn"
      :class="{
        'is-active': currentStep === step.number,
        'is-enabled': step.enabled,
        'is-disabled': !step.enabled
      }"
      :disabled="!step.enabled"
      @click="goToStep(step.number)"
      :title="step.tooltip"
    >
      <span class="step-badge">
        <svg v-if="isStepPassed(step.number)" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span v-else>{{ step.number }}</span>
      </span>
      <span class="step-text">{{ step.label }}</span>
      <span v-if="step.number < 5" class="step-chevron">›</span>
    </button>
  </nav>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getSimulation } from '../api/simulation'
import { getReport, getReportBySimulation } from '../api/report'

const props = defineProps({
  currentStep: {
    type: Number,
    required: true
  },
  projectId: String,
  simulationId: String,
  reportId: String
})

const router = useRouter()
const { tm, t } = useI18n()

// Resolved IDs
const activeProjectId = ref(props.projectId || sessionStorage.getItem('mirofish_active_project_id') || '')
const activeSimulationId = ref(props.simulationId || sessionStorage.getItem('mirofish_active_simulation_id') || '')
const activeReportId = ref(props.reportId || sessionStorage.getItem('mirofish_active_report_id') || '')

// Sync with storage
const saveState = () => {
  if (activeProjectId.value) sessionStorage.setItem('mirofish_active_project_id', activeProjectId.value)
  if (activeSimulationId.value) sessionStorage.setItem('mirofish_active_simulation_id', activeSimulationId.value)
  if (activeReportId.value) sessionStorage.setItem('mirofish_active_report_id', activeReportId.value)
}

// Auto resolve missing links
const resolveMissingContext = async () => {
  // If we have reportId, get simulationId and projectId
  if (activeReportId.value && (!activeSimulationId.value || !activeProjectId.value)) {
    try {
      const res = await getReport(activeReportId.value)
      if (res.success && res.data) {
        if (!activeSimulationId.value && res.data.simulation_id) {
          activeSimulationId.value = res.data.simulation_id
        }
      }
    } catch (e) {
      // ignore
    }
  }

  // If we have simulationId, get projectId
  if (activeSimulationId.value && !activeProjectId.value) {
    try {
      const res = await getSimulation(activeSimulationId.value)
      if (res.success && res.data && res.data.project_id) {
        activeProjectId.value = res.data.project_id
      }
    } catch (e) {
      // ignore
    }
  }

  // If we have simulationId and need reportId
  if (activeSimulationId.value && !activeReportId.value) {
    try {
      const res = await getReportBySimulation(activeSimulationId.value)
      if (res.success && res.data && res.data.report_id) {
        activeReportId.value = res.data.report_id
      }
    } catch (e) {
      // ignore
    }
  }

  saveState()
}

watch(() => props.projectId, (val) => {
  if (val) {
    activeProjectId.value = val
    saveState()
  }
})

watch(() => props.simulationId, (val) => {
  if (val) {
    activeSimulationId.value = val
    saveState()
    resolveMissingContext()
  }
})

watch(() => props.reportId, (val) => {
  if (val) {
    activeReportId.value = val
    saveState()
    resolveMissingContext()
  }
})

onMounted(() => {
  resolveMissingContext()
})

const stepNames = computed(() => {
  const names = tm('main.stepNames') || []
  return [
    names[0] || 'Bangun Graf',
    names[1] || 'Siapkan Lingkungan',
    names[2] || 'Jalankan Simulasi',
    names[3] || 'Laporan Analisis',
    names[4] || 'Interaksi Mendalam'
  ]
})

const steps = computed(() => {
  return [
    {
      number: 1,
      label: stepNames.value[0],
      enabled: !!activeProjectId.value,
      tooltip: activeProjectId.value ? `Menuju Step 1: ${stepNames.value[0]}` : 'Step 1 belum tersedia'
    },
    {
      number: 2,
      label: stepNames.value[1],
      enabled: !!activeSimulationId.value,
      tooltip: activeSimulationId.value ? `Menuju Step 2: ${stepNames.value[1]}` : 'Step 2 belum tersedia'
    },
    {
      number: 3,
      label: stepNames.value[2],
      enabled: !!activeSimulationId.value,
      tooltip: activeSimulationId.value ? `Menuju Step 3: ${stepNames.value[2]}` : 'Step 3 belum tersedia'
    },
    {
      number: 4,
      label: stepNames.value[3],
      enabled: !!activeReportId.value,
      tooltip: activeReportId.value ? `Menuju Step 4: ${stepNames.value[3]}` : 'Step 4 membutuhkan simulasi selesai'
    },
    {
      number: 5,
      label: stepNames.value[4],
      enabled: !!activeReportId.value,
      tooltip: activeReportId.value ? `Menuju Step 5: ${stepNames.value[4]}` : 'Step 5 membutuhkan laporan terbuat'
    }
  ]
})

const isStepPassed = (stepNum) => {
  return stepNum < props.currentStep
}

const goToStep = (stepNum) => {
  if (stepNum === props.currentStep) return

  switch (stepNum) {
    case 1:
      if (activeProjectId.value) {
        router.push({ name: 'Process', params: { projectId: activeProjectId.value } })
      }
      break
    case 2:
      if (activeSimulationId.value) {
        router.push({ name: 'Simulation', params: { simulationId: activeSimulationId.value } })
      }
      break
    case 3:
      if (activeSimulationId.value) {
        router.push({ name: 'SimulationRun', params: { simulationId: activeSimulationId.value } })
      }
      break
    case 4:
      if (activeReportId.value) {
        router.push({ name: 'Report', params: { reportId: activeReportId.value } })
      }
      break
    case 5:
      if (activeReportId.value) {
        router.push({ name: 'Interaction', params: { reportId: activeReportId.value } })
      }
      break
  }
}
</script>

<style scoped>
.workflow-nav {
  display: inline-flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 3px 6px;
  gap: 2px;
}

.nav-step-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.nav-step-btn.is-enabled:hover:not(.is-active) {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.08);
}

.nav-step-btn.is-active {
  background: #2563eb;
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.35);
}

.nav-step-btn.is-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.12);
  color: inherit;
}

.nav-step-btn.is-active .step-badge {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.step-text {
  font-size: 12px;
  line-height: 1;
}

.step-chevron {
  font-size: 13px;
  color: #475569;
  margin-left: 4px;
}

@media (max-width: 1100px) {
  .step-text {
    display: none;
  }
  .nav-step-btn {
    padding: 4px 6px;
  }
}
</style>
