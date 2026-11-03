import service from './index'

/**
 * 开始报告生成
 * @param {Object} data - { simulation_id, force_regenerate? }
 */
export const generateReport = (data) => {
  return service.post('/api/report/generate', data)
}

/**
 * 获取模拟关联的报告
 * @param {string} simulationId
 */
export const getReportBySimulation = (simulationId) => {
  return service.get(`/api/report/by-simulation/${simulationId}`)
}

/**
 * 获取报告生成状态
 * @param {string} reportId
 */
export const getReportStatus = (reportId) => {
  return service.get(`/api/report/generate/status`, { params: { report_id: reportId } })
}

/**
 * 获取 Agent 日志（增量）
 * @param {string} reportId
 * @param {number} fromLine - 从第几行开始获取
 */
export const getAgentLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/agent-log`, { params: { from_line: fromLine } })
}

/**
 * 获取控制台日志（增量）
 * @param {string} reportId
 * @param {number} fromLine - 从第几行开始获取
 */
export const getConsoleLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/console-log`, { params: { from_line: fromLine } })
}

/**
 * 获取报告详情
 * @param {string} reportId
 */
export const getReport = (reportId) => {
  return service.get(`/api/report/${reportId}`)
}

/**
 * Dapatkan data Ringkasan Eksekutif (Eksum) dinamis berbasis AI
 * @param {string} reportId
 * @param {boolean} refresh
 */
export const getExecutiveSummary = (reportId, refresh = false) => {
  return service.get(`/api/report/${reportId}/eksum${refresh ? '?refresh=true' : ''}`)
}

/**
 * 与 Report Agent 对话
 * @param {Object} data - { simulation_id, message, chat_history? }
 */
export const chatWithReport = (data) => {
  return service.post('/api/report/chat', data)
}

/**
 * Muat riwayat interaksi obrolan & survei secara persisten dari server
 * @param {string} simulationId
 */
export const getInteractionHistory = (simulationId) => {
  return service.get(`/api/report/interaction/history?simulation_id=${simulationId}`)
}

/**
 * Simpan riwayat interaksi obrolan & survei secara persisten ke server
 * @param {Object} data - { simulation_id, chat_cache, survey_results?, active_target? }
 */
export const saveInteractionHistory = (data) => {
  return service.post('/api/report/interaction/history', data)
}

/**
 * Hapus riwayat interaksi obrolan dari server
 * @param {string} simulationId
 * @param {string} target - 'all' atau 'report_agent' atau 'agent_X'
 */
export const deleteInteractionHistory = (simulationId, target = 'all') => {
  return service.delete(`/api/report/interaction/history?simulation_id=${simulationId}&target=${target}`)
}
