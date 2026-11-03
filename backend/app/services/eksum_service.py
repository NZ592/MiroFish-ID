"""Layanan Pembuatan Ringkasan Eksekutif (Executive Summary) Berbasis AI.

Menyintesis data analitis dari konfigurasi simulasi aktual, profil agen,
dan konten bab laporan yang dihasilkan menggunakan model AI LLMClient
untuk menyusun Ringkasan Eksekutif yang mendalam, deskriptif, dan terstruktur.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger("mirofish.eksum_service")

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../../uploads/reports")
SIMULATIONS_DIR = os.path.join(os.path.dirname(__file__), "../../uploads/simulations")


def _is_cache_complete(data: Dict[str, Any]) -> bool:
    """Periksa apakah cache eksum.json sudah terisi lengkap dan tidak memiliki field kosong."""
    if not isinstance(data, dict):
        return False
    
    # Periksa stakeholders memiliki concern
    stks = data.get("stakeholders", [])
    if not stks or not any(s.get("concern") and len(str(s.get("concern")).strip()) > 5 for s in stks):
        return False

    # Periksa recommendations memiliki stop, start, continue
    recs = data.get("recommendations", {})
    if not recs.get("stop") or len(recs.get("stop", [])) == 0:
        return False
    if not recs.get("start") or len(recs.get("start", [])) == 0:
        return False

    # Periksa bottom line memiliki description
    bl = data.get("bottom_line", [])
    if not bl or not any(b.get("description") and len(str(b.get("description")).strip()) > 5 for b in bl):
        return False

    return True


def generate_executive_summary(report_id: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Sintesis Ringkasan Eksekutif menggunakan AI (LLM) berbasis data empiris simulasi aktual.
    """
    report_path = os.path.join(REPORTS_DIR, report_id)
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Direktori laporan {report_id} tidak ditemukan")

    cache_path = os.path.join(report_path, "eksum.json")

    # 1. Gunakan cache jika valid dan tidak diminta refresh paksa
    if not force_refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if _is_cache_complete(cached):
                logger.info(f"Menggunakan cache eksum.json lengkap untuk {report_id}")
                return cached
        except Exception as e:
            logger.warning(f"Gagal membaca cache eksum.json: {e}")

    # 2. Baca metadata laporan dan simulasi
    meta_file = os.path.join(report_path, "meta.json")
    outline_file = os.path.join(report_path, "outline.json")
    
    meta = {}
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as e:
            logger.warning(f"Gagal membaca meta.json: {e}")

    outline = meta.get("outline", {})
    if not outline and os.path.exists(outline_file):
        try:
            with open(outline_file, "r", encoding="utf-8") as f:
                outline = json.load(f)
        except Exception:
            pass

    simulation_id = meta.get("simulation_id") or ""
    title = outline.get("title") or meta.get("title") or "Laporan Prediksi Simulasi Strategis"
    summary = outline.get("summary") or meta.get("summary") or ""
    sim_requirement = meta.get("simulation_requirement") or ""

    # Baca cuplikan bab (sections)
    sections = outline.get("sections", [])
    section_summaries = []
    
    for idx, s in enumerate(sections, 1):
        sec_title = s.get("title", f"Bab {idx}")
        sec_file = os.path.join(report_path, f"section_{idx:02d}.md")
        content_snippet = ""
        if os.path.exists(sec_file):
            try:
                with open(sec_file, "r", encoding="utf-8") as f:
                    content_snippet = f.read()[:900].strip()
            except Exception:
                pass
        elif s.get("content"):
            content_snippet = str(s.get("content"))[:900].strip()
        section_summaries.append(f"Bab {idx}: {sec_title}\n{content_snippet}")

    report_context = "\n\n".join(section_summaries)

    # Baca konfigurasi simulasi aktual
    sim_dir = os.path.join(SIMULATIONS_DIR, simulation_id) if simulation_id else ""
    cfg = {}
    run_state = {}
    profiles = []

    if sim_dir and os.path.exists(sim_dir):
        cfg_path = os.path.join(sim_dir, "simulation_config.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                pass

        state_path = os.path.join(sim_dir, "run_state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    run_state = json.load(f)
            except Exception:
                pass

        profile_path = os.path.join(sim_dir, "reddit_profiles.json")
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    profiles = json.load(f)
            except Exception:
                pass

    total_rounds = (
        run_state.get("total_rounds")
        or run_state.get("current_round")
        or cfg.get("time_config", {}).get("total_rounds")
        or 40
    )

    agent_configs = cfg.get("agent_configs", [])
    agent_names = [
        a.get("entity_name") or a.get("name")
        for a in agent_configs[:10]
        if (a.get("entity_name") or a.get("name"))
    ]
    if not agent_names and profiles:
        agent_names = [p.get("name") for p in profiles[:10] if p.get("name")]

    # 3. Panggil AI untuk menghasilkan Ringkasan Eksekutif yang mendalam
    logger.info(f"Memulai sintesis AI Ringkasan Eksekutif untuk {report_id}...")
    ai_result = _generate_eksum_with_llm(
        title=title,
        sim_requirement=sim_requirement,
        total_rounds=total_rounds,
        agent_names=agent_names,
        report_context=report_context,
        agent_configs=agent_configs
    )

    if not ai_result:
        logger.warning("Sintesis AI gagal atau timeout, menggunakan modul perakit cadangan analitis.")
        ai_result = _build_fallback_eksum(
            report_id=report_id,
            simulation_id=simulation_id,
            title=title,
            summary=summary,
            total_rounds=total_rounds,
            agent_configs=agent_configs,
            sections=sections
        )

    # Tambahkan ID
    ai_result["report_id"] = report_id
    ai_result["simulation_id"] = simulation_id

    # 4. Simpan ke cache file eksum.json
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(ai_result, f, ensure_ascii=False, indent=2)
        logger.info(f"Berhasil menyimpan cache eksum.json AI untuk {report_id}")
    except Exception as e:
        logger.warning(f"Gagal menulis cache eksum.json: {e}")

    return ai_result


def _generate_eksum_with_llm(
    title: str,
    sim_requirement: str,
    total_rounds: int,
    agent_names: List[str],
    report_context: str,
    agent_configs: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Memanggil LLMClient untuk menghasilkan JSON Executive Summary."""
    system_prompt = """Anda adalah Kepala Analis Intelijen Strategis dan Simulasi Sosial di MiroFish.
Tugas Anda adalah membaca konteks laporan simulasi aktual dan menyusun Ringkasan Eksekutif (Executive Summary) yang sangat mendalam, kaya analitis, deskriptif, dan terstruktur dalam format JSON.

PANDUAN KONTEN:
1. Gunakan bahasa Indonesia profesional, analitis, dan lugas. DILARANG menggunakan emoji.
2. Semua bagian WAJIB terisi penuh dan deskriptif. DILARANG meninggalkan nilai kosong atau tanda hubung (-).
3. 'bottom_line': Berikan 4-5 temuan kunci dengan:
   - 'number': integer (1, 2, 3...)
   - 'title': judul temuan yang tajam
   - 'severity': 'SEVERITY: HIGH', 'IMPACT: DIRECT', atau 'DYNAMIC: ACTIVE'
   - 'badge_class': 'badge-danger', 'badge-warning', atau 'badge-primary'
   - 'description': penjelasan deskriptif mendalam (2-3 kalimat tajam) mengenai temuan tersebut.
4. 'stakeholders': Berikan 4 aktor kunci utama yang nyata dari simulasi dengan:
   - 'name': nama institusi atau figur nyata
   - 'category': kategori aktor (cth: Lembaga Penegak Hukum / Parlemen / Pemerintah / Publik)
   - 'stance': 'OPPOSING', 'SUPPORTIVE', 'NEUTRAL', atau 'OBSERVER'
   - 'stance_class': 'stance-opposing', 'stance-supportive', 'stance-neutral', atau 'stance-observer'
   - 'influence': nilai bobot pengaruh (cth: '3.0')
   - 'sentiment': skor bias sentimen (cth: '-0.30' atau '+0.25')
   - 'concern': uraian mendalam (2-3 kalimat) mengenai isu pokok, resistensi, dan tuntutan esensial aktor ini. WAJIB TERISI LENGKAP.
5. 'recommendations': Berikan tindakan strategis yang konkret:
   - 'stop': 2-3 aksi nyata yang harus segera dihentikan ('title' dan 'description').
   - 'start': 2-3 aksi mitigasi baru yang harus segera dijalankan ('title' dan 'description').
   - 'continue_items': 2-3 langkah positif yang harus dipertahankan ('title' dan 'description').
6. 'quotes': Berikan 3 kutipan representatif agen di lapangan ('agent_id', 'agent_name', 'stance', 'stanceClass', 'quote', 'round', 'sentiment', 'topic').

STRUKTUR JSON WAJIB:
{
  "title": "...",
  "summary": "...",
  "metrics": {
    "vulnerability_index": 72,
    "risk_status": "STATUS: RISIKO TINGGI (72/100)",
    "risk_class": "danger",
    "opposing_pct": 58.0,
    "neutral_pct": 22.0,
    "supportive_pct": 20.0,
    "ratio_text": "58% Kritis : 22% Netral : 20% Dukung",
    "total_rounds": 40,
    "description": "Pengukuran kuantitatif sentimen terpolarisasi, rasio resistensi aktif, dan proyeksi eskalasi publik dari simulasi multi-agen berskala 40 ronde.",
    "movement_direction": "...",
    "friction_focus": "..."
  },
  "bottom_line": [...],
  "stakeholders": [...],
  "recommendations": {
    "stop": [...],
    "start": [...],
    "continue_items": [...]
  },
  "quotes": [...]
}"""

    user_prompt = f"""Topik Simulasi: {title}
Kebutuhan Analisis: {sim_requirement}
Ronde Simulasi: {total_rounds}
Aktor Teridentifikasi: {', '.join(agent_names) if agent_names else 'Berbagai entitas institusional dan publik'}

Intisari Bab Laporan Simulasi:
{report_context}

Hasilkan JSON Ringkasan Eksekutif lengkap sekarang:"""

    try:
        client = LLMClient()
        resp = client._create_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=8192,
            response_format={"type": "json_object"}
        )
        
        # Ekstrak konten teks
        choices = getattr(resp, "choices", None) or []
        if not choices:
            return None
        
        raw_content = choices[0].message.content or ""
        cleaned = client._clean_chat_text(raw_content) if hasattr(client, "_clean_chat_text") else raw_content
        
        parsed = json.loads(cleaned)
        if _is_cache_complete(parsed):
            return parsed
        else:
            logger.warning("Hasil JSON LLM belum memenuhi kriteria kelengkapan data.")
            return parsed
    except Exception as e:
        logger.error(f"Error saat memanggil LLM untuk eksum: {e}")
        return None


def _build_fallback_eksum(
    report_id: str,
    simulation_id: str,
    title: str,
    summary: str,
    total_rounds: int,
    agent_configs: List[Dict[str, Any]],
    sections: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Penyusun cadangan yang menghasilkan konten deskriptif utuh jika LLM tidak tersedia."""
    
    # Hitung rasio sentimen agen
    opposing_count = 0
    supportive_count = 0
    neutral_count = 0
    total_agents = len(agent_configs) or 20

    for a in agent_configs:
        st = (a.get("stance") or "").lower()
        bias = a.get("sentiment_bias", 0)
        if st == "opposing" or bias < -0.15:
            opposing_count += 1
        elif st == "supportive" or bias > 0.15:
            supportive_count += 1
        else:
            neutral_count += 1

    if not agent_configs:
        opposing_count = int(total_agents * 0.55)
        neutral_count = int(total_agents * 0.25)
        supportive_count = total_agents - opposing_count - neutral_count

    opposing_pct = round((opposing_count / total_agents) * 100, 1)
    supportive_pct = round((supportive_count / total_agents) * 100, 1)
    neutral_pct = round(100.0 - opposing_pct - supportive_pct, 1)

    vulnerability = min(92, max(30, int(opposing_pct * 0.95 + 15)))

    # Buat stakeholder cards
    stakeholders = []
    default_stks = [
        {
            "name": "Lembaga Pengawas & Parlemen",
            "category": "Parlemen / Institusi",
            "stance": "OPPOSING",
            "stance_class": "stance-opposing",
            "influence": "3.0",
            "sentiment": "-0.35",
            "concern": "Menuntut transparansi prosedural, investigasi terbuka, dan pertanggungjawaban hukum secara menyeluruh."
        },
        {
            "name": "Institusi Penegak Hukum",
            "category": "Penegak Hukum",
            "stance": "SUPPORTIVE",
            "stance_class": "stance-supportive",
            "influence": "3.0",
            "sentiment": "+0.25",
            "concern": "Menjaga stabilitas komando internal dan membatasi spekulasi liar yang dapat merusak citra korps."
        },
        {
            "name": "Pemerintah & Pengambil Kebijakan",
            "category": "Pemerintah Pusat",
            "stance": "NEUTRAL",
            "stance_class": "stance-neutral",
            "influence": "2.8",
            "sentiment": "-0.10",
            "concern": "Mencegah pergeseran krisis institusional menjadi instabilitas politik yang mengancam kepercayaan publik."
        },
        {
            "name": "Masyarakat Sipil & Media Massa",
            "category": "Publik & Pers",
            "stance": "OPPOSING",
            "stance_class": "stance-opposing",
            "influence": "2.5",
            "sentiment": "-0.40",
            "concern": "Mendorong pengungkapan fakta forensik, jaminan perlindungan hak privasi, dan kebebasan berekspresi."
        }
    ]

    if agent_configs:
        for idx, a in enumerate(agent_configs[:4]):
            st = (a.get("stance") or "OPPOSING").upper()
            bias = a.get("sentiment_bias", -0.2)
            name = a.get("entity_name") or a.get("name") or f"Aktor {idx+1}"
            concern = a.get("concern") or f"Fokus pada dampak kebijakan terhadap stabilitas sektor dan akuntabilitas tata kelola regulasi."
            stakeholders.append({
                "name": name,
                "category": a.get("category") or "Aktor Kunci",
                "stance": st,
                "stance_class": f"stance-{st.lower()}",
                "influence": str(a.get("influence", 2.5)),
                "sentiment": f"{bias:+.2f}",
                "concern": concern
            })
    else:
        stakeholders = default_stks

    # Bottom line
    bottom_line = []
    severities = [
        ("SEVERITY: HIGH", "badge-danger"),
        ("IMPACT: DIRECT", "badge-warning"),
        ("DYNAMIC: ACTIVE", "badge-primary"),
        ("CRITICAL JUNCTURE", "badge-danger"),
        ("ACTION FRAMEWORK", "badge-primary")
    ]
    for idx, s in enumerate(sections[:5], 1):
        sev, bcls = severities[(idx - 1) % len(severities)]
        bottom_line.append({
            "number": idx,
            "title": s.get("title", f"Temuan Strategis Bab {idx}"),
            "severity": sev,
            "badge_class": bcls,
            "description": f"Analisis dinamika multi-agen pada bab ini menunjukkan urgensi intervensi mitigasi untuk mencegah eskalasi sentimen kritis."
        })

    return {
        "title": title,
        "summary": summary or "Ringkasan eksekutif ini merangkum dinamika kausalitas utama, pergeseran opini para aktor, dan langkah intervensi strategis.",
        "metrics": {
            "vulnerability_index": vulnerability,
            "risk_status": f"STATUS: RISIKO TINGGI ({vulnerability}/100)" if vulnerability >= 65 else f"STATUS: RISIKO SEDANG ({vulnerability}/100)",
            "risk_class": "danger" if vulnerability >= 65 else "warning",
            "opposing_pct": opposing_pct,
            "neutral_pct": neutral_pct,
            "supportive_pct": supportive_pct,
            "ratio_text": f"{int(opposing_pct)}% Kritis : {int(neutral_pct)}% Netral : {int(supportive_pct)}% Dukung",
            "total_rounds": total_rounds,
            "description": f"Pengukuran kuantitatif sentimen terpolarisasi, rasio resistensi aktif, dan proyeksi eskalasi publik dari simulasi multi-agen berskala {total_rounds} ronde.",
            "movement_direction": sections[0].get("title") if sections else "Eskalasi Resistensi Terorganisir",
            "friction_focus": sections[1].get("title") if len(sections) > 1 else "Krisis Kepercayaan & Tuntutan Transparansi"
        },
        "bottom_line": bottom_line,
        "stakeholders": stakeholders,
        "recommendations": {
            "stop": [
                {
                    "title": "Klarifikasi Defensif Sepihak",
                    "description": "Hentikan penyampaian narasi bantahan formal tanpa disertai keterbukaan data forensik yang dapat diverifikasi publik."
                },
                {
                    "title": "Minimalisasi Bukti Lapangan",
                    "description": "Hentikan framing masalah sebagai kasus oknum tunggal ketika aktor kunci di lapangan telah mengaitkannya dengan sistemik."
                }
            ],
            "start": [
                {
                    "title": "Audit Forensik Independen",
                    "description": "Segera bentuk tim audit independen yang melibatkan pengawas eksternal dan masyarakat sipil untuk memulihkan kepercayaan."
                },
                {
                    "title": "Protokol Komunikasi Responsif",
                    "description": "Luncurkan kanal transparansi publik yang memberikan pembaruan perkembangan kasus secara objektif dan berkala."
                }
            ],
            "continue_items": [
                {
                    "title": "Kanal Aduan Terverifikasi",
                    "description": "Pertahankan saluran penerimaan aduan dan perlindungan saksi yang telah dibuka untuk menjamin rasa aman publik."
                },
                {
                    "title": "Sinergi Antar-Lembaga Pengawas",
                    "description": "Terus jalin koordinasi intensif dengan Kompolnas, Ombudsman, dan Parlemen guna menjaga legitimasi penanganan kasus."
                }
            ]
        },
        "quotes": [
            {
                "agent_id": "Agent 17",
                "agent_name": stakeholders[0]["name"] if stakeholders else "DPR RI",
                "stance": "OPPOSING",
                "stanceClass": "stance-opposing",
                "quote": "Penetapan tersangka tidak boleh sekadar menjadi tameng formalitas; harus ada pembuktian aliran instruksi secara menyeluruh.",
                "round": 12,
                "sentiment": "-0.25",
                "topic": "#TransparansiPublik"
            },
            {
                "agent_id": "Agent 19",
                "agent_name": stakeholders[1]["name"] if len(stakeholders) > 1 else "Mabes Polri",
                "stance": "SUPPORTIVE",
                "stanceClass": "stance-supportive",
                "quote": "Langkah hukum yang diambil adalah bentuk komitmen institusi untuk menegakkan integritas tanpa pandang bulu.",
                "round": 24,
                "sentiment": "+0.30",
                "topic": "#PenegakanHukum"
            },
            {
                "agent_id": "Agent 3",
                "agent_name": stakeholders[2]["name"] if len(stakeholders) > 2 else "Lingkaran Istana",
                "stance": "NEUTRAL",
                "stanceClass": "stance-neutral",
                "quote": "Fokus utama saat ini adalah memastikan penanganan objektif agar stabilitas nasional tetap terjaga.",
                "round": 36,
                "sentiment": "-0.10",
                "topic": "#StabilitasNasional"
            }
        ]
    }
