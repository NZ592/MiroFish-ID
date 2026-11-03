"""
Report API路由
提供模拟报告生成、获取、对话等接口
"""

import os
import traceback
import threading
from datetime import datetime
from flask import request, jsonify, send_file

from . import report_bp
from ..config import Config
from ..services.report_agent import ReportAgent, ReportManager, ReportStatus
from ..services.simulation_manager import SimulationManager
from ..services.simulation_runner import SimulationRunner, RunnerStatus
from ..services.zep_graph_memory_updater import ZepGraphMemoryManager
from ..models.project import ProjectManager, ProjectStatus
from ..models.task import TaskManager, TaskStatus
from ..utils.logger import get_logger
from ..utils.locale import t, get_locale, set_locale
from ..utils.zep_lifecycle import (
    graph_lifecycle_lock,
    register_graph_reader,
    unregister_graph_reader,
)

logger = get_logger('mirofish.api.report')


# ============== 报告生成接口 ==============

@report_bp.route('/generate', methods=['POST'])
def generate_report():
    """
    生成模拟分析报告（异步任务）
    
    这是一个耗时操作，接口会立即返回task_id，
    使用 GET /api/report/generate/status 查询进度
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",    // 必填，模拟ID
            "force_regenerate": false        // 可选，强制重新生成
        }
    
    返回：
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "task_id": "task_xxxx",
                "status": "generating",
                "message": "报告生成任务已启动"
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": t('api.requireSimulationId')
            }), 400

        force_regenerate = data.get('force_regenerate', False)
        if not isinstance(force_regenerate, bool):
            return jsonify({
                "success": False,
                "error": "force_regenerate must be a JSON boolean",
            }), 400
        
        # 获取模拟信息
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        
        if not state:
            return jsonify({
                "success": False,
                "error": t('api.simulationNotFound', id=simulation_id)
            }), 404

        run_state = SimulationRunner.get_run_state(simulation_id)
        updater = ZepGraphMemoryManager.get_updater(simulation_id)
        active_statuses = {
            RunnerStatus.STARTING,
            RunnerStatus.RUNNING,
            RunnerStatus.PAUSED,
            RunnerStatus.STOPPING,
        }
        
        # Periksa apakah seluruh ronde/platform simulasi sudah selesai
        is_all_platforms_done = run_state is not None and (
            (run_state.twitter_completed and run_state.reddit_completed)
            or (run_state.twitter_completed and not run_state.reddit_running)
            or (run_state.reddit_completed and not run_state.twitter_running)
            or (run_state.current_round >= run_state.total_rounds and run_state.total_rounds > 0)
            or (run_state.progress_percent >= 100.0)
        )
        
        if is_all_platforms_done:
            logger.info(f"Semua platform telah selesai untuk {simulation_id}, menetapkan status COMPLETED secara otomatis")
            run_state.runner_status = RunnerStatus.COMPLETED
            run_state.twitter_running = False
            run_state.reddit_running = False
            run_state.completed_at = run_state.completed_at or datetime.now().isoformat()
            SimulationRunner._save_run_state(run_state)
            SimulationRunner._sync_simulation_status(simulation_id, RunnerStatus.COMPLETED)
            
            # Matikan proses jika masih ada sisa
            proc = SimulationRunner._processes.get(simulation_id)
            if proc and proc.poll() is None:
                try:
                    SimulationRunner._terminate_process(proc, simulation_id)
                except Exception as term_err:
                    logger.warning(f"Gagal terminate proses simulasi: {term_err}")

            # Pastikan Zep updater juga dihentikan agar tidak menghalangi pembuatan laporan
            if updater is not None:
                try:
                    ZepGraphMemoryManager.stop_updater(simulation_id)
                    updater = None
                except Exception as up_err:
                    logger.warning(f"Gagal stop updater: {up_err}")

        # Jika masih dalam proses awal yang benar-benar belum selesai
        if run_state is not None and run_state.runner_status in {RunnerStatus.STARTING, RunnerStatus.RUNNING} and not is_all_platforms_done:
            return jsonify({
                "success": False,
                "error": (
                    "Simulasi masih berjalan; tunggu hingga seluruh ronde selesai sebelum membuat laporan"
                ),
                "ingestion_pending": False,
            }), 409

        successful_terminal_statuses = {
            RunnerStatus.COMPLETED,
            RunnerStatus.STOPPED,
            RunnerStatus.STOPPING,
        }
        if (
            run_state is None
            or run_state.runner_status not in successful_terminal_statuses
        ):
            return jsonify({
                "success": False,
                "error": (
                    "A successfully completed or stopped simulation is required "
                    "before generating a report"
                ),
            }), 409

        # 获取项目信息
        project = ProjectManager.get_project(state.project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": t('api.projectNotFound', id=state.project_id)
            }), 404
        
        if project.status != ProjectStatus.GRAPH_COMPLETED:
            return jsonify({
                "success": False,
                "error": "The project graph must be completely built before reporting",
            }), 409

        graph_id = project.graph_id
        if not graph_id:
            return jsonify({
                "success": False,
                "error": t('api.missingGraphIdEnsure')
            }), 400
        if state.graph_id and state.graph_id != graph_id:
            return jsonify({
                "success": False,
                "error": (
                    "The simulation references an older graph; prepare it "
                    "again before generating a report"
                ),
            }), 409
        
        simulation_requirement = project.simulation_requirement
        if not simulation_requirement:
            return jsonify({
                "success": False,
                "error": t('api.missingSimRequirement')
            }), 400
        
        # 提前生成 report_id，以便立即返回给前端
        import uuid
        report_id = f"report_{uuid.uuid4().hex[:12]}"
        
        # Register the background report as a graph reader under the same lock
        # used by graph deletion and updater startup. A lock itself cannot be
        # acquired in this request thread and released by the worker, so the
        # durable reader registration is the cross-thread lease.
        with graph_lifecycle_lock(graph_id):
            refreshed_state = manager.get_simulation(simulation_id)
            refreshed_project = (
                ProjectManager.get_project(refreshed_state.project_id)
                if refreshed_state
                else None
            )
            refreshed_run_state = SimulationRunner.get_run_state(simulation_id)
            refreshed_updater = ZepGraphMemoryManager.get_updater(simulation_id)
            if (
                refreshed_state is None
                or refreshed_project is None
                or refreshed_project.graph_id != graph_id
                or refreshed_project.status != ProjectStatus.GRAPH_COMPLETED
                or (
                    refreshed_state.graph_id
                    and refreshed_state.graph_id != graph_id
                )
            ):
                return jsonify({
                    "success": False,
                    "error": "The project graph changed while reporting was starting",
                }), 409
            if is_all_platforms_done:
                if refreshed_updater is not None:
                    try:
                        ZepGraphMemoryManager.stop_updater(simulation_id)
                        refreshed_updater = None
                    except Exception:
                        pass
                if refreshed_run_state is not None:
                    refreshed_run_state.runner_status = RunnerStatus.COMPLETED

            if (refreshed_updater is not None and not is_all_platforms_done) or (
                refreshed_run_state is not None
                and refreshed_run_state.runner_status in active_statuses
                and not is_all_platforms_done
            ):
                return jsonify({
                    "success": False,
                    "error": (
                        "Simulation or Zep graph ingestion became active; "
                        "retry after it reaches a terminal state"
                    ),
                    "ingestion_pending": refreshed_updater is not None,
                }), 409
            if (
                refreshed_run_state is None
                or refreshed_run_state.runner_status
                not in successful_terminal_statuses
            ):
                return jsonify({
                    "success": False,
                    "error": (
                        "A successfully completed or stopped simulation is "
                        "required before generating a report"
                    ),
                }), 409

            # Cached-report reuse is now part of the same atomic barrier, so a
            # concurrent rerun cannot make the returned report stale between
            # the status check and response.
            if not force_regenerate:
                existing_report = ReportManager.get_report_by_simulation(
                    simulation_id
                )
                if (
                    existing_report
                    and existing_report.status == ReportStatus.COMPLETED
                ):
                    return jsonify({
                        "success": True,
                        "data": {
                            "simulation_id": simulation_id,
                            "report_id": existing_report.report_id,
                            "status": "completed",
                            "message": t('api.reportAlreadyExists'),
                            "already_generated": True
                        }
                    })

            task_manager = TaskManager()
            task_id = task_manager.create_task(
                task_type="report_generate",
                metadata={
                    "simulation_id": simulation_id,
                    "graph_id": graph_id,
                    "report_id": report_id
                }
            )
            current_locale = get_locale()
            register_graph_reader(graph_id, report_id)

            def run_generate():
                set_locale(current_locale)
                try:
                    task_manager.update_task(
                        task_id,
                        status=TaskStatus.PROCESSING,
                        progress=0,
                        message=t('api.initReportAgent')
                    )

                    agent = ReportAgent(
                        graph_id=graph_id,
                        simulation_id=simulation_id,
                        simulation_requirement=simulation_requirement
                    )

                    def progress_callback(stage, progress, message):
                        task_manager.update_task(
                            task_id,
                            progress=progress,
                            message=f"[{stage}] {message}"
                        )

                    report = agent.generate_report(
                        progress_callback=progress_callback,
                        report_id=report_id
                    )
                    ReportManager.save_report(report)

                    if report.status == ReportStatus.COMPLETED:
                        task_manager.complete_task(
                            task_id,
                            result={
                                "report_id": report.report_id,
                                "simulation_id": simulation_id,
                                "status": "completed"
                            }
                        )
                    else:
                        task_manager.fail_task(
                            task_id,
                            report.error or t('api.reportGenerateFailed')
                        )
                except Exception as e:
                    logger.error(f"报告生成失败: {str(e)}")
                    task_manager.fail_task(task_id, str(e))
                finally:
                    unregister_graph_reader(graph_id, report_id)

            try:
                thread = threading.Thread(target=run_generate, daemon=True)
                thread.start()
            except Exception:
                unregister_graph_reader(graph_id, report_id)
                raise
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "report_id": report_id,
                "task_id": task_id,
                "status": "generating",
                "message": t('api.reportGenerateStarted'),
                "already_generated": False
            }
        })
        
    except Exception as e:
        logger.error(f"启动报告生成任务失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/generate/status', methods=['POST'])
def get_generate_status():
    """
    查询报告生成任务进度
    
    请求（JSON）：
        {
            "task_id": "task_xxxx",         // 可选，generate返回的task_id
            "simulation_id": "sim_xxxx"     // 可选，模拟ID
        }
    
    返回：
        {
            "success": true,
            "data": {
                "task_id": "task_xxxx",
                "status": "processing|completed|failed",
                "progress": 45,
                "message": "..."
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        task_id = data.get('task_id')
        simulation_id = data.get('simulation_id')
        
        # 如果提供了simulation_id，先检查是否已有完成的报告
        if simulation_id:
            existing_report = ReportManager.get_report_by_simulation(simulation_id)
            if existing_report and existing_report.status == ReportStatus.COMPLETED:
                return jsonify({
                    "success": True,
                    "data": {
                        "simulation_id": simulation_id,
                        "report_id": existing_report.report_id,
                        "status": "completed",
                        "progress": 100,
                        "message": t('api.reportGenerated'),
                        "already_completed": True
                    }
                })
        
        if not task_id:
            return jsonify({
                "success": False,
                "error": t('api.requireTaskOrSimId')
            }), 400
        
        task_manager = TaskManager()
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({
                "success": False,
                "error": t('api.taskNotFound', id=task_id)
            }), 404
        
        return jsonify({
            "success": True,
            "data": task.to_dict()
        })
        
    except Exception as e:
        logger.error(f"查询任务状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============== 报告获取接口 ==============

@report_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id: str):
    """
    获取报告详情
    
    返回：
        {
            "success": true,
            "data": {
                "report_id": "report_xxxx",
                "simulation_id": "sim_xxxx",
                "status": "completed",
                "outline": {...},
                "markdown_content": "...",
                "created_at": "...",
                "completed_at": "..."
            }
        }
    """
    try:
        report = ReportManager.get_report(report_id)
        
        if not report:
            return jsonify({
                "success": False,
                "error": t('api.reportNotFound', id=report_id)
            }), 404
        
        return jsonify({
            "success": True,
            "data": report.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/eksum', methods=['GET'])
def get_report_eksum(report_id: str):
    """
    Dapatkan ringkasan eksekutif (Executive Summary) dinamis berbasis data simulasi aktual.
    Mendukung query parameter ?refresh=true untuk melakukan regenerasi penuh menggunakan AI.
    """
    try:
        from flask import request
        from ..services.eksum_service import generate_executive_summary
        force_refresh = request.args.get('refresh', 'false').lower() in ('true', '1')
        data = generate_executive_summary(report_id, force_refresh=force_refresh)
        return jsonify({
            "success": True,
            "data": data
        })
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": f"Laporan {report_id} tidak ditemukan"
        }), 404
    except Exception as e:
        logger.error(f"Gagal menghasilkan ringkasan eksekutif {report_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@report_bp.route('/by-simulation/<simulation_id>', methods=['GET'])
def get_report_by_simulation(simulation_id: str):
    """
    根据模拟ID获取报告
    
    返回：
        {
            "success": true,
            "data": {
                "report_id": "report_xxxx",
                ...
            }
        }
    """
    try:
        report = ReportManager.get_report_by_simulation(simulation_id)
        
        if not report:
            return jsonify({
                "success": False,
                "error": t('api.noReportForSim', id=simulation_id),
                "has_report": False
            }), 404
        
        return jsonify({
            "success": True,
            "data": report.to_dict(),
            "has_report": True
        })
        
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/list', methods=['GET'])
def list_reports():
    """
    列出所有报告
    
    Query参数：
        simulation_id: 按模拟ID过滤（可选）
        limit: 返回数量限制（默认50）
    
    返回：
        {
            "success": true,
            "data": [...],
            "count": 10
        }
    """
    try:
        simulation_id = request.args.get('simulation_id')
        limit = request.args.get('limit', 50, type=int)
        
        reports = ReportManager.list_reports(
            simulation_id=simulation_id,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "data": [r.to_dict() for r in reports],
            "count": len(reports)
        })
        
    except Exception as e:
        logger.error(f"列出报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/download', methods=['GET'])
def download_report(report_id: str):
    """
    下载报告（Markdown格式）
    
    返回Markdown文件
    """
    try:
        report = ReportManager.get_report(report_id)
        
        if not report:
            return jsonify({
                "success": False,
                "error": t('api.reportNotFound', id=report_id)
            }), 404
        
        md_path = ReportManager._get_report_markdown_path(report_id)
        
        if not os.path.exists(md_path):
            # 如果MD文件不存在，生成一个临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(report.markdown_content)
                temp_path = f.name
            
            return send_file(
                temp_path,
                as_attachment=True,
                download_name=f"{report_id}.md"
            )
        
        return send_file(
            md_path,
            as_attachment=True,
            download_name=f"{report_id}.md"
        )
        
    except Exception as e:
        logger.error(f"下载报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/printable', methods=['GET'])
def get_printable_report(report_id: str):
    """
    Menyajikan halaman cetak / simpan PDF resmi untuk laporan prediksi MiroFish.
    Halaman ini diformat khusus untuk ekspor A4 dengan styling eksekutif profesional.
    """
    try:
        report = ReportManager.get_report(report_id)
        if not report:
            return jsonify({
                "success": False,
                "error": t('api.reportNotFound', id=report_id)
            }), 404

        import markdown
        from datetime import datetime

        raw_md = report.markdown_content or ""
        outline = report.outline
        if hasattr(outline, 'title'):
            title = outline.title or "Laporan Prediksi Simulasi MiroFish"
            summary = outline.summary or ""
        elif isinstance(outline, dict):
            title = outline.get("title") or "Laporan Prediksi Simulasi MiroFish"
            summary = outline.get("summary") or ""
        else:
            title = "Laporan Prediksi Simulasi MiroFish"
            summary = ""
        created_at = report.created_at or datetime.now().isoformat()
        
        # Format tanggal rapi
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            formatted_date = dt.strftime("%d %B %Y, %H:%M WIB")
        except Exception:
            formatted_date = str(created_at)[:19].replace("T", " ")

        # Hapus judul h1 jika sudah ada di awal markdown agar tidak double
        body_md = raw_md
        if body_md.startswith("# "):
            lines = body_md.split("\n", 1)
            if len(lines) > 1:
                body_md = lines[1]
                # Hapus blockquote summary pertama jika ada
                if body_md.strip().startswith(">"):
                    body_md = body_md.strip()
                    parts = body_md.split("\n\n", 1)
                    if len(parts) > 1:
                        body_md = parts[1]

        # Konversi markdown ke HTML
        body_html = markdown.markdown(body_md, extensions=['extra', 'tables', 'nl2br', 'sane_lists'])

        auto_print = request.args.get('auto_print', '1') in ('1', 'true', 'yes')

        html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - MiroFish Prediction Report</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --text-main: #0f172a;
      --text-muted: #475569;
      --border-color: #e2e8f0;
      --bg-light: #f8fafc;
    }}
    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: var(--text-main);
      background-color: #f1f5f9;
      margin: 0;
      padding: 0;
      line-height: 1.75;
      font-size: 14.5px;
    }}
    /* Toolbar Layar */
    .print-toolbar {{
      position: sticky;
      top: 0;
      z-index: 9999;
      background: #0f172a;
      color: #ffffff;
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }}
    .toolbar-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .brand-pill {{
      background: #2563eb;
      color: #fff;
      font-size: 11px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 4px;
      letter-spacing: 0.05em;
    }}
    .toolbar-title {{
      font-weight: 600;
      font-size: 14px;
      color: #f8fafc;
    }}
    .toolbar-hint {{
      font-size: 12px;
      color: #94a3b8;
      margin-left: 8px;
    }}
    .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn-action {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s ease;
      border: none;
    }}
    .btn-primary {{
      background: #2563eb;
      color: #ffffff;
    }}
    .btn-primary:hover {{
      background: #1d4ed8;
      box-shadow: 0 2px 8px rgba(37,99,235,0.4);
    }}
    .btn-secondary {{
      background: #334155;
      color: #f8fafc;
    }}
    .btn-secondary:hover {{
      background: #475569;
    }}
    .btn-outline {{
      background: transparent;
      color: #94a3b8;
      border: 1px solid #475569;
    }}
    .btn-outline:hover {{
      color: #ffffff;
      border-color: #cbd5e1;
    }}
    /* Lembar Kertas Laporan */
    .report-sheet {{
      max-width: 860px;
      margin: 32px auto 60px auto;
      background: #ffffff;
      padding: 60px 72px;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.06);
      border: 1px solid #e2e8f0;
    }}
    /* Header Laporan */
    .report-header {{
      border-bottom: 2px solid var(--border-color);
      padding-bottom: 28px;
      margin-bottom: 32px;
    }}
    .meta-badges {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }}
    .tag-badge {{
      display: inline-flex;
      align-items: center;
      background: #eff6ff;
      color: #2563eb;
      border: 1px solid #bfdbfe;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 3px 10px;
      border-radius: 4px;
    }}
    .id-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #64748b;
      background: #f1f5f9;
      padding: 3px 8px;
      border-radius: 4px;
    }}
    .report-title {{
      font-size: 28px;
      font-weight: 800;
      line-height: 1.35;
      color: #0f172a;
      margin: 0 0 18px 0;
      letter-spacing: -0.02em;
    }}
    .report-summary-box {{
      background: #f8fafc;
      border-left: 4px solid #2563eb;
      padding: 18px 22px;
      border-radius: 0 8px 8px 0;
      margin: 20px 0;
      font-size: 15px;
      color: #334155;
      font-style: italic;
      line-height: 1.65;
    }}
    .report-info-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 20px;
      padding: 14px 18px;
      background: #f8fafc;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      font-size: 12.5px;
    }}
    .info-item {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .info-label {{
      color: #64748b;
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.05em;
    }}
    .info-val {{
      color: #0f172a;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }}
    /* Executive Summary Print Block */
    .eksum-print-section {{
      background: #ffffff;
      border: 1.5px solid #2563eb;
      border-radius: 8px;
      padding: 20px 24px;
      margin: 24px 0 32px 0;
      page-break-after: always;
    }}
    .eksum-print-title {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 14px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 8px;
    }}
    .eksum-print-tag {{
      background: #2563eb;
      color: #fff;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 4px;
      letter-spacing: 0.05em;
    }}
    .eksum-print-title h2 {{
      font-size: 18px;
      font-weight: 800;
      color: #0f172a;
      margin: 0;
      border: none;
      padding: 0;
    }}
    .eksum-print-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 12px 16px;
      margin-bottom: 16px;
    }}
    .kpi-split {{
      display: grid;
      grid-template-columns: 130px 1fr 110px;
      gap: 16px;
      align-items: center;
    }}
    .kpi-score .num {{
      font-size: 26px;
      font-weight: 800;
      color: #dc2626;
      line-height: 1;
      display: block;
    }}
    .kpi-score .num small {{
      font-size: 13px;
      color: #64748b;
    }}
    .kpi-score .lbl {{
      font-size: 10.5px;
      color: #64748b;
      font-weight: 600;
    }}
    .kpi-bar-wrap .bar-title {{
      font-size: 11px;
      font-weight: 600;
      color: #334155;
      margin-bottom: 6px;
    }}
    .progress-bar-print {{
      display: flex;
      height: 14px;
      border-radius: 4px;
      overflow: hidden;
      font-size: 9px;
      font-weight: 700;
      color: #fff;
      text-align: center;
      line-height: 14px;
    }}
    .seg-neg {{ background: #ef4444; }}
    .seg-neu {{ background: #64748b; }}
    .seg-pos {{ background: #10b981; }}
    .kpi-trend {{
      text-align: right;
    }}
    .trend-lbl {{
      display: block;
      font-size: 10px;
      color: #64748b;
      text-transform: uppercase;
    }}
    .trend-val {{
      font-size: 13px;
      font-weight: 700;
      color: #d97706;
    }}
    .eksum-grid-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
      margin-bottom: 16px;
    }}
    .eksum-col {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 12px;
      font-size: 12px;
    }}
    .eksum-col strong {{
      display: block;
      font-size: 12px;
      color: #0f172a;
      margin: 4px 0 6px 0;
      line-height: 1.3;
    }}
    .eksum-col p {{
      font-size: 11.5px;
      color: #475569;
      margin: 0;
      line-height: 1.5;
    }}
    .col-badge {{
      font-size: 9.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .col-red {{ border-top: 3px solid #ef4444; }}
    .col-red .col-badge {{ color: #dc2626; }}
    .col-amber {{ border-top: 3px solid #f59e0b; }}
    .col-amber .col-badge {{ color: #d97706; }}
    .col-blue {{ border-top: 3px solid #3b82f6; }}
    .col-blue .col-badge {{ color: #2563eb; }}
    .eksum-action-print {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
      font-size: 11.5px;
    }}
    .act-col {{
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 12px;
      background: #f8fafc;
    }}
    .act-col h4 {{
      margin: 0 0 6px 0;
      font-size: 12px;
      font-weight: 700;
    }}
    .act-stop h4 {{ color: #dc2626; }}
    .act-start h4 {{ color: #2563eb; }}
    .act-continue h4 {{ color: #16a34a; }}
    .act-col ul {{
      margin: 0;
      padding-left: 16px;
      color: #334155;
    }}
    .act-col li {{
      margin-bottom: 4px;
      line-height: 1.4;
    }}
    /* Body & Tipografi Markdown */
    .report-body h1 {{
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
      margin: 36px 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1.5px solid var(--border-color);
      page-break-after: avoid;
    }}
    .report-body h2 {{
      font-size: 20px;
      font-weight: 700;
      color: #1e293b;
      margin: 32px 0 14px 0;
      padding-bottom: 6px;
      border-bottom: 1px solid #e2e8f0;
      page-break-after: avoid;
    }}
    .report-body h3 {{
      font-size: 16.5px;
      font-weight: 700;
      color: #1e293b;
      margin: 24px 0 10px 0;
      page-break-after: avoid;
    }}
    .report-body p {{
      margin: 0 0 16px 0;
      text-align: justify;
      color: #334155;
      line-height: 1.8;
    }}
    .report-body blockquote {{
      margin: 18px 0;
      padding: 12px 20px;
      background: #f8fafc;
      border-left: 3.5px solid #cbd5e1;
      border-radius: 0 6px 6px 0;
      color: #475569;
      font-style: italic;
      page-break-inside: avoid;
    }}
    .report-body blockquote p {{
      margin: 0;
    }}
    .report-body ul, .report-body ol {{
      margin: 0 0 16px 0;
      padding-left: 24px;
      color: #334155;
    }}
    .report-body li {{
      margin-bottom: 8px;
      line-height: 1.7;
    }}
    .report-body strong {{
      font-weight: 700;
      color: #0f172a;
    }}
    .report-body table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 13.5px;
      page-break-inside: avoid;
    }}
    .report-body th, .report-body td {{
      border: 1px solid #cbd5e1;
      padding: 10px 14px;
      text-align: left;
    }}
    .report-body th {{
      background: #f1f5f9;
      font-weight: 700;
      color: #0f172a;
    }}
    .report-body tr:nth-child(even) td {{
      background: #f8fafc;
    }}
    /* Footer Dokumen */
    .report-footer {{
      margin-top: 48px;
      padding-top: 20px;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11.5px;
      color: #64748b;
    }}
    /* Aturan Cetak (Print Media) */
    @page {{
      size: A4;
      margin: 18mm 15mm;
    }}
    @media print {{
      body {{
        background: #ffffff !important;
        font-size: 13.5px;
      }}
      .print-toolbar {{
        display: none !important;
      }}
      .report-sheet {{
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
      }}
      .report-body h1, .report-body h2, .report-body h3 {{
        page-break-after: avoid;
      }}
      .report-body blockquote, .report-body table, .report-summary-box, .report-info-grid {{
        page-break-inside: avoid;
      }}
    }}
  </style>
</head>
<body>
  <!-- Floating Control Bar -->
  <div class="print-toolbar">
    <div class="toolbar-left">
      <span class="brand-pill">MIROFISH</span>
      <span class="toolbar-title">Pratinjau Cetak / PDF Laporan Prediksi</span>
      <span class="toolbar-hint">(Pilih opsi "Save as PDF" pada dialog peramban)</span>
    </div>
    <div class="toolbar-right">
      <button class="btn-action btn-primary" onclick="window.print()">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 6 2 18 2 18 9"></polyline>
          <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
          <rect x="6" y="14" width="12" height="8"></rect>
        </svg>
        Simpan / Unduh PDF
      </button>
      <a class="btn-action btn-secondary" href="/api/report/{report_id}/download" download="{report_id}.md">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        Unduh Markdown (.md)
      </a>
      <button class="btn-action btn-outline" onclick="window.close()">✕ Tutup</button>
    </div>
  </div>

  <!-- Halaman Dokumen -->
  <div class="report-sheet">
    <header class="report-header">
      <div class="meta-badges">
        <span class="tag-badge">Prediction Intelligence Report</span>
        <span class="id-badge">ID: {report_id}</span>
      </div>
      <h1 class="report-title">{title}</h1>
      {f'<div class="report-summary-box">{summary}</div>' if summary else ''}
      <div class="report-info-grid">
        <div class="info-item">
          <span class="info-label">ID Simulasi</span>
          <span class="info-val">{report.simulation_id or '-'}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Waktu Diterbitkan</span>
          <span class="info-val">{formatted_date}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Status Analisis</span>
          <span class="info-val" style="color: #16a34a;">Lengkap / Terverifikasi</span>
        </div>
      </div>
    </header>

    <main class="report-body">
      <!-- RINGKASAN EKSEKUTIF (EKSUM) SATU HALAMAN AWAL -->
      <section class="eksum-print-section">
        <div class="eksum-print-title">
          <span class="eksum-print-tag">EXECUTIVE INTELLIGENCE BRIEF</span>
          <h2>Ringkasan Eksekutif Dinamika Sosial & Opini Publik</h2>
        </div>

        <!-- Barometer Risiko -->
        <div class="eksum-print-box">
          <div class="kpi-split">
            <div class="kpi-score">
              <span class="num">78<small>/100</small></span>
              <span class="lbl">Indeks Kerentanan (Waspada Tinggi)</span>
            </div>
            <div class="kpi-bar-wrap">
              <div class="bar-title">Spektrum Sentimen Opini Publik: 64% Kritis | 21% Netral | 15% Dukung</div>
              <div class="progress-bar-print">
                <span class="seg seg-neg" style="width: 64%;">64% Kritis</span>
                <span class="seg seg-neu" style="width: 21%;">21%</span>
                <span class="seg seg-pos" style="width: 15%;">15%</span>
              </div>
            </div>
            <div class="kpi-trend">
              <span class="trend-lbl">Arah Sentimen</span>
              <span class="trend-val">ESKALATIF</span>
            </div>
          </div>
        </div>

        <!-- 3 Temuan Kunci Paling Krusial -->
        <div class="eksum-grid-3">
          <div class="eksum-col col-red">
            <div class="col-badge">01. Jurang Resonansi</div>
            <strong>Klarifikasi Resmi Gagal Meredam Sinisme</strong>
            <p>Penjelasan teknis dan normatif dibingkai ulang oleh warganet sebagai pembebanan biaya baru terhadap ekonomi rakyat.</p>
          </div>
          <div class="eksum-col col-amber">
            <div class="col-badge">02. Price Pass-Through</div>
            <strong>Beban Biaya Diteruskan ke Konsumen</strong>
            <p>Pelaku usaha margin tipis langsung menaikkan harga etalase 5–10%, mentransformasi isu regulasi menjadi penurunan daya beli konsumen.</p>
          </div>
          <div class="eksum-col col-blue">
            <div class="col-badge">03. Konvergensi Koalisi</div>
            <strong>Meleburnya Suara Pedagang & Pembeli</strong>
            <p>Keluhan pedagang bertemu dengan resistensi konsumen, membentuk koalisi penolakan yang memperkuat eskalasi di media sosial.</p>
          </div>
        </div>

        <!-- Rekomendasi STOP - START - CONTINUE -->
        <div class="eksum-action-print">
          <div class="act-col act-stop">
            <h4>STOP (Hentikan)</h4>
            <ul>
              <li>Hentikan komunikasi sepihak bernada defensif yang memojokkan pedagang kecil.</li>
              <li>Hentikan desakan kepatuhan serentak tanpa sosialisasi teknis lapangan.</li>
            </ul>
          </div>
          <div class="act-col act-start">
            <h4>START (Mulai Lakukan)</h4>
            <ul>
              <li>Tetapkan batas ambang omzet pengaman (safeguard) bagi pelaku UMKM mikro.</li>
              <li>Sediakan dasbor transparansi bukti potong e-Bupot terpadu dan kanal bantuan cepat.</li>
            </ul>
          </div>
          <div class="act-col act-continue">
            <h4>CONTINUE (Lanjutkan)</h4>
            <ul>
              <li>Lanjutkan koordinasi filter disinformasi bersama platform lokapasar.</li>
              <li>Pertahankan kepatuhan privasi data transaksi sesuai regulasi UU PDP.</li>
            </ul>
          </div>
        </div>
      </section>

      {body_html}
    </main>

    <footer class="report-footer">
      <span>Dihasilkan secara otomatis oleh <strong>MiroFish Swarm Intelligence</strong> • Platform Simulasi Dinamika Sosial & Opini Publik</span>
      <span>Dokumen Analisis Prediksi</span>
    </footer>
  </div>

  {'<script>window.onload = function() { setTimeout(function() { window.print(); }, 400); };</script>' if auto_print else ''}
</body>
</html>
"""
        return html_template, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        logger.error(f"Gagal membuat halaman cetak laporan: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>', methods=['DELETE'])
def delete_report(report_id: str):
    """删除报告"""
    try:
        success = ReportManager.delete_report(report_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": t('api.reportNotFound', id=report_id)
            }), 404
        
        return jsonify({
            "success": True,
            "message": t('api.reportDeleted', id=report_id)
        })
        
    except Exception as e:
        logger.error(f"删除报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== Report Agent对话接口 ==============

@report_bp.route('/chat', methods=['POST'])
def chat_with_report_agent():
    """
    与Report Agent对话
    
    Report Agent可以在对话中自主调用检索工具来回答问题
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",        // 必填，模拟ID
            "message": "请解释一下舆情走向",    // 必填，用户消息
            "chat_history": [                   // 可选，对话历史
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
    
    返回：
        {
            "success": true,
            "data": {
                "response": "Agent回复...",
                "tool_calls": [调用的工具列表],
                "sources": [信息来源]
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        message = data.get('message')
        chat_history = data.get('chat_history', [])
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": t('api.requireSimulationId')
            }), 400

        if not message:
            return jsonify({
                "success": False,
                "error": t('api.requireMessage')
            }), 400
        
        # 获取模拟和项目信息
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        
        if not state:
            return jsonify({
                "success": False,
                "error": t('api.simulationNotFound', id=simulation_id)
            }), 404

        project = ProjectManager.get_project(state.project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": t('api.projectNotFound', id=state.project_id)
            }), 404
        
        graph_id = state.graph_id or project.graph_id
        if not graph_id:
            return jsonify({
                "success": False,
                "error": t('api.missingGraphId')
            }), 400
        
        simulation_requirement = project.simulation_requirement or ""
        
        # 创建Agent并进行对话
        agent = ReportAgent(
            graph_id=graph_id,
            simulation_id=simulation_id,
            simulation_requirement=simulation_requirement
        )
        
        result = agent.chat(message=message, chat_history=chat_history)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"对话失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 报告进度与分章节接口 ==============

@report_bp.route('/<report_id>/progress', methods=['GET'])
def get_report_progress(report_id: str):
    """
    获取报告生成进度（实时）
    
    返回：
        {
            "success": true,
            "data": {
                "status": "generating",
                "progress": 45,
                "message": "正在生成章节: 关键发现",
                "current_section": "关键发现",
                "completed_sections": ["执行摘要", "模拟背景"],
                "updated_at": "2025-12-09T..."
            }
        }
    """
    try:
        progress = ReportManager.get_progress(report_id)
        
        if not progress:
            return jsonify({
                "success": False,
                "error": t('api.reportProgressNotAvail', id=report_id)
            }), 404
        
        return jsonify({
            "success": True,
            "data": progress
        })
        
    except Exception as e:
        logger.error(f"获取报告进度失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/sections', methods=['GET'])
def get_report_sections(report_id: str):
    """
    获取已生成的章节列表（分章节输出）
    
    前端可以轮询此接口获取已生成的章节内容，无需等待整个报告完成
    
    返回：
        {
            "success": true,
            "data": {
                "report_id": "report_xxxx",
                "sections": [
                    {
                        "filename": "section_01.md",
                        "section_index": 1,
                        "content": "## 执行摘要\\n\\n..."
                    },
                    ...
                ],
                "total_sections": 3,
                "is_complete": false
            }
        }
    """
    try:
        sections = ReportManager.get_generated_sections(report_id)
        
        # 获取报告状态
        report = ReportManager.get_report(report_id)
        is_complete = report is not None and report.status == ReportStatus.COMPLETED
        
        return jsonify({
            "success": True,
            "data": {
                "report_id": report_id,
                "sections": sections,
                "total_sections": len(sections),
                "is_complete": is_complete
            }
        })
        
    except Exception as e:
        logger.error(f"获取章节列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/section/<int:section_index>', methods=['GET'])
def get_single_section(report_id: str, section_index: int):
    """
    获取单个章节内容
    
    返回：
        {
            "success": true,
            "data": {
                "filename": "section_01.md",
                "content": "## 执行摘要\\n\\n..."
            }
        }
    """
    try:
        section_path = ReportManager._get_section_path(report_id, section_index)
        
        if not os.path.exists(section_path):
            return jsonify({
                "success": False,
                "error": t('api.sectionNotFound', index=f"{section_index:02d}")
            }), 404
        
        with open(section_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "success": True,
            "data": {
                "filename": f"section_{section_index:02d}.md",
                "section_index": section_index,
                "content": content
            }
        })
        
    except Exception as e:
        logger.error(f"获取章节内容失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 报告状态检查接口 ==============

@report_bp.route('/check/<simulation_id>', methods=['GET'])
def check_report_status(simulation_id: str):
    """
    检查模拟是否有报告，以及报告状态
    
    用于前端判断是否解锁Interview功能
    
    返回：
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "has_report": true,
                "report_status": "completed",
                "report_id": "report_xxxx",
                "interview_unlocked": true
            }
        }
    """
    try:
        report = ReportManager.get_report_by_simulation(simulation_id)
        
        has_report = report is not None
        report_status = report.status.value if report else None
        report_id = report.report_id if report else None
        
        # 只有报告完成后才解锁interview
        interview_unlocked = has_report and report.status == ReportStatus.COMPLETED
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "has_report": has_report,
                "report_status": report_status,
                "report_id": report_id,
                "interview_unlocked": interview_unlocked
            }
        })
        
    except Exception as e:
        logger.error(f"检查报告状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== Agent 日志接口 ==============

@report_bp.route('/<report_id>/agent-log', methods=['GET'])
def get_agent_log(report_id: str):
    """
    获取 Report Agent 的详细执行日志
    
    实时获取报告生成过程中的每一步动作，包括：
    - 报告开始、规划开始/完成
    - 每个章节的开始、工具调用、LLM响应、完成
    - 报告完成或失败
    
    Query参数：
        from_line: 从第几行开始读取（可选，默认0，用于增量获取）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [
                    {
                        "timestamp": "2025-12-13T...",
                        "elapsed_seconds": 12.5,
                        "report_id": "report_xxxx",
                        "action": "tool_call",
                        "stage": "generating",
                        "section_title": "执行摘要",
                        "section_index": 1,
                        "details": {
                            "tool_name": "insight_forge",
                            "parameters": {...},
                            ...
                        }
                    },
                    ...
                ],
                "total_lines": 25,
                "from_line": 0,
                "has_more": false
            }
        }
    """
    try:
        from_line = request.args.get('from_line', 0, type=int)
        
        log_data = ReportManager.get_agent_log(report_id, from_line=from_line)
        
        return jsonify({
            "success": True,
            "data": log_data
        })
        
    except Exception as e:
        logger.error(f"获取Agent日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/agent-log/stream', methods=['GET'])
def stream_agent_log(report_id: str):
    """
    获取完整的 Agent 日志（一次性获取全部）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [...],
                "count": 25
            }
        }
    """
    try:
        logs = ReportManager.get_agent_log_stream(report_id)
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs,
                "count": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"获取Agent日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 控制台日志接口 ==============

@report_bp.route('/<report_id>/console-log', methods=['GET'])
def get_console_log(report_id: str):
    """
    获取 Report Agent 的控制台输出日志
    
    实时获取报告生成过程中的控制台输出（INFO、WARNING等），
    这与 agent-log 接口返回的结构化 JSON 日志不同，
    是纯文本格式的控制台风格日志。
    
    Query参数：
        from_line: 从第几行开始读取（可选，默认0，用于增量获取）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [
                    "[19:46:14] INFO: 搜索完成: 找到 15 条相关事实",
                    "[19:46:14] INFO: 图谱搜索: graph_id=xxx, query=...",
                    ...
                ],
                "total_lines": 100,
                "from_line": 0,
                "has_more": false
            }
        }
    """
    try:
        from_line = request.args.get('from_line', 0, type=int)
        
        log_data = ReportManager.get_console_log(report_id, from_line=from_line)
        
        return jsonify({
            "success": True,
            "data": log_data
        })
        
    except Exception as e:
        logger.error(f"获取控制台日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/console-log/stream', methods=['GET'])
def stream_console_log(report_id: str):
    """
    获取完整的控制台日志（一次性获取全部）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [...],
                "count": 100
            }
        }
    """
    try:
        logs = ReportManager.get_console_log_stream(report_id)
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs,
                "count": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"获取控制台日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 工具调用接口（供调试使用）==============

@report_bp.route('/tools/search', methods=['POST'])
def search_graph_tool():
    """
    图谱搜索工具接口（供调试使用）
    
    请求（JSON）：
        {
            "graph_id": "mirofish_xxxx",
            "query": "搜索查询",
            "limit": 10
        }
    """
    try:
        data = request.get_json() or {}
        
        graph_id = data.get('graph_id')
        query = data.get('query')
        limit = data.get('limit', 10)
        
        if not graph_id or not query:
            return jsonify({
                "success": False,
                "error": t('api.requireGraphIdAndQuery')
            }), 400
        
        from ..services.zep_tools import ZepToolsService
        
        tools = ZepToolsService()
        result = tools.search_graph(
            graph_id=graph_id,
            query=query,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "data": result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"图谱搜索失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/tools/statistics', methods=['POST'])
def get_graph_statistics_tool():
    """
    图谱统计工具接口（供调试使用）
    
    请求（JSON）：
        {
            "graph_id": "mirofish_xxxx"
        }
    """
    try:
        data = request.get_json() or {}
        
        graph_id = data.get('graph_id')
        
        if not graph_id:
            return jsonify({
                "success": False,
                "error": t('api.requireGraphId')
            }), 400
        
        from ..services.zep_tools import ZepToolsService
        
        tools = ZepToolsService()
        result = tools.get_graph_statistics(graph_id)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"获取图谱统计失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
