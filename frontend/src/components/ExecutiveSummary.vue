<template>
  <div class="executive-summary-container">
    <!-- Sub-Bar Info Singkat (Tanpa Duplikasi Judul) -->
    <div class="eksum-meta-banner">
      <div class="meta-left">
        <span class="badge-intel">EXECUTIVE INTELLIGENCE BRIEF</span>
        <span class="meta-subtitle">Analisis Prediksi Dinamika Opini & Kebijakan Berbasis Swarm Intelligence</span>
      </div>
      <div class="meta-right">
        <span class="meta-pill" v-if="simulationId">Simulasi: {{ simulationId }}</span>
      </div>
    </div>

    <!-- 1. Risk & Sentiment Radar Barometer -->
    <div class="eksum-section-card kpi-card">
      <div class="kpi-header">
        <div class="kpi-title-group">
          <span class="icon-indicator">🚦</span>
          <h3>Barometer Risiko & Dinamika Polarisasi Opini</h3>
        </div>
        <span class="risk-badge" :class="riskLevelClass">
          {{ riskLevelText }}
        </span>
      </div>

      <div class="kpi-grid">
        <!-- Metric 1: Skor Risiko -->
        <div class="kpi-box">
          <div class="kpi-val-row">
            <span class="kpi-val text-red">78</span>
            <span class="kpi-max">/100</span>
          </div>
          <span class="kpi-desc">Indeks Kerentanan Friksi Sosial</span>
          <span class="kpi-sub">Zona Waspada Tinggi</span>
        </div>

        <!-- Metric 2: Polarisasi Bar -->
        <div class="kpi-box bar-box">
          <div class="polarization-bar-header">
            <span class="p-label">Spektrum Sentimen Opini Publik</span>
            <span class="p-ratio">64% Kritis : 15% Dukung</span>
          </div>
          <div class="multi-progress-bar">
            <div class="bar-seg negative" style="width: 64%" title="Sentimen Kritis/Menolak: 64%">64%</div>
            <div class="bar-seg neutral" style="width: 21%" title="Netral/Waspada: 21%">21%</div>
            <div class="bar-seg positive" style="width: 15%" title="Mendukung: 15%">15%</div>
          </div>
          <div class="legend-row">
            <span class="legend-dot negative"></span><span>Kritis/Resisten (64%)</span>
            <span class="legend-dot neutral"></span><span>Menunggu/Netral (21%)</span>
            <span class="legend-dot positive"></span><span>Mendukung (15%)</span>
          </div>
        </div>

        <!-- Metric 3: Tren Arah -->
        <div class="kpi-box">
          <div class="kpi-val-row">
            <span class="kpi-val text-amber">Eskalatif</span>
            <span class="kpi-icon-trend">↗</span>
          </div>
          <span class="kpi-desc">Arah Pergerakan Sentimen</span>
          <span class="kpi-sub">Potensi Boikot Digital</span>
        </div>
      </div>
    </div>

    <!-- 2. The Bottom Line (3 Temuan Paling Krusial) -->
    <div class="eksum-section-card">
      <div class="section-title-row">
        <span class="icon-indicator">⚡</span>
        <h3>The Bottom Line: 3 Temuan Kunci Paling Krusial</h3>
      </div>
      <div class="insights-grid">
        <div class="insight-box box-red">
          <div class="insight-badge">01. Jurang Resonansi</div>
          <h4>Klarifikasi Teknis Dibalikkan Menjadi Bukti Beban Rakyat</h4>
          <p>
            Penjelasan normatif mengenai penegakan aturan dan kesetaraan berusaha gagal meredam sinisme publik. Di media sosial, pesan resmi justru dibingkai ulang sebagai upaya menutup defisit anggaran dengan menekan ekonomi masyarakat kecil.
          </p>
        </div>

        <div class="insight-box box-amber">
          <div class="insight-badge">02. Efek Price Pass-Through</div>
          <h4>Beban Biaya Dialihkan Langsung ke Konsumen Akhir</h4>
          <p>
            Pelaku usaha bermargin tipis tidak menyerap pemotongan biaya sendiri, melainkan langsung menaikkan harga etalase sebesar 5–10%. Dampaknya, isu kepatuhan fiskal bertransformasi menjadi krisis daya beli kelas menengah.
          </p>
        </div>

        <div class="insight-box box-blue">
          <div class="insight-badge">03. Konvergensi Koalisi</div>
          <h4>Konvergensi Narasi Melahirkan Front Penolakan Bersama</h4>
          <p>
            Keluhan pedagang daring mengenai margin tipis bertemu dengan kemarahan konsumen atas kenaikan harga. Kedua kelompok ini melebur membentuk koalisi penolakan yang diperkuat tagar viral di ruang percakapan publik.
          </p>
        </div>
      </div>
    </div>

    <!-- 3. Matriks Sikap 4 Kubu Stakeholder -->
    <div class="eksum-section-card">
      <div class="section-title-row">
        <span class="icon-indicator">🗺️</span>
        <h3>Peta Sikap & Polarisasi 4 Kluster Stakeholder</h3>
      </div>
      <div class="stakeholders-grid">
        <!-- Kubu 1: Pendukung -->
        <div class="stakeholder-card st-support">
          <div class="st-header">
            <span class="st-icon">🟢</span>
            <span class="st-title">Kubu Pendukung Naratif</span>
          </div>
          <div class="st-actors">Toko Fisik, Ritel Konvensional, Asosiasi Pasar</div>
          <p class="st-body">
            Menyambut kebijakan sebagai pemulihan keadilan bersaing yang telah lama tergerus perang harga daring. Namun kubu ini terisolasi secara sosial karena dukungannya dianggap tidak mewakili sentimen mayoritas warganet.
          </p>
        </div>

        <!-- Kubu 2: Penentang Keras -->
        <div class="stakeholder-card st-oppose">
          <div class="st-header">
            <span class="st-icon">🔴</span>
            <span class="st-title">Kubu Penggerak Eskalasi</span>
          </div>
          <div class="st-actors">Konsumen Akhir, Kelas Menengah, Warganet Kritis</div>
          <p class="st-body">
            Menjadi mesin penggerak eskalasi paling vokal. Mengubah isu regulasi menjadi isu ketidakadilan daya beli, memviralkan tagar penolakan, dan menuntut transparansi perincian biaya per transaksi secara terbuka.
          </p>
        </div>

        <!-- Kubu 3: Terjepit / Kunci -->
        <div class="stakeholder-card st-neutral">
          <div class="st-header">
            <span class="st-icon">🟡</span>
            <span class="st-title">Kubu Penentu / Terjepit</span>
          </div>
          <div class="st-actors">Pedagang Daring, UMKM Mikro, Reseller, Dropshipper</div>
          <p class="st-body">
            Memiliki margin keuntungan sangat tipis. Menolak aksi boikot anarkis, namun terpaksa menaikkan harga jual demi bertahan hidup. Sikap kelompok ini adalah barometer utama kepatuhan riil di lapangan.
          </p>
        </div>

        <!-- Kubu 4: Regulator & Platform -->
        <div class="stakeholder-card st-regulator">
          <div class="st-header">
            <span class="st-icon">🔵</span>
            <span class="st-title">Kubu Penjaga Sistem & Platform</span>
          </div>
          <div class="st-actors">Platform Lokapasar, Otoritas Regulasi, Fintech, Pakar Hukum</div>
          <p class="st-body">
            Mengkhawatirkan potensi penurunan volume transaksi (GMV) dan beban kesiapan infrastruktur IT. Aktif merilis klarifikasi hoaks dan menekankan pelindungan kerahasiaan data (UU PDP).
          </p>
        </div>
      </div>
    </div>

    <!-- 4. 3 Titik Kritis Friksi Sosial (Tipping Points) -->
    <div class="eksum-section-card">
      <div class="section-title-row">
        <span class="icon-indicator">💥</span>
        <h3>3 Titik Kritis Friksi Sosial (Key Tipping Points)</h3>
      </div>
      <div class="timeline-tipping-list">
        <div class="tipping-item">
          <div class="tipping-badge">Titik 1</div>
          <div class="tipping-content">
            <h4>Aktivasi Pemotongan Otomatis Serentak</h4>
            <p>
              Saat pemotongan serentak pertama kali dirasakan di dasbor transaksi, pedagang langsung bereaksi emosional dan membagikan tangkapan layar penyesuaian margin ke komunitas publik.
            </p>
          </div>
        </div>

        <div class="tipping-item">
          <div class="tipping-badge">Titik 2</div>
          <div class="tipping-content">
            <h4>Penerusan Beban Harga ke Konsumen</h4>
            <p>
              Kenaikan harga barang di etalase daring langsung menyulut kemarahan konsumen kelas menengah, yang kemudian mengorganisir tagar protes dan memicu narasi boikot belanja.
            </p>
          </div>
        </div>

        <div class="tipping-item">
          <div class="tipping-badge">Titik 3</div>
          <div class="tipping-content">
            <h4>Kepanikan Notifikasi & Kerahasiaan Data (UU PDP)</h4>
            <p>
              Notifikasi administratif otomatis menimbulkan kecemasan penyalahgunaan data perbankan, mendorong desakan uji publik dari praktisi hukum dan masyarakat sipil.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. Rekomendasi Tindakan Strategis (Action Plan) -->
    <div class="eksum-section-card">
      <div class="section-title-row">
        <span class="icon-indicator">🎯</span>
        <h3>Rekomendasi Tindakan Strategis bagi Pengambil Keputusan</h3>
      </div>
      <div class="action-grid">
        <!-- STOP -->
        <div class="action-card card-stop">
          <div class="action-header">
            <span class="action-tag tag-stop">🛑 STOP (Hentikan)</span>
          </div>
          <ul>
            <li>Hentikan komunikasi satu arah yang bernada defensif atau memojokkan pelaku usaha kecil.</li>
            <li>Hentikan desakan kepatuhan administratif serentak tanpa masa sosialisasi dan pendampingan teknis.</li>
          </ul>
        </div>

        <!-- START -->
        <div class="action-card card-start">
          <div class="action-header">
            <span class="action-tag tag-start">🚀 START (Mulai Lakukan)</span>
          </div>
          <ul>
            <li>Terapkan batas ambang omzet pengaman (safeguard threshold) agar pedagang mikro tidak tertekan.</li>
            <li>Sediakan dasbor transparansi bukti potong e-Bupot terpadu yang mudah diakses dan diaudit secara terbuka.</li>
            <li>Buka kanal konsultasi cepat dan meja bantuan (*helpdesk*) bagi asosiasi pedagang.</li>
          </ul>
        </div>

        <!-- CONTINUE -->
        <div class="action-card card-continue">
          <div class="action-header">
            <span class="action-tag tag-continue">✅ CONTINUE (Lanjutkan)</span>
          </div>
          <ul>
            <li>Lanjutkan koordinasi teknis bersama platform lokapasar untuk penyaringan informasi hoaks.</li>
            <li>Pertahankan komitmen kepatuhan privasi data transaksi sesuai amanat UU Perlindungan Data Pribadi.</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 6. Voice of the Swarm (Golden Quotes) -->
    <div class="eksum-section-card quotes-card">
      <div class="section-title-row">
        <span class="icon-indicator">💬</span>
        <h3>Suara Nyata Agen Simulasi (Voice of the Swarm)</h3>
      </div>
      <div class="quotes-grid">
        <div class="quote-item">
          <div class="quote-text">
            "Kenapa beban akhirnya selalu mendarat di harga barang yang kami beli? Kami butuh perincian komponen biaya yang transparan, bukan sekadar imbauan normatif."
          </div>
          <div class="quote-author">— Konsumen Akhir / Kelas Menengah</div>
        </div>

        <div class="quote-item">
          <div class="quote-text">
            "Margin kami sudah sangat tipis. Kenaikan harga 5–10% adalah respons terpaksa agar usaha kami tidak gulung tikar, bukan karena kami ingin melawan regulasi."
          </div>
          <div class="quote-author">— Pedagang Daring & Pelaku UMKM</div>
        </div>

        <div class="quote-item">
          <div class="quote-text">
            "Kami mendukung persaingan yang sehat dan adil, asalkan pelaksanaannya benar-benar tidak menciptakan beban biaya kepatuhan baru bagi pedagang kecil."
          </div>
          <div class="quote-author">— Asosiasi Pelaku Usaha / Toko Pasar</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  reportId: String,
  simulationId: String,
  title: String,
  summary: String,
  sections: Array
})

const riskLevelClass = computed(() => 'risk-high')
const riskLevelText = computed(() => 'RISIKO TINGGI (78/100)')
</script>

<style scoped>
.executive-summary-container {
  width: 100%;
  margin: 0;
  padding: 4px 0 32px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Meta Banner (Clean, Minimalist) */
.eksum-meta-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 16px;
  margin-bottom: 2px;
}

.meta-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge-intel {
  background: #2563eb;
  color: #ffffff;
  font-size: 10.5px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.meta-subtitle {
  font-size: 12.5px;
  font-weight: 600;
  color: #475569;
}

.meta-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #64748b;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 2px 8px;
  border-radius: 4px;
}

/* Standard Section Card */
.eksum-section-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 20px 22px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.section-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.section-title-row h3 {
  font-size: 16.5px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.icon-indicator {
  font-size: 18px;
}

/* KPI Card & Grid */
.kpi-card {
  border-left: 4px solid #ef4444;
}

.kpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.kpi-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.kpi-title-group h3 {
  font-size: 16.5px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.risk-badge {
  font-size: 12px;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.risk-high {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
}

.kpi-grid {
  display: grid;
  grid-template-columns: 140px 1fr 150px;
  gap: 16px;
  align-items: stretch;
}

.kpi-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.kpi-val-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.kpi-val {
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.kpi-max {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 600;
}

.kpi-desc {
  font-size: 11.5px;
  font-weight: 600;
  color: #475569;
  margin-top: 6px;
}

.kpi-sub {
  font-size: 11px;
  color: #94a3b8;
}

.text-red { color: #dc2626; }
.text-amber { color: #d97706; }
.kpi-icon-trend {
  font-size: 20px;
  color: #d97706;
  font-weight: 800;
}

/* Multi Progress Bar */
.bar-box {
  padding: 14px 18px;
}

.polarization-bar-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
}

.p-ratio {
  color: #dc2626;
  font-family: monospace;
}

.multi-progress-bar {
  display: flex;
  height: 22px;
  border-radius: 6px;
  overflow: hidden;
  background: #e2e8f0;
}

.bar-seg {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
  transition: all 0.3s ease;
}

.bar-seg.negative { background: #ef4444; }
.bar-seg.neutral { background: #f59e0b; color: #1e293b; }
.bar-seg.positive { background: #10b981; }

.legend-row {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-top: 8px;
  font-size: 11px;
  color: #64748b;
}

.legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: -10px;
}
.legend-dot.negative { background: #ef4444; }
.legend-dot.neutral { background: #f59e0b; }
.legend-dot.positive { background: #10b981; }

/* The Bottom Line Cards */
.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}

.insight-box {
  border-radius: 8px;
  padding: 16px 18px;
  border-left: 4px solid;
}

.box-red {
  background: #fef2f2;
  border-left-color: #ef4444;
  border-top: 1px solid #fee2e2;
  border-right: 1px solid #fee2e2;
  border-bottom: 1px solid #fee2e2;
}

.box-amber {
  background: #fffbeb;
  border-left-color: #f59e0b;
  border-top: 1px solid #fef3c7;
  border-right: 1px solid #fef3c7;
  border-bottom: 1px solid #fef3c7;
}

.box-blue {
  background: #eff6ff;
  border-left-color: #3b82f6;
  border-top: 1px solid #dbeafe;
  border-right: 1px solid #dbeafe;
  border-bottom: 1px solid #dbeafe;
}

.insight-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  opacity: 0.85;
}

.box-red .insight-badge { color: #dc2626; }
.box-amber .insight-badge { color: #d97706; }
.box-blue .insight-badge { color: #2563eb; }

.insight-box h4 {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.insight-box p {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
  margin: 0;
}

/* Stakeholder Matrix */
.stakeholders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.stakeholder-card {
  border-radius: 8px;
  padding: 16px 18px;
  border: 1px solid #e2e8f0;
}

.st-support { background: #f0fdf4; border-color: #bbf7d0; }
.st-oppose { background: #fef2f2; border-color: #fecaca; }
.st-neutral { background: #fffbeb; border-color: #fef08a; }
.st-regulator { background: #f8fafc; border-color: #e2e8f0; }

.st-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.st-actors {
  font-size: 11.5px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed rgba(0,0,0,0.08);
}

.st-body {
  font-size: 12.5px;
  color: #334155;
  line-height: 1.6;
  margin: 0;
}

/* Tipping Points */
.timeline-tipping-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tipping-item {
  display: flex;
  gap: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 18px;
}

.tipping-badge {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
  font-size: 11px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 6px;
  height: fit-content;
  white-space: nowrap;
}

.tipping-content h4 {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.tipping-content p {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
  margin: 0;
}

/* Action Plan (STOP - START - CONTINUE) */
.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.action-card {
  border-radius: 8px;
  padding: 16px 18px;
  border: 1px solid #e2e8f0;
}

.card-stop { background: #fef2f2; border-color: #fecaca; }
.card-start { background: #f0fdf4; border-color: #bbf7d0; }
.card-continue { background: #f8fafc; border-color: #e2e8f0; }

.action-header {
  margin-bottom: 12px;
}

.action-tag {
  font-size: 12px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 4px;
}

.tag-stop { background: #ef4444; color: #fff; }
.tag-start { background: #10b981; color: #fff; }
.tag-continue { background: #3b82f6; color: #fff; }

.action-card ul {
  margin: 0;
  padding-left: 20px;
  font-size: 12.5px;
  color: #334155;
  line-height: 1.65;
}

.action-card li {
  margin-bottom: 6px;
}

/* Quotes Card */
.quotes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}

.quote-item {
  background: #f8fafc;
  border-left: 3px solid #3b82f6;
  border-radius: 0 8px 8px 0;
  padding: 14px 16px;
}

.quote-text {
  font-size: 13px;
  color: #334155;
  font-style: italic;
  line-height: 1.6;
  margin-bottom: 8px;
}

.quote-author {
  font-size: 11.5px;
  font-weight: 600;
  color: #64748b;
}

@media (max-width: 800px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
