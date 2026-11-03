<template>
  <div class="executive-summary-wrapper">
    <!-- Header Ringkasan Eksekutif -->
    <div class="eksum-hero-card">
      <div class="hero-badge-group">
        <span class="badge-type">RINGKASAN EKSEKUTIF</span>
        <span class="badge-id">ID: {{ reportId || 'N/A' }}</span>
        <span v-if="simulationId" class="badge-id">SIM: {{ simulationId }}</span>
      </div>
      <h2 class="hero-title">{{ displayData.title || title || 'Ringkasan Eksekutif Simulasi' }}</h2>
      <p class="hero-summary">{{ displayData.summary || summary || 'Analisis proyeksi strategis dan dinamika sosial berbasis simulasi multi-agen MiroFish.' }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="eksum-loading">
      <div class="spinner"></div>
      <span>Memuat data ringkasan eksekutif dinamis...</span>
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
              {{ displayData.metrics.risk_status || 'STATUS: RISIKO TINGGI' }}
            </span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">METRICS /swarms/sentiment-analysis/v2</p>
          <p class="description">
            {{ displayData.metrics.description || 'Pengukuran kuantitatif sentimen terpolarisasi, rasio resistensi aktif, dan proyeksi eskalasi publik.' }}
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
              <span class="config-item-value text-muted">{{ displayData.metrics.neutral_pct }}%</span>
            </div>
            <div class="config-item">
              <span class="config-item-label">Sentimen Mendukung</span>
              <span class="config-item-value text-success">{{ displayData.metrics.supportive_pct }}%</span>
            </div>
          </div>

          <!-- Spektrum Sentimen -->
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

          <!-- Arah Pergerakan & Fokus Gesekan -->
          <div class="sub-parameters-grid">
            <div class="sub-item">
              <span class="sub-key">Arah Pergerakan</span>
              <span class="sub-val">{{ displayData.metrics.movement_direction }}</span>
              <span class="sub-tag tag-orange">ESKALATIF</span>
            </div>
            <div class="sub-item">
              <span class="sub-key">Fokus Gesekan</span>
              <span class="sub-val">{{ displayData.metrics.friction_focus }}</span>
              <span class="sub-tag tag-red">KRITIS</span>
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
            Dinamika kausalitas utama dan hasil observasi yang menggerakkan respons publik serta pergeseran posisi antar-aktor.
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
            Identifikasi posisi, tingkat pengaruh, dan tuntutan esensial dari aktor-aktor sentral dalam jaringan simulasi.
          </p>

          <div class="stakeholder-grid">
            <div 
              v-for="(stk, idx) in displayData.stakeholders" 
              :key="idx" 
              class="stakeholder-card"
            >
              <div class="stk-top">
                <div class="stk-meta">
                  <span class="stk-category">{{ stk.category }}</span>
                  <h4 class="stk-name">{{ stk.name }}</h4>
                </div>
                <span :class="['stk-stance-pill', stk.stance_class || 'stance-opposing']">{{ stk.stance }}</span>
              </div>
              <div class="stk-metrics">
                <div class="stk-metric">
                  <span class="m-label">Bobot Pengaruh</span>
                  <span class="m-val">{{ stk.influence }}</span>
                </div>
                <div class="stk-metric">
                  <span class="m-label">Bias Sentimen</span>
                  <span :class="['m-val', Number(stk.sentiment) < 0 ? 'text-danger' : 'text-success']">
                    {{ stk.sentiment > 0 ? '+' : '' }}{{ stk.sentiment }}
                  </span>
                </div>
              </div>
              <div class="stk-concern">
                <span class="concern-label">Isu Pokok:</span>
                <span class="concern-text">{{ stk.concern }}</span>
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
            Panduan intervensi taktis dan komunikatif guna meredam friksi serta membangun kepatuhan sukarela.
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

      <!-- Section 05: Suara Lapangan / Kutipan Representatif -->
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
            Kutipan langsung dari interaksi percakapan agen yang mencerminkan sentimen dan persepsi autentik di lapangan.
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
                <span :class="['stk-stance-pill', q.stanceClass || 'stance-opposing']">{{ q.stance }}</span>
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

const fetchEksumData = async () => {
  if (!props.reportId) return
  loading.value = true
  try {
    const res = await getExecutiveSummary(props.reportId)
    if (res && res.data && res.data.success && res.data.data) {
      remoteData.value = res.data.data
    } else if (res && res.data && res.data.title) {
      remoteData.value = res.data
    }
  } catch (err) {
    console.warn('[ExecutiveSummary] Menggunakan fallback data prop:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchEksumData()
})

watch(() => props.reportId, (newId) => {
  if (newId) {
    fetchEksumData()
  }
})

const displayData = computed(() => {
  if (remoteData.value) {
    return remoteData.value
  }

  // Fallback jika API belum selesai atau offline
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
    opposing = Math.round(totalAgents * 0.55)
    neutral = Math.round(totalAgents * 0.30)
    supportive = totalAgents - opposing - neutral
  }

  const oppPct = Math.round((opposing / totalAgents) * 100)
  const supPct = Math.round((supportive / totalAgents) * 100)
  const neuPct = 100 - oppPct - supPct

  const bottomLine = (props.sections || []).slice(0, 5).map((sec, idx) => ({
    number: idx + 1,
    title: sec.title || `Temuan Bab ${idx + 1}`,
    severity: idx === 0 ? 'SEVERITY: HIGH' : idx === 1 ? 'IMPACT: DIRECT' : 'DYNAMIC: ACTIVE',
    badge_class: idx === 0 ? 'badge-danger' : idx === 1 ? 'badge-warning' : 'badge-primary',
    description: sec.content ? sec.content.slice(0, 160).replace(/[#*`]/g, '') + '...' : 'Analisis strategis berdasarkan observasi interaksi simulasi multi-agen.'
  }))

  const stakeholders = agentConfigs.slice(0, 4).map(a => ({
    name: a.entity_name || a.name || 'Aktor Simulasi',
    category: a.category || 'Organisasi',
    stance: (a.stance || 'OPPOSING').toUpperCase(),
    stance_class: `stance-${(a.stance || 'opposing').toLowerCase()}`,
    influence: a.influence ? a.influence.toFixed(1) : '2.5',
    sentiment: a.sentiment_bias ? a.sentiment_bias.toFixed(2) : '-0.20',
    concern: a.concern || 'Tuntutan kepatuhan, keadilan prosedural, dan transparansi kebijakan publik.'
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
        concern: 'Kekhawatiran terhadap akuntabilitas dan perlindungan hak-hak masyarakat.'
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
          description: 'Pertahankan jalur pelaporan publik yang terverifikasi dan berikan update berkala secara terstruktur.'
        }
      ]
    },
    quotes: []
  }
})
</script>

<style scoped>
.executive-summary-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.eksum-hero-card {
  background: #252830;
  border: 1px solid #363b47;
  border-radius: 8px;
  padding: 20px 24px;
}

.hero-badge-group {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.badge-type {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  background: #1890ff;
  color: #fff;
  letter-spacing: 0.5px;
}

.badge-id {
  font-size: 11px;
  color: #8c8c8c;
  font-family: monospace;
}

.hero-title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  line-height: 1.4;
  margin: 0 0 8px 0;
}

.hero-summary {
  font-size: 13px;
  color: #a0a6b5;
  line-height: 1.6;
  margin: 0;
}

.eksum-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  background: #252830;
  border: 1px solid #363b47;
  border-radius: 8px;
  color: #a0a6b5;
  font-size: 14px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #363b47;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Base Card Styling Matching MiroFish Theme */
.step-card {
  background: #252830;
  border: 1px solid #363b47;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #363b47;
  background: #1e222b;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  font-size: 16px;
  font-weight: 700;
  font-family: monospace;
  color: #fff;
}

.step-title {
  font-size: 15px;
  font-weight: 600;
  color: #e5e9f0;
}

.step-status .badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.badge.danger {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
  border: 1px solid rgba(245, 108, 108, 0.3);
}

.badge.warning {
  background: rgba(230, 162, 60, 0.15);
  color: #e6a23c;
  border: 1px solid rgba(230, 162, 60, 0.3);
}

.badge.success {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.badge.info {
  background: rgba(24, 144, 255, 0.15);
  color: #1890ff;
  border: 1px solid rgba(24, 144, 255, 0.3);
}

.card-content {
  padding: 20px;
}

.api-note {
  font-family: monospace;
  font-size: 11px;
  color: #7b8495;
  margin: 0 0 4px 0;
  letter-spacing: 0.5px;
}

.description {
  font-size: 13px;
  color: #a0a6b5;
  line-height: 1.5;
  margin: 0 0 20px 0;
}

/* Config Grid / Stat Cards */
.config-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.config-item {
  background: #1e222b;
  border: 1px solid #363b47;
  border-radius: 6px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-item-label {
  font-size: 11px;
  color: #8c96a8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.config-item-value {
  font-size: 20px;
  font-weight: 700;
  font-family: monospace;
}

.unit {
  font-size: 12px;
  font-weight: 400;
  color: #8c96a8;
}

.text-danger { color: #f56c6c; }
.text-warning { color: #e6a23c; }
.text-success { color: #67c23a; }
.text-muted { color: #a0a6b5; }
.text-primary { color: #1890ff; }

/* Spektrum Sentimen Bar */
.spectrum-box {
  background: #1e222b;
  border: 1px solid #363b47;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
}

.spectrum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.spectrum-title {
  font-size: 11px;
  font-weight: 700;
  color: #8c96a8;
  letter-spacing: 0.5px;
}

.spectrum-ratio {
  font-size: 12px;
  font-weight: 600;
  font-family: monospace;
  color: #e5e9f0;
}

.spectrum-bar {
  display: flex;
  height: 18px;
  border-radius: 4px;
  overflow: hidden;
  background: #14171d;
  margin-bottom: 12px;
}

.bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  transition: width 0.4s ease;
}

.bar-segment.critical { background: #e5484d; }
.bar-segment.neutral { background: #f5a623; }
.bar-segment.support { background: #30a46c; }

.spectrum-legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #8c96a8;
}

.legend-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.critical { background: #e5484d; }
.dot.neutral { background: #f5a623; }
.dot.support { background: #30a46c; }

/* Sub Parameters Grid */
.sub-parameters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.sub-item {
  background: #1e222b;
  border: 1px solid #363b47;
  border-radius: 6px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.sub-key {
  font-size: 11px;
  color: #8c96a8;
  min-width: 105px;
}

.sub-val {
  font-size: 12px;
  font-weight: 500;
  color: #e5e9f0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sub-tag {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.tag-orange {
  background: rgba(245, 166, 35, 0.15);
  color: #f5a623;
  border: 1px solid rgba(245, 166, 35, 0.3);
}

.tag-red {
  background: rgba(229, 72, 77, 0.15);
  color: #e5484d;
  border: 1px solid rgba(229, 72, 77, 0.3);
}

/* Findings List (Bottom Line) */
.findings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.finding-item {
  background: #1e222b;
  border: 1px solid #363b47;
  border-radius: 6px;
  padding: 14px 18px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.finding-num {
  font-size: 18px;
  font-weight: 700;
  font-family: monospace;
  color: #7b8495;
  line-height: 1.2;
}

.finding-body {
  flex: 1;
}

.finding-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.finding-title {
  font-size: 14px;
  font-weight: 600;
  color: #e5e9f0;
  margin: 0;
}

.finding-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  font-family: monospace;
}

.badge-danger {
  background: rgba(229, 72, 77, 0.15);
  color: #e5484d;
  border: 1px solid rgba(229, 72, 77, 0.3);
}

.badge-warning {
  background: rgba(245, 166, 35, 0.15);
  color: #f5a623;
  border: 1px solid rgba(245, 166, 35, 0.3);
}

.badge-primary {
  background: rgba(24, 144, 255, 0.15);
  color: #1890ff;
  border: 1px solid rgba(24, 144, 255, 0.3);
}

.finding-desc {
  font-size: 12.5px;
  color: #a0a6b5;
  line-height: 1.5;
  margin: 0;
}

/* Stakeholder Matrix */
.stakeholder-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.stakeholder-card {
  background: #1e222b;
  border: 1px solid #363b47;
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stk-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stk-category {
  font-size: 10px;
  color: #8c96a8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stk-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin: 2px 0 0 0;
}

.stk-stance-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  font-family: monospace;
}

.stance-opposing {
  background: rgba(229, 72, 77, 0.15);
  color: #e5484d;
  border: 1px solid rgba(229, 72, 77, 0.3);
}

.stance-supportive {
  background: rgba(48, 164, 108, 0.15);
  color: #30a46c;
  border: 1px solid rgba(48, 164, 108, 0.3);
}

.stance-neutral {
  background: rgba(140, 150, 168, 0.15);
  color: #a0a6b5;
  border: 1px solid rgba(140, 150, 168, 0.3);
}

.stk-metrics {
  display: flex;
  gap: 20px;
  padding: 8px 12px;
  background: #14171d;
  border-radius: 4px;
}

.stk-metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.m-label {
  font-size: 10px;
  color: #8c96a8;
}

.m-val {
  font-size: 13px;
  font-weight: 700;
  font-family: monospace;
  color: #fff;
}

.stk-concern {
  font-size: 12px;
  line-height: 1.4;
  color: #a0a6b5;
}

.concern-label {
  font-weight: 600;
  color: #8c96a8;
  margin-right: 4px;
}

/* Stop-Start-Continue Columns */
.action-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.action-col {
  background: #1e222b;
  border: 1px solid #363b47;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.action-col-header {
  padding: 12px 14px;
  background: #161920;
  border-bottom: 1px solid #363b47;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.col-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.pill-stop {
  background: rgba(229, 72, 77, 0.2);
  color: #e5484d;
}

.pill-start {
  background: rgba(24, 144, 255, 0.2);
  color: #1890ff;
}

.pill-continue {
  background: rgba(48, 164, 108, 0.2);
  color: #30a46c;
}

.col-count {
  font-size: 11px;
  color: #8c96a8;
  font-family: monospace;
}

.action-col-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  border-bottom: 1px solid #2a2f3a;
  padding-bottom: 10px;
}

.action-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.action-item-title {
  font-size: 13px;
  font-weight: 600;
  color: #e5e9f0;
  margin: 0 0 4px 0;
}

.action-item-desc {
  font-size: 12px;
  color: #a0a6b5;
  line-height: 1.4;
  margin: 0;
}

/* Quotes Grid */
.quotes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.quote-card {
  background: #1e222b;
  border: 1px solid #363b47;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
}

.quote-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quote-agent-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quote-agent-badge {
  font-size: 10px;
  font-weight: 700;
  background: #14171d;
  color: #8c96a8;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.quote-agent-name {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.quote-text {
  font-size: 12px;
  font-style: italic;
  color: #d8dee9;
  line-height: 1.5;
  margin: 0;
  padding-left: 10px;
  border-left: 2px solid #1890ff;
}

.quote-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  color: #8c96a8;
  padding-top: 6px;
  border-top: 1px solid #2a2f3a;
}

.quote-meta {
  font-family: monospace;
}

.quote-tag {
  color: #1890ff;
  font-family: monospace;
}

@media (max-width: 1200px) {
  .config-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .stakeholder-grid,
  .action-columns,
  .quotes-grid {
    grid-template-columns: 1fr;
  }
}
</style>
