<template>
  <div class="executive-summary-wrapper">
    <!-- Section 01: Indikator & Metrik Risiko -->
    <div class="step-card">
      <div class="card-header">
        <div class="step-info">
          <span class="step-num">01</span>
          <span class="step-title">Indeks Kerentanan Friksi Sosial & Polarisasi Opini</span>
        </div>
        <div class="step-status">
          <span class="badge danger">STATUS: RISIKO TINGGI (78/100)</span>
        </div>
      </div>

      <div class="card-content">
        <p class="api-note">METRICS /swarms/sentiment-analysis/v2</p>
        <p class="description">
          Pengukuran kuantitatif sentimen terpolarisasi, rasio resistensi aktif, dan proyeksi eskalasi publik dari simulasi multi-agen berskala 35 ronde.
        </p>

        <!-- Config Grid (4 Stat Cards) -->
        <div class="config-grid">
          <div class="config-item">
            <span class="config-item-label">Indeks Kerentanan</span>
            <span class="config-item-value text-danger">78 <small class="unit">/ 100</small></span>
          </div>
          <div class="config-item">
            <span class="config-item-label">Sentimen Kritis / Penolakan</span>
            <span class="config-item-value text-danger">64.0%</span>
          </div>
          <div class="config-item">
            <span class="config-item-label">Sentimen Netral / Observasi</span>
            <span class="config-item-value text-neutral">21.0%</span>
          </div>
          <div class="config-item">
            <span class="config-item-label">Sentimen Mendukung</span>
            <span class="config-item-value text-success">15.0%</span>
          </div>
        </div>

        <!-- Polarization Spectrum Bar -->
        <div class="spectrum-container">
          <div class="spectrum-header">
            <span class="spectrum-title">SPEKTRUM DISTRIBUSI SENTIMEN</span>
            <span class="spectrum-ratio">64% Kritis : 21% Netral : 15% Dukung</span>
          </div>
          <div class="spectrum-bar">
            <div class="seg seg-danger" style="width: 64%" title="Kritis / Resisten: 64%">64%</div>
            <div class="seg seg-warning" style="width: 21%" title="Netral / Mengamati: 21%">21%</div>
            <div class="seg seg-success" style="width: 15%" title="Mendukung: 15%">15%</div>
          </div>
          <div class="spectrum-legend">
            <span class="legend-item"><span class="dot dot-danger"></span>Kritis / Resisten (64%)</span>
            <span class="legend-item"><span class="dot dot-warning"></span>Netral / Observasi (21%)</span>
            <span class="legend-item"><span class="dot dot-success"></span>Mendukung (15%)</span>
          </div>
        </div>

        <!-- Dynamic Rows -->
        <div class="time-periods">
          <div class="period-item">
            <span class="period-label">Arah Pergerakan</span>
            <span class="period-hours">Eskalasi Resistensi Terorganisir (Potensi Boikot Belanja Digital)</span>
            <span class="period-multiplier badge-warning">ESKALATIF</span>
          </div>
          <div class="period-item">
            <span class="period-label">Fokus Gesekan</span>
            <span class="period-hours">Penerusan Beban Harga ke Konsumen Akhir (Price Pass-Through)</span>
            <span class="period-multiplier badge-danger">KRITIS</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 02: Temuan Kunci Simulasi -->
    <div class="step-card">
      <div class="card-header">
        <div class="step-info">
          <span class="step-num">02</span>
          <span class="step-title">Temuan Strategis Simulasi (The Bottom Line)</span>
        </div>
        <div class="step-status">
          <span class="badge primary">3 TEMUAN KUNCI</span>
        </div>
      </div>

      <div class="card-content">
        <p class="api-note">ANALYSIS /swarms/bottom-line-findings</p>
        <p class="description">
          Tiga dinamika kausalitas utama yang menggerakkan resistensi publik dan pergeseran opini lintas kluster.
        </p>

        <div class="time-periods">
          <div class="period-item interactive-row">
            <div class="row-num mono">01</div>
            <div class="row-content">
              <div class="row-title">Jurang Resonansi (Klarifikasi Teknis Dibalikkan Menjadi Beban Rakyat)</div>
              <div class="row-desc">
                Penjelasan normatif mengenai penegakan aturan dan kesetaraan berusaha gagal meredam sinisme publik. Di media sosial, pesan resmi justru dibingkai ulang sebagai upaya menutup defisit anggaran dengan menekan ekonomi masyarakat kecil.
              </div>
            </div>
            <span class="period-multiplier badge-danger">SEVERITY: HIGH</span>
          </div>

          <div class="period-item interactive-row">
            <div class="row-num mono">02</div>
            <div class="row-content">
              <div class="row-title">Efek Price Pass-Through (Beban Biaya Dialihkan ke Konsumen Akhir)</div>
              <div class="row-desc">
                Pelaku usaha bermargin tipis tidak menyerap pemotongan biaya sendiri, melainkan langsung menaikkan harga etalase sebesar 5–10%. Dampaknya, isu kepatuhan fiskal bertransformasi menjadi krisis daya beli masyarakat kelas menengah.
              </div>
            </div>
            <span class="period-multiplier badge-warning">IMPACT: DIRECT</span>
          </div>

          <div class="period-item interactive-row">
            <div class="row-num mono">03</div>
            <div class="row-content">
              <div class="row-title">Konvergensi Koalisi (Meleburnya Suara Pedagang dan Pembeli)</div>
              <div class="row-desc">
                Keluhan pedagang daring mengenai margin tipis bertemu dengan kemarahan konsumen atas kenaikan harga. Kedua kelompok ini melebur membentuk koalisi penolakan yang diperkuat tagar viral di ruang percakapan publik.
              </div>
            </div>
            <span class="period-multiplier badge-primary">DYNAMIC: ACTIVE</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 03: Pemetaan 4 Kubu Stakeholder -->
    <div class="step-card">
      <div class="card-header">
        <div class="step-info">
          <span class="step-num">03</span>
          <span class="step-title">Pemetaan Sikap & Polarisasi Kluster Stakeholder</span>
        </div>
        <div class="step-status">
          <span class="badge neutral">{{ filteredStakeholders.length }} KELOMPOK</span>
        </div>
      </div>

      <div class="card-content">
        <p class="api-note">MATRIX /swarms/stakeholder-clusters</p>
        <p class="description">
          Segmentasi kelompok aktor simulasi, distribusi sikap penolakan/dukungan, dan parameter pengaruh sosial.
        </p>

        <!-- Interactive Cluster Filter Bar -->
        <div class="cluster-filter-bar">
          <button 
            v-for="filter in stanceFilters" 
            :key="filter.key"
            class="filter-pill"
            :class="{ 'active': activeStanceFilter === filter.key }"
            @click="activeStanceFilter = filter.key"
          >
            {{ filter.label }}
          </button>
        </div>

        <!-- 2-Column Agent Style Cards -->
        <div class="agents-cards">
          <div 
            v-for="stk in filteredStakeholders" 
            :key="stk.id"
            class="agent-card"
            :class="{ 'card-highlighted': selectedCluster === stk.id }"
            @click="toggleSelectCluster(stk.id)"
          >
            <div class="agent-card-header">
              <div class="agent-identity">
                <span class="agent-id">Cluster {{ stk.clusterId }}</span>
                <span class="agent-name">{{ stk.name }}</span>
              </div>
              <div class="agent-tags">
                <span class="agent-type">{{ stk.type }}</span>
                <span class="agent-stance" :class="stk.stanceClass">{{ stk.stance }}</span>
              </div>
            </div>

            <p class="cluster-narrative">{{ stk.narrative }}</p>

            <div class="agent-params">
              <div class="param-group">
                <div class="param-item">
                  <span class="param-label">Pangsa Resonansi</span>
                  <div class="param-value with-bar">
                    <span class="mini-bar" :style="{ width: stk.resonanceWidth }"></span>
                    <span>{{ stk.resonance }}</span>
                  </div>
                </div>
                <div class="param-item">
                  <span class="param-label">Bias Sentimen</span>
                  <span class="param-value" :class="stk.sentimentClass">{{ stk.sentiment }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">Skor Pengaruh</span>
                  <span class="param-value highlight">{{ stk.influence }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 04: Titik Kritis Friksi Sosial -->
    <div class="step-card">
      <div class="card-header">
        <div class="step-info">
          <span class="step-num">04</span>
          <span class="step-title">Titik Kritis Friksi Sosial (Key Social Tipping Points)</span>
        </div>
        <div class="step-status">
          <span class="badge warning">3 TAHAPAN KRITIS</span>
        </div>
      </div>

      <div class="card-content">
        <p class="api-note">CHRONOLOGY /simulation-events/tipping-points</p>
        <p class="description">
          Tahapan krusial dalam simulasi yang memicu lonjakan eskalasi penolakan dan pergeseran sentimen publik secara masif.
        </p>

        <div class="time-periods">
          <div class="period-item interactive-row">
            <span class="period-label mono">TAHAP 01</span>
            <div class="row-content">
              <div class="row-title">Aktivasi Pemotongan Otomatis Serentak</div>
              <div class="row-desc">
                Saat pemotongan serentak pertama kali dirasakan di dasbor transaksi, pedagang langsung bereaksi emosional dan membagikan tangkapan layar penyesuaian margin ke komunitas publik.
              </div>
            </div>
            <span class="period-multiplier badge-danger">PEMICU AWAL</span>
          </div>

          <div class="period-item interactive-row">
            <span class="period-label mono">TAHAP 02</span>
            <div class="row-content">
              <div class="row-title">Penerusan Beban Harga ke Etalase Pembeli</div>
              <div class="row-desc">
                Kenaikan harga barang di etalase daring langsung menyulut kemarahan konsumen kelas menengah, yang kemudian mengorganisir tagar protes dan memicu narasi boikot belanja.
              </div>
            </div>
            <span class="period-multiplier badge-warning">AMPLIFIKASI</span>
          </div>

          <div class="period-item interactive-row">
            <span class="period-label mono">TAHAP 03</span>
            <div class="row-content">
              <div class="row-title">Kepanikan Notifikasi & Kerahasiaan Data (UU PDP)</div>
              <div class="row-desc">
                Notifikasi administratif otomatis menimbulkan kecemasan penyalahgunaan data perbankan, mendorong desakan uji publik dari praktisi hukum dan masyarakat sipil.
              </div>
            </div>
            <span class="period-multiplier badge-primary">SENGKETA REGULASI</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 05: Rekomendasi Tindakan Strategis -->
    <div class="step-card">
      <div class="card-header">
        <div class="step-info">
          <span class="step-num">05</span>
          <span class="step-title">Rekomendasi Tindakan Strategis bagi Pengambil Keputusan</span>
        </div>
        <div class="step-status">
          <span class="badge success">ACTION FRAMEWORK</span>
        </div>
      </div>

      <div class="card-content">
        <p class="api-note">POLICY /action-framework/stop-start-continue</p>
        <p class="description">
          Pedoman mitigasi berbasis bukti simulasi untuk mencegah boikot transaksi dan memulihkan kepatuhan sukarela.
        </p>

        <div class="action-columns">
          <!-- STOP -->
          <div class="action-card card-stop">
            <div class="action-card-header">
              <span class="badge danger">STOP (HENTIKAN)</span>
              <span class="action-meta">Tindakan Kontraproduktif</span>
            </div>
            <ul class="action-list">
              <li>Hentikan komunikasi satu arah yang bernada defensif atau memojokkan pelaku usaha kecil.</li>
              <li>Hentikan desakan kepatuhan administratif serentak tanpa masa sosialisasi dan pendampingan teknis.</li>
            </ul>
          </div>

          <!-- START -->
          <div class="action-card card-start">
            <div class="action-card-header">
              <span class="badge primary">START (MULAI LAKUKAN)</span>
              <span class="action-meta">Langkah Kunci Baru</span>
            </div>
            <ul class="action-list">
              <li>Terapkan batas ambang omzet pengaman (safeguard threshold) agar pedagang mikro terlindungi.</li>
              <li>Sediakan dasbor transparansi bukti potong e-Bupot terpadu yang mudah diaudit secara terbuka.</li>
              <li>Buka kanal konsultasi cepat dan meja bantuan terintegrasi bagi asosiasi pedagang.</li>
            </ul>
          </div>

          <!-- CONTINUE -->
          <div class="action-card card-continue">
            <div class="action-card-header">
              <span class="badge success">CONTINUE (PERTAHANKAN)</span>
              <span class="action-meta">Praktik Baik Berjalan</span>
            </div>
            <ul class="action-list">
              <li>Lanjutkan koordinasi teknis bersama platform lokapasar untuk penyaringan disinformasi.</li>
              <li>Pertahankan komitmen kepatuhan privasi data transaksi sesuai regulasi UU PDP.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 06: Representasi Respon Agen Simulasi -->
    <div class="step-card">
      <div class="card-header">
        <div class="step-info">
          <span class="step-num">06</span>
          <span class="step-title">Representasi Respons Nyata Agen Simulasi</span>
        </div>
        <div class="step-status">
          <span class="badge neutral">3 KUTIPAN KUNCI</span>
        </div>
      </div>

      <div class="card-content">
        <p class="api-note">VOICES /swarms/agent-dialogues/highlights</p>
        <p class="description">
          Sampel dialog paling representatif dari profil agen yang mencerminkan psikologi sentimen publik.
        </p>

        <div class="quotes-grid">
          <div class="quote-card">
            <div class="quote-header">
              <div class="agent-identity">
                <span class="agent-id">Agent 14</span>
                <span class="agent-name">Konsumen Akhir / Kelas Menengah</span>
              </div>
              <span class="agent-stance stance-opposing">OPPOSING</span>
            </div>
            <blockquote class="quote-body">
              "Kenapa beban akhirnya selalu mendarat di harga barang yang kami beli? Kami butuh perincian komponen biaya yang transparan, bukan sekadar imbauan normatif."
            </blockquote>
            <div class="quote-meta">
              <span class="meta-item mono">Ronde: 24</span>
              <span class="meta-item mono">Sentimen: -0.78</span>
              <span class="meta-item mono">Topik: #TransparansiHarga</span>
            </div>
          </div>

          <div class="quote-card">
            <div class="quote-header">
              <div class="agent-identity">
                <span class="agent-id">Agent 08</span>
                <span class="agent-name">Pedagang Daring & Pelaku UMKM Mikro</span>
              </div>
              <span class="agent-stance stance-neutral">NEUTRAL</span>
            </div>
            <blockquote class="quote-body">
              "Margin kami sudah sangat tipis. Kenaikan harga 5–10% adalah respons terpaksa agar usaha kami tidak gulung tikar, bukan karena kami ingin melawan regulasi."
            </blockquote>
            <div class="quote-meta">
              <span class="meta-item mono">Ronde: 18</span>
              <span class="meta-item mono">Sentimen: -0.42</span>
              <span class="meta-item mono">Topik: #MarginPedagang</span>
            </div>
          </div>

          <div class="quote-card">
            <div class="quote-header">
              <div class="agent-identity">
                <span class="agent-id">Agent 03</span>
                <span class="agent-name">Asosiasi Pelaku Usaha / Toko Pasar Fisik</span>
              </div>
              <span class="agent-stance stance-supportive">SUPPORTIVE</span>
            </div>
            <blockquote class="quote-body">
              "Kami mendukung persaingan yang sehat dan adil, asalkan pelaksanaannya benar-benar tidak menciptakan beban biaya kepatuhan baru bagi pedagang kecil."
            </blockquote>
            <div class="quote-meta">
              <span class="meta-item mono">Ronde: 31</span>
              <span class="meta-item mono">Sentimen: +0.35</span>
              <span class="meta-item mono">Topik: #KeadilanBerusaha</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  reportId: String,
  simulationId: String,
  title: String,
  summary: String,
  sections: Array
})

// Stakeholder Filter State
const activeStanceFilter = ref('ALL')
const selectedCluster = ref(null)

const stanceFilters = [
  { key: 'ALL', label: 'SEMUA (4)' },
  { key: 'OPPOSING', label: 'PENENTANG (1)' },
  { key: 'NEUTRAL', label: 'TERJEPIT (1)' },
  { key: 'SUPPORTIVE', label: 'PENDUKUNG (1)' },
  { key: 'OBSERVER', label: 'REGULATOR (1)' }
]

const stakeholders = [
  {
    id: 'c1',
    clusterId: '01',
    name: 'Konsumen Akhir & Warganet Vokal',
    type: 'Public',
    stance: 'OPPOSING',
    stanceClass: 'stance-opposing',
    narrative: 'Menjadi motor penggerak eskalasi sentimen paling vokal di media sosial. Mengubah isu teknis perpajakan menjadi narasi ketidakadilan daya beli, menggalang solidaritas warganet, dan menuntut transparansi struktur biaya transaksi secara terbuka.',
    resonance: '42%',
    resonanceWidth: '42px',
    sentiment: '-0.65',
    sentimentClass: 'negative',
    influence: '4.5'
  },
  {
    id: 'c2',
    clusterId: '02',
    name: 'Pedagang Daring Mikro & Reseller',
    type: 'Merchant',
    stance: 'NEUTRAL',
    stanceClass: 'stance-neutral',
    narrative: 'Memiliki margin keuntungan tipis (3–8%). Menolak aksi anarkis atau penghindaran total, namun terpaksa menaikkan harga etalase demi menutup biaya kepatuhan. Menjadi kelompok penentu kepatuhan riil di lapangan.',
    resonance: '28%',
    resonanceWidth: '28px',
    sentiment: '-0.35',
    sentimentClass: 'negative',
    influence: '3.8'
  },
  {
    id: 'c3',
    clusterId: '03',
    name: 'Toko Fisik & Ritel Konvensional',
    type: 'Retail',
    stance: 'SUPPORTIVE',
    stanceClass: 'stance-supportive',
    narrative: 'Menyambut positif kebijakan sebagai pemulihan kesetaraan berusaha (level playing field) terhadap pasar daring. Namun posisinya terisolasi secara sosial karena dukungannya tidak mendapat gaung di media sosial.',
    resonance: '14%',
    resonanceWidth: '14px',
    sentiment: '+0.45',
    sentimentClass: 'positive',
    influence: '2.4'
  },
  {
    id: 'c4',
    clusterId: '04',
    name: 'Platform Lokapasar & Regulator',
    type: 'System',
    stance: 'OBSERVER',
    stanceClass: 'stance-observer',
    narrative: 'Mengkhawatirkan potensi penurunan Gross Merchandise Volume (GMV) dan kesiapan infrastruktur integrasi IT. Berfokus pada klarifikasi disinformasi dan kepatuhan privasi data transaksi sesuai UU PDP.',
    resonance: '16%',
    resonanceWidth: '16px',
    sentiment: '+0.05',
    sentimentClass: 'neutral',
    influence: '4.8'
  }
]

const filteredStakeholders = computed(() => {
  if (activeStanceFilter.value === 'ALL') return stakeholders
  return stakeholders.filter(s => s.stance === activeStanceFilter.value)
})

const toggleSelectCluster = (id) => {
  selectedCluster.value = selectedCluster.value === id ? null : id
}
</script>

<style scoped>
.executive-summary-wrapper {
  width: 100%;
  margin: 0;
  padding: 4px 0 32px 0;
}

/* Step Card (Native MiroFish UI) */
.step-card {
  background: #FFFFFF;
  border: 1px solid #EAEAEA;
  border-radius: 8px;
  margin-bottom: 20px;
  transition: all 0.2s ease;
}

.step-card:hover {
  border-color: #CBD5E1;
}

.card-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #F1F5F9;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px;
  font-weight: 700;
  color: #0F172A;
}

.step-title {
  font-size: 15px;
  font-weight: 700;
  color: #0F172A;
}

.card-content {
  padding: 20px;
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #94A3B8;
  margin: 0 0 6px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.description {
  font-size: 13px;
  color: #64748B;
  line-height: 1.6;
  margin: 0 0 18px 0;
}

/* Badges */
.badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge.danger {
  background: #FEE2E2;
  color: #DC2626;
}

.badge.warning {
  background: #FEF3C7;
  color: #D97706;
}

.badge.success {
  background: #DCFCE7;
  color: #16A34A;
}

.badge.primary {
  background: #EFF6FF;
  color: #2563EB;
}

.badge.neutral {
  background: #F1F5F9;
  color: #475569;
}

/* Config Grid (4 Columns) */
.config-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.config-item {
  background: #F9F9F9;
  padding: 12px 14px;
  border-radius: 6px;
  border: 1px solid #F1F5F9;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-item-label {
  font-size: 11px;
  color: #94A3B8;
  font-weight: 500;
  text-transform: capitalize;
}

.config-item-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px;
  font-weight: 700;
  color: #1E293B;
}

.config-item-value .unit {
  font-size: 13px;
  color: #94A3B8;
  font-weight: 500;
}

.text-danger { color: #DC2626; }
.text-warning { color: #D97706; }
.text-success { color: #16A34A; }
.text-neutral { color: #64748B; }

/* Spectrum Bar */
.spectrum-container {
  background: #F9F9F9;
  border: 1px solid #F1F5F9;
  border-radius: 6px;
  padding: 14px 16px;
  margin-bottom: 16px;
}

.spectrum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.spectrum-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: #64748B;
  letter-spacing: 0.05em;
}

.spectrum-ratio {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11.5px;
  font-weight: 600;
  color: #DC2626;
}

.spectrum-bar {
  display: flex;
  height: 20px;
  border-radius: 4px;
  overflow: hidden;
  background: #E2E8F0;
}

.seg {
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  font-weight: 700;
  color: #FFFFFF;
  transition: all 0.2s ease;
}

.seg-danger { background: #EF4444; }
.seg-warning { background: #F59E0B; color: #1E293B; }
.seg-success { background: #10B981; }

.spectrum-legend {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-top: 10px;
  font-size: 11px;
  color: #64748B;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-danger { background: #EF4444; }
.dot-warning { background: #F59E0B; }
.dot-success { background: #10B981; }

/* Time Periods & Rows */
.time-periods {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.period-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  background: #F9F9F9;
  border-radius: 6px;
  border: 1px solid #F1F5F9;
  transition: all 0.15s ease;
}

.interactive-row:hover {
  background: #FFFFFF;
  border-color: #CBD5E1;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
}

.period-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748B;
  min-width: 110px;
}

.period-hours {
  font-size: 12.5px;
  color: #334155;
  flex: 1;
}

.period-multiplier {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.badge-danger { background: #FEE2E2; color: #DC2626; }
.badge-warning { background: #FEF3C7; color: #D97706; }
.badge-primary { background: #EFF6FF; color: #2563EB; }
.badge-success { background: #DCFCE7; color: #16A34A; }

.mono {
  font-family: 'JetBrains Mono', monospace;
}

.row-num {
  font-size: 14px;
  font-weight: 700;
  color: #94A3B8;
  min-width: 24px;
}

.row-content {
  flex: 1;
}

.row-title {
  font-size: 13px;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 2px;
}

.row-desc {
  font-size: 12px;
  color: #64748B;
  line-height: 1.5;
}

/* Cluster Filter Bar */
.cluster-filter-bar {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.filter-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid #E2E8F0;
  background: #F9F9F9;
  color: #64748B;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-pill:hover {
  background: #FFFFFF;
  color: #0F172A;
  border-color: #CBD5E1;
}

.filter-pill.active {
  background: #0F172A;
  color: #FFFFFF;
  border-color: #0F172A;
}

/* Agents Cards (2-Columns matching Step2EnvSetup) */
.agents-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.agent-card {
  background: #F9F9F9;
  border: 1px solid #E5E5E5;
  border-radius: 6px;
  padding: 14px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.agent-card:hover, .agent-card.card-highlighted {
  border-color: #0284C7;
  background: #FFFFFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #F1F5F9;
}

.agent-identity {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.agent-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #94A3B8;
  font-weight: 600;
}

.agent-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #1E293B;
}

.agent-tags {
  display: flex;
  gap: 6px;
  align-items: center;
}

.agent-type {
  font-size: 10px;
  color: #64748B;
  background: #F1F5F9;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.agent-stance {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
}

.stance-neutral { background: #F1F5F9; color: #64748B; }
.stance-supportive { background: #DCFCE7; color: #16A34A; }
.stance-opposing { background: #FEE2E2; color: #DC2626; }
.stance-observer { background: #FEF3C7; color: #D97706; }

.cluster-narrative {
  font-size: 12px;
  color: #475569;
  line-height: 1.55;
  margin: 0 0 12px 0;
}

.agent-params {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px solid #F1F5F9;
  padding-top: 8px;
}

.param-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.param-item .param-label {
  font-size: 10px;
  color: #94A3B8;
}

.param-item .param-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.param-value.with-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mini-bar {
  height: 4px;
  background: linear-gradient(90deg, #6366F1, #A855F7);
  border-radius: 2px;
  min-width: 4px;
}

.param-value.positive { color: #16A34A; }
.param-value.negative { color: #DC2626; }
.param-value.neutral { color: #64748B; }
.param-value.highlight { color: #2563EB; }

/* Action Columns (STOP - START - CONTINUE) */
.action-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.action-card {
  background: #F9F9F9;
  border: 1px solid #E5E5E5;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
}

.action-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #F1F5F9;
}

.action-meta {
  font-size: 11px;
  color: #94A3B8;
}

.action-list {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  color: #475569;
  line-height: 1.6;
}

.action-list li {
  margin-bottom: 6px;
}

/* Quotes Grid */
.quotes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quote-card {
  background: #F9F9F9;
  border: 1px solid #E5E5E5;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.quote-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.quote-body {
  margin: 0 0 12px 0;
  padding: 0;
  font-size: 12px;
  font-style: italic;
  color: #334155;
  line-height: 1.6;
}

.quote-meta {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #F1F5F9;
  padding-top: 8px;
  font-size: 10px;
  color: #94A3B8;
}

@media (max-width: 900px) {
  .config-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .agents-cards, .action-columns, .quotes-grid {
    grid-template-columns: 1fr;
  }
}
</style>
