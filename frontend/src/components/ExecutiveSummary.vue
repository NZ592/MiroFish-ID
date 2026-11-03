<template>
  <div class="executive-summary-wrapper">
    <!-- Header Ringkasan Eksekutif -->
    <div class="eksum-hero-card">
      <div class="hero-top-row">
        <div class="hero-badge-group">
          <span class="badge-type">RINGKASAN EKSEKUTIF</span>
          <span class="badge-id">ID: {{ reportId || 'N/A' }}</span>
          <span v-if="simulationId" class="badge-id">SIM: {{ simulationId }}</span>
        </div>
        <button 
          class="btn-regenerate" 
          :disabled="loading" 
          @click="handleRegenerate"
          title="Sintesis ulang seluruh eksum menggunakan AI"
        >
          <span v-if="loading" class="btn-spinner"></span>
          <span v-else class="btn-icon">↺</span>
          {{ loading ? 'Menyintesis dengan AI...' : 'Regenerasi AI' }}
        </button>
      </div>

      <h2 class="hero-title">{{ displayData.title || title || 'Ringkasan Eksekutif Simulasi' }}</h2>
      <p class="hero-summary">{{ displayData.summary || summary || 'Analisis proyeksi strategis dan dinamika sosial berbasis simulasi multi-agen MiroFish.' }}</p>
    </div>

    <!-- Loading State Overlay -->
    <div v-if="loading && !remoteData" class="eksum-loading-card">
      <div class="spinner"></div>
      <div class="loading-text">
        <strong>Menyusun Ringkasan Eksekutif dengan AI...</strong>
        <span>Menganalisis perilaku agen, dinamika polarisasi, dan seluruh bab temuan simulasi.</span>
      </div>
    </div>

    <template v-else>
      <!-- Section 01: Indikator & Metrik Risiko -->
      <div class="step-card">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">01</span>
            <span class="step-title">Indeks Kerentanan Friksi Sosial & Polarisasi Opini</span>
          </div>
          <div class="step-status">
            <span :class="['badge', displayData.metrics.risk_class || 'danger']">
              {{ displayData.metrics.risk_status || 'STATUS: RISIKO TINGGI (70/100)' }}
            </span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">METRICS /swarms/sentiment-analysis/v2</p>
          <p class="description">
            {{ displayData.metrics.description || 'Pengukuran kuantitatif sentimen terpolarisasi, rasio resistensi aktif, dan proyeksi eskalasi publik dari simulasi multi-agen.' }}
          </p>

          <!-- 4 Stat Cards -->
          <div class="config-grid">
            <div class="config-item">
              <span class="config-item-label">Indeks Kerentanan</span>
              <span :class="['config-item-value', displayData.metrics.vulnerability_index >= 65 ? 'text-danger' : 'text-primary']">
                {{ displayData.metrics.vulnerability_index }} <small class="unit">/ 100</small>
              </span>
            </div>
            <div class="config-item">
              <span class="config-item-label">Sentimen Kritis / Penolakan</span>
              <span class="config-item-value text-danger">{{ displayData.metrics.opposing_pct }}%</span>
            </div>
            <div class="config-item">
              <span class="config-item-label">Sentimen Netral / Observasi</span>
              <span class="config-item-value text-neutral">{{ displayData.metrics.neutral_pct }}%</span>
            </div>
            <div class="config-item">
              <span class="config-item-label">Sentimen Mendukung</span>
              <span class="config-item-value text-success">{{ displayData.metrics.supportive_pct }}%</span>
            </div>
          </div>

          <!-- Spektrum Sentimen Bar -->
          <div class="spectrum-box">
            <div class="spectrum-header">
              <span class="spectrum-title">SPEKTRUM DISTRIBUSI SENTIMEN</span>
              <span class="spectrum-ratio">{{ displayData.metrics.ratio_text }}</span>
            </div>
            <div class="spectrum-bar">
              <div 
                class="bar-segment critical" 
                :style="{ width: displayData.metrics.opposing_pct + '%' }"
                :title="'Kritis: ' + displayData.metrics.opposing_pct + '%'"
              >
                {{ displayData.metrics.opposing_pct > 12 ? displayData.metrics.opposing_pct + '%' : '' }}
              </div>
              <div 
                class="bar-segment neutral" 
                :style="{ width: displayData.metrics.neutral_pct + '%' }"
                :title="'Netral: ' + displayData.metrics.neutral_pct + '%'"
              >
                {{ displayData.metrics.neutral_pct > 12 ? displayData.metrics.neutral_pct + '%' : '' }}
              </div>
              <div 
                class="bar-segment support" 
                :style="{ width: displayData.metrics.supportive_pct + '%' }"
                :title="'Mendukung: ' + displayData.metrics.supportive_pct + '%'"
              >
                {{ displayData.metrics.supportive_pct > 12 ? displayData.metrics.supportive_pct + '%' : '' }}
              </div>
            </div>
            <div class="spectrum-legend">
              <span class="legend-item"><span class="dot critical"></span> Kritis / Penolakan ({{ displayData.metrics.opposing_pct }}%)</span>
              <span class="legend-item"><span class="dot neutral"></span> Netral / Observasi ({{ displayData.metrics.neutral_pct }}%)</span>
              <span class="legend-item"><span class="dot support"></span> Mendukung ({{ displayData.metrics.supportive_pct }}%)</span>
            </div>
          </div>

          <!-- Arah Pergerakan & Fokus Gesekan: Teks Utuh Tanpa Terpotong -->
          <div class="sub-parameters-grid">
            <div class="sub-item">
              <div class="sub-item-header">
                <span class="sub-key">Arah Pergerakan</span>
                <span class="sub-tag tag-orange">ESKALATIF</span>
              </div>
              <p class="sub-val">{{ displayData.metrics.movement_direction }}</p>
            </div>
            <div class="sub-item">
              <div class="sub-item-header">
                <span class="sub-key">Fokus Gesekan</span>
                <span class="sub-tag tag-red">KRITIS</span>
              </div>
              <p class="sub-val">{{ displayData.metrics.friction_focus }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 02: Temuan Strategis Simulasi -->
      <div class="step-card">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">02</span>
            <span class="step-title">Temuan Strategis Simulasi (The Bottom Line)</span>
          </div>
          <div class="step-status">
            <span class="badge info">{{ displayData.bottom_line.length }} TEMUAN KUNCI</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">ANALYSIS /swarms/bottom-line-findings</p>
          <p class="description">
            Dinamika kausalitas utama dan temuan kritis yang menggerakkan pergeseran persepsi publik serta resistensi institusional.
          </p>

          <div class="findings-list">
            <div 
              v-for="(item, idx) in displayData.bottom_line" 
              :key="idx" 
              class="finding-item"
            >
              <div class="finding-num">{{ String(item.number || idx + 1).padStart(2, '0') }}</div>
              <div class="finding-body">
                <div class="finding-header">
                  <h4 class="finding-title">{{ item.title }}</h4>
                  <span :class="['finding-badge', item.badge_class || 'badge-danger']">{{ item.severity }}</span>
                </div>
                <p class="finding-desc">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 03: Matriks Pemangku Kepentingan -->
      <div class="step-card">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">03</span>
            <span class="step-title">Matriks Pemangku Kepentingan Utama & Titik Tekan</span>
          </div>
          <div class="step-status">
            <span class="badge warning">{{ displayData.stakeholders.length }} AKTOR KUNCI</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">STAKEHOLDERS /graph-rag/actor-matrix</p>
          <p class="description">
            Identifikasi posisi, bobot pengaruh, dan isu pokok tuntutan esensial dari aktor-aktor sentral dalam jaringan simulasi.
          </p>

          <div class="stakeholder-grid">
            <div 
              v-for="(stk, idx) in displayData.stakeholders" 
              :key="idx" 
              class="stakeholder-card"
            >
              <div class="stk-top">
                <div class="stk-meta">
                  <span class="stk-category">{{ stk.category || 'Aktor Simulasi' }}</span>
                  <h4 class="stk-name">{{ stk.name }}</h4>
                </div>
                <span :class="['stk-stance-pill', stk.stance_class || 'stance-opposing']">
                  {{ stk.stance }}
                </span>
              </div>

              <div class="stk-metrics">
                <div class="stk-metric">
                  <span class="m-label">Bobot Pengaruh</span>
                  <span class="m-val">{{ stk.influence }}</span>
                </div>
                <div class="stk-metric">
                  <span class="m-label">Bias Sentimen</span>
                  <span :class="['m-val', String(stk.sentiment).startsWith('-') ? 'text-danger' : 'text-success']">
                    {{ stk.sentiment }}
                  </span>
                </div>
              </div>

              <!-- Isu Pokok Terisi Penuh dari Hasil Analisis AI -->
              <div class="stk-concern-box">
                <span class="concern-label">ISU POKOK & TUNTUTAN:</span>
                <p class="concern-text">{{ stk.concern || 'Menuntut transparansi kebijakan, akuntabilitas prosedural, dan keterbukaan informasi publik.' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 04: Kerangka Tindakan Strategis (Stop - Start - Continue) -->
      <div class="step-card">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">04</span>
            <span class="step-title">Rekomendasi Tindakan Strategis (Stop - Start - Continue)</span>
          </div>
          <div class="step-status">
            <span class="badge success">PANDUAN INTERVENSI</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POLICY-RECOMMENDATION /matrix/intervention-framework</p>
          <p class="description">
            Panduan intervensi taktis dan komunikasi krisis berbasis hasil simulasi guna meredam friksi dan memulihkan kepercayaan publik.
          </p>

          <div class="action-columns">
            <!-- STOP Column -->
            <div class="action-col stop-col">
              <div class="action-col-header">
                <span class="col-pill pill-stop">HENTIKAN SEGERA</span>
                <span class="col-count">{{ displayData.recommendations.stop?.length || 0 }} Aksi</span>
              </div>
              <div class="action-col-body">
                <div 
                  v-for="(rec, idx) in displayData.recommendations.stop" 
                  :key="idx" 
                  class="action-item"
                >
                  <h5 class="action-item-title">{{ rec.title }}</h5>
                  <p class="action-item-desc">{{ rec.description }}</p>
                </div>
              </div>
            </div>

            <!-- START Column -->
            <div class="action-col start-col">
              <div class="action-col-header">
                <span class="col-pill pill-start">MULAI LAKUKAN</span>
                <span class="col-count">{{ displayData.recommendations.start?.length || 0 }} Aksi</span>
              </div>
              <div class="action-col-body">
                <div 
                  v-for="(rec, idx) in displayData.recommendations.start" 
                  :key="idx" 
                  class="action-item"
                >
                  <h5 class="action-item-title">{{ rec.title }}</h5>
                  <p class="action-item-desc">{{ rec.description }}</p>
                </div>
              </div>
            </div>

            <!-- CONTINUE Column -->
            <div class="action-col continue-col">
              <div class="action-col-header">
                <span class="col-pill pill-continue">PERTAHANKAN</span>
                <span class="col-count">{{ displayData.recommendations.continue_items?.length || 0 }} Aksi</span>
              </div>
              <div class="action-col-body">
                <div 
                  v-for="(rec, idx) in displayData.recommendations.continue_items" 
                  :key="idx" 
                  class="action-item"
                >
                  <h5 class="action-item-title">{{ rec.title }}</h5>
                  <p class="action-item-desc">{{ rec.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 05: Suara Lapangan / Kutipan Representatif Agen -->
      <div v-if="displayData.quotes && displayData.quotes.length > 0" class="step-card">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">05</span>
            <span class="step-title">Suara Lapangan & Kutipan Representatif Agen</span>
          </div>
          <div class="step-status">
            <span class="badge info">{{ displayData.quotes.length }} KUTIPAN KUNCI</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">EVIDENCE /simulation-logs/agent-dialogues</p>
          <p class="description">
            Kutipan representatif dari percakapan simulasi multi-agen yang mencerminkan eskalasi sikap dan dinamika lapangan.
          </p>

          <div class="quotes-grid">
            <div 
              v-for="(q, idx) in displayData.quotes" 
              :key="idx" 
              class="quote-card"
            >
              <div class="quote-header">
                <div class="quote-agent-info">
                  <span class="quote-agent-badge">{{ q.agent_id }}</span>
                  <span class="quote-agent-name">{{ q.agent_name }}</span>
                </div>
                <span :class="['stk-stance-pill', q.stanceClass || 'stance-opposing']">
                  {{ q.stance }}
                </span>
              </div>
              <blockquote class="quote-text">
                "{{ q.quote }}"
              </blockquote>
              <div class="quote-footer">
                <span class="quote-meta">Ronde {{ q.round }} | Sentimen: {{ q.sentiment }}</span>
                <span class="quote-tag">{{ q.topic }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getExecutiveSummary } from '../api/report'

const props = defineProps({
  reportId: {
    type: String,
    default: ''
  },
  simulationId: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  summary: {
    type: String,
    default: ''
  },
  sections: {
    type: Array,
    default: () => []
  },
  simulationConfig: {
    type: Object,
    default: () => ({})
  }
})

const loading = ref(false)
const remoteData = ref(null)

const fetchEksumData = async (refresh = false) => {
  if (!props.reportId) return
  loading.value = true
  try {
    const res = await getExecutiveSummary(props.reportId, refresh)
    if (res && res.data && res.data.success && res.data.data) {
      remoteData.value = res.data.data
    } else if (res && res.data && res.data.title) {
      remoteData.value = res.data
    }
  } catch (err) {
    console.warn('[ExecutiveSummary] Menggunakan data lokal/prop:', err)
  } finally {
    loading.value = false
  }
}

const handleRegenerate = () => {
  fetchEksumData(true)
}

onMounted(() => {
  fetchEksumData(false)
})

watch(() => props.reportId, (newId) => {
  if (newId) {
    fetchEksumData(false)
  }
})

const displayData = computed(() => {
  if (remoteData.value) {
    return remoteData.value
  }

  // Fallback prop jika API belum merespons
  const totalRounds = props.simulationConfig?.time_config?.total_rounds || 40
  const agentConfigs = props.simulationConfig?.agent_configs || []
  const totalAgents = agentConfigs.length || 20

  let opposing = 0
  let supportive = 0
  let neutral = 0

  agentConfigs.forEach(a => {
    const st = (a.stance || '').toLowerCase()
    const bias = a.sentiment_bias || 0
    if (st === 'opposing' || bias < -0.15) opposing++
    else if (st === 'supportive' || bias > 0.15) supportive++
    else neutral++
  })

  if (agentConfigs.length === 0) {
    opposing = Math.round(totalAgents * 0.58)
    neutral = Math.round(totalAgents * 0.22)
    supportive = totalAgents - opposing - neutral
  }

  const oppPct = Math.round((opposing / totalAgents) * 100)
  const supPct = Math.round((supportive / totalAgents) * 100)
  const neuPct = 100 - oppPct - supPct

  const bottomLine = (props.sections || []).slice(0, 5).map((sec, idx) => ({
    number: idx + 1,
    title: sec.title || `Temuan Strategis Bab ${idx + 1}`,
    severity: idx === 0 ? 'SEVERITY: HIGH' : idx === 1 ? 'IMPACT: DIRECT' : 'DYNAMIC: ACTIVE',
    badge_class: idx === 0 ? 'badge-danger' : idx === 1 ? 'badge-warning' : 'badge-primary',
    description: sec.content ? sec.content.slice(0, 160).replace(/[#*`]/g, '') + '...' : 'Analisis mendalam terhadap respon aktor dan jalur propagasi isu berdasarkan observasi simulasi multi-agen.'
  }))

  const stakeholders = agentConfigs.slice(0, 4).map((a, idx) => ({
    name: a.entity_name || a.name || `Aktor Kunci ${idx + 1}`,
    category: a.category || 'Organisasi / Institusi',
    stance: (a.stance || 'OPPOSING').toUpperCase(),
    stance_class: `stance-${(a.stance || 'opposing').toLowerCase()}`,
    influence: a.influence ? a.influence.toFixed(1) : '2.8',
    sentiment: a.sentiment_bias ? a.sentiment_bias.toFixed(2) : '-0.25',
    concern: a.concern || 'Menuntut transparansi kebijakan, keterbukaan bukti forensik, dan akuntabilitas prosedural menyeluruh.'
  }))

  return {
    title: props.title || 'Ringkasan Eksekutif Simulasi',
    summary: props.summary || 'Proyeksi strategis dinamika opini dan respon publik berbasis simulasi OASIS.',
    metrics: {
      vulnerability_index: 70,
      risk_status: 'STATUS: RISIKO TINGGI (70/100)',
      risk_class: 'danger',
      opposing_pct: oppPct,
      neutral_pct: neuPct,
      supportive_pct: supPct,
      ratio_text: `${oppPct}% Kritis : ${neuPct}% Netral : ${supPct}% Dukung`,
      movement_direction: props.sections?.[0]?.title || 'Eskalasi Resistensi Terorganisir',
      friction_focus: props.sections?.[1]?.title || 'Krisis Kepercayaan & Tuntutan Transparansi Kebijakan',
      description: `Pengukuran kuantitatif sentimen terpolarisasi, rasio resistensi aktif, dan proyeksi eskalasi publik dari simulasi multi-agen berskala ${totalRounds} ronde.`
    },
    bottom_line: bottomLine.length > 0 ? bottomLine : [
      {
        number: 1,
        title: 'Polarisasi Respons Publik dan Resistensi Awal',
        severity: 'SEVERITY: HIGH',
        badge_class: 'badge-danger',
        description: 'Kebijakan yang diuji memicu resistensi langsung di kluster kritis akibat belum tersosialisasikannya kerangka regulasi secara transparan.'
      }
    ],
    stakeholders: stakeholders.length > 0 ? stakeholders : [
      {
        name: 'Masyarakat Sipil & Pengamat',
        category: 'Publik',
        stance: 'OPPOSING',
        stance_class: 'stance-opposing',
        influence: '2.8',
        sentiment: '-0.45',
        concern: 'Kekhawatiran terhadap akuntabilitas prosedural dan jaminan perlindungan hak-hak masyarakat.'
      }
    ],
    recommendations: {
      stop: [
        {
          title: 'Narasi Defensif Sepihak',
          description: 'Hentikan klarifikasi sepihak tanpa didukung pembuktian data forensik yang dapat diverifikasi publik.'
        }
      ],
      start: [
        {
          title: 'Audit Forensik Independen',
          description: 'Bentuk tim ad-hoc independen yang melibatkan perwakilan masyarakat sipil dan pakar terpercaya.'
        }
      ],
      continue_items: [
        {
          title: 'Komunikasi Proaktif Terbuka',
          description: 'Pertahankan jalur pelaporan publik yang terverifikasi dan berikan pembaruan secara berkala.'
        }
      ]
    },
    quotes: []
  }
})
</script>

<style scoped>
/* ==========================================================================
   MiroFish Native Light Theme Design System (Responsive & Non-Truncated)
   Matches Step 1-3, White Cards, Crisp Borders, Clean Typography
   ========================================================================== */
.executive-summary-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  color: #111827;
  padding-bottom: 30px;
  container-type: inline-size;
  container-name: eksum-container;
}

/* Hero / Header Brief Card */
.eksum-hero-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 22px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.hero-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
}

.hero-badge-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.badge-type {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  background: #000000;
  color: #ffffff;
  letter-spacing: 0.5px;
}

.badge-id {
  font-size: 11px;
  color: #6b7280;
  font-family: 'JetBrains Mono', monospace;
  word-break: break-all;
}

.btn-regenerate {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  background: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-regenerate:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #111827;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-regenerate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 14px;
  line-height: 1;
}

.btn-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.hero-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  line-height: 1.45;
  margin: 0 0 10px 0;
  word-break: break-word;
}

.hero-summary {
  font-size: 13.5px;
  color: #374151;
  line-height: 1.7;
  margin: 0;
  word-break: break-word;
}

/* Loading Card */
.eksum-loading-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 30px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.loading-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.loading-text strong {
  font-size: 14px;
  color: #111827;
}

.loading-text span {
  font-size: 12.5px;
  color: #6b7280;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Base Step Card - MiroFish White Theme */
.step-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  transition: all 0.2s ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  background: #ffffff;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 220px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px;
  font-weight: 700;
  color: #000000;
  line-height: 1;
}

.step-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  letter-spacing: 0.2px;
  line-height: 1.4;
}

/* Status Badges */
.step-status .badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  white-space: nowrap;
}

.badge.danger {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.badge.warning {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}

.badge.success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.badge.info {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.card-content {
  padding: 20px;
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #6b7280;
  margin: 0 0 6px 0;
  letter-spacing: 0.5px;
}

.description {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.6;
  margin: 0 0 20px 0;
  word-break: break-word;
}

/* Section 01: Config Grid / Stat Cards */
.config-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.config-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-item-label {
  font-size: 11px;
  color: #6b7280;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
  line-height: 1.3;
}

.config-item-value {
  font-size: 22px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.2;
}

.unit {
  font-size: 12px;
  font-weight: 400;
  color: #9ca3af;
}

.text-danger { color: #dc2626; }
.text-warning { color: #d97706; }
.text-success { color: #16a34a; }
.text-neutral { color: #4b5563; }
.text-primary { color: #2563eb; }

/* Spektrum Sentimen Bar */
.spectrum-box {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
}

.spectrum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.spectrum-title {
  font-size: 11px;
  font-weight: 700;
  color: #374151;
  letter-spacing: 0.5px;
}

.spectrum-ratio {
  font-size: 12px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: #111827;
}

.spectrum-bar {
  display: flex;
  height: 16px;
  border-radius: 4px;
  overflow: hidden;
  background: #e5e7eb;
  margin-bottom: 12px;
}

.bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: #ffffff;
  transition: width 0.4s ease;
}

.bar-segment.critical { background: #ef4444; }
.bar-segment.neutral { background: #f59e0b; }
.bar-segment.support { background: #10b981; }

.spectrum-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: #4b5563;
}

.legend-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot.critical { background: #ef4444; }
.dot.neutral { background: #f59e0b; }
.dot.support { background: #10b981; }

/* Sub Parameters Grid - Teks Lengkap Tanpa Ellipsis */
.sub-parameters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.sub-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sub-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.sub-key {
  font-size: 11.5px;
  color: #6b7280;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sub-val {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  line-height: 1.55;
  margin: 0;
  word-break: break-word;
  white-space: normal;
  overflow: visible;
}

.sub-tag {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.tag-orange {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}

.tag-red {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

/* Section 02: Findings List (Bottom Line) */
.findings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.finding-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px 20px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  transition: all 0.2s ease;
}

.finding-item:hover {
  background: #ffffff;
  border-color: #cbd5e1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.finding-num {
  font-size: 18px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: #9ca3af;
  line-height: 1.2;
  flex-shrink: 0;
}

.finding-body {
  flex: 1;
  min-width: 0;
}

.finding-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 8px;
}

.finding-title {
  font-size: 14.5px;
  font-weight: 700;
  color: #111827;
  line-height: 1.45;
  margin: 0;
  flex: 1;
  word-break: break-word;
}

.finding-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
  flex-shrink: 0;
}

.badge-danger {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.badge-warning {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}

.badge-primary {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.finding-desc {
  font-size: 13px;
  color: #374151;
  line-height: 1.65;
  margin: 0;
  word-break: break-word;
}

/* Section 03: Stakeholder Matrix */
.stakeholder-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stakeholder-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.2s ease;
}

.stakeholder-card:hover {
  background: #ffffff;
  border-color: #cbd5e1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.stk-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.stk-meta {
  flex: 1;
  min-width: 0;
}

.stk-category {
  font-size: 10.5px;
  color: #6b7280;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
  display: block;
}

.stk-name {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  margin: 2px 0 0 0;
  line-height: 1.35;
  word-break: break-word;
}

.stk-stance-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
  flex-shrink: 0;
}

.stance-opposing {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.stance-supportive {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.stance-neutral {
  background: #f3f4f6;
  color: #4b5563;
  border: 1px solid #e5e7eb;
}

.stance-observer {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.stk-metrics {
  display: flex;
  gap: 20px;
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
}

.stk-metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.m-label {
  font-size: 10.5px;
  color: #6b7280;
}

.m-val {
  font-size: 13px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: #111827;
}

/* Isu Pokok Box - Terisi Penuh dari Hasil AI */
.stk-concern-box {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 10px 12px;
}

.concern-label {
  font-size: 10.5px;
  font-weight: 700;
  color: #4b5563;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
  display: block;
}

.concern-text {
  font-size: 12.5px;
  color: #1f2937;
  line-height: 1.55;
  margin: 0;
  word-break: break-word;
}

/* Section 04: Stop-Start-Continue Columns */
.action-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.action-col {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.action-col-header {
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.stop-col .action-col-header {
  background: #fef2f2;
  border-bottom: 1px solid #fecaca;
}

.start-col .action-col-header {
  background: #eff6ff;
  border-bottom: 1px solid #bfdbfe;
}

.continue-col .action-col-header {
  background: #f0fdf4;
  border-bottom: 1px solid #bbf7d0;
}

.col-pill {
  font-size: 10.5px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.pill-stop {
  background: #fee2e2;
  color: #b91c1c;
}

.pill-start {
  background: #dbeafe;
  color: #1d4ed8;
}

.pill-continue {
  background: #dcfce7;
  color: #15803d;
}

.col-count {
  font-size: 11px;
  color: #6b7280;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  white-space: nowrap;
}

.action-col-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #ffffff;
  flex: 1;
}

.action-item {
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 12px;
}

.action-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.action-item-title {
  font-size: 13px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px 0;
  line-height: 1.4;
  word-break: break-word;
}

.action-item-desc {
  font-size: 12px;
  color: #4b5563;
  line-height: 1.55;
  margin: 0;
  word-break: break-word;
}

/* Section 05: Quotes Grid */
.quotes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.quote-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 12px;
  transition: all 0.2s ease;
}

.quote-card:hover {
  background: #ffffff;
  border-color: #cbd5e1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.quote-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.quote-agent-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.quote-agent-badge {
  font-size: 10px;
  font-weight: 700;
  background: #ffffff;
  border: 1px solid #d1d5db;
  color: #374151;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
  flex-shrink: 0;
}

.quote-agent-name {
  font-size: 12.5px;
  font-weight: 700;
  color: #111827;
  word-break: break-word;
}

.quote-text {
  font-size: 12px;
  font-style: italic;
  color: #1f2937;
  line-height: 1.6;
  margin: 0;
  padding: 8px 12px;
  background: #ffffff;
  border-radius: 0 4px 4px 0;
  border-left: 3px solid #2563eb;
  word-break: break-word;
}

.quote-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 10.5px;
  color: #6b7280;
  padding-top: 6px;
  border-top: 1px solid #e5e7eb;
}

.quote-meta {
  font-family: 'JetBrains Mono', monospace;
}

.quote-tag {
  color: #2563eb;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  word-break: break-all;
}

/* ==========================================================================
   Container Queries & Responsive Layout
   Adapts perfectly whether full-screen or side-by-side in "Bagi Dua" workspace
   ========================================================================== */
@container eksum-container (max-width: 820px) {
  .config-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .sub-parameters-grid {
    grid-template-columns: 1fr;
  }
  .stakeholder-grid {
    grid-template-columns: 1fr;
  }
  .action-columns {
    grid-template-columns: 1fr;
  }
  .quotes-grid {
    grid-template-columns: 1fr;
  }
}

@container eksum-container (max-width: 480px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}

/* Media Query Fallbacks for Browsers */
@media (max-width: 1024px) {
  .config-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .sub-parameters-grid,
  .stakeholder-grid,
  .action-columns,
  .quotes-grid {
    grid-template-columns: 1fr;
  }
}
</style>
