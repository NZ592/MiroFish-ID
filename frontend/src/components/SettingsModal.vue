<template>
  <div v-if="visible" class="modal-backdrop" @click.self="close">
    <div class="settings-dialog">
      <!-- Header -->
      <div class="dialog-header">
        <div class="header-title">
          <span class="icon">⚙️</span>
          <h3>{{ $t('settings.title') }}</h3>
        </div>
        <button class="close-btn" @click="close">×</button>
      </div>

      <!-- Navigation Tabs -->
      <div class="dialog-tabs">
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'llm' }"
          @click="currentTab = 'llm'"
        >
          {{ $t('settings.tabLLM') }}
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'memory' }"
          @click="currentTab = 'memory'"
        >
          {{ $t('settings.tabMemory') }}
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'preferences' }"
          @click="currentTab = 'preferences'"
        >
          {{ $t('settings.tabPreferences') }}
        </button>
      </div>

      <!-- Tab Content Area -->
      <div class="dialog-body">
        <!-- 1. LLM Tab -->
        <div v-if="currentTab === 'llm'" class="tab-panel">
          <!-- Base URL -->
          <div class="form-group">
            <label class="form-label">{{ $t('settings.baseUrl') }}</label>
            <input
              type="text"
              class="form-input mono"
              v-model="form.llm_base_url"
              placeholder="https://api.openai.com/v1"
            />
          </div>

          <!-- API Key -->
          <div class="form-group">
            <label class="form-label">{{ $t('settings.apiKey') }}</label>
            <div class="input-with-button">
              <input
                :type="showApiKey ? 'text' : 'password'"
                class="form-input mono"
                v-model="form.llm_api_key"
                :placeholder="apiKeyMaskedPlaceholder"
              />
              <button class="toggle-eye-btn" type="button" @click="showApiKey = !showApiKey">
                {{ showApiKey ? '🔒' : '👁️' }}
              </button>
            </div>
          </div>

          <!-- Primary Model -->
          <div class="form-group">
            <label class="form-label">{{ $t('settings.primaryModel') }}</label>
            <input
              type="text"
              class="form-input mono"
              v-model="form.llm_model_name"
              placeholder="gpt-4o-mini / gemini-1.5-flash / qwen-plus"
            />
          </div>

          <!-- Secondary Model (Tier 2 Netizens) -->
          <div class="form-group">
            <label class="form-label">{{ $t('settings.secondaryModel') }}</label>
            <input
              type="text"
              class="form-input mono"
              v-model="form.llm_model_tier2"
              placeholder="qwen-turbo / gpt-4o-mini / gemini-1.5-flash (opsional)"
            />
            <span class="field-hint">{{ $t('settings.secondaryModelHint') }}</span>
          </div>

          <!-- Test Connection Button & Status -->
          <div class="test-connection-section">
            <button
              class="btn-test"
              :disabled="testingConnection"
              @click="testLLMConnection"
            >
              <span v-if="testingConnection" class="spinner"></span>
              {{ testingConnection ? $t('settings.testing') : $t('settings.testConnection') }}
            </button>

            <div v-if="testResult" class="test-feedback" :class="testResult.success ? 'success' : 'error'">
              {{ testResult.message }}
            </div>
          </div>
        </div>

        <!-- 2. Memory Tab -->
        <div v-if="currentTab === 'memory'" class="tab-panel">
          <div class="form-group">
            <label class="form-label">{{ $t('settings.memoryMode') }}</label>
            <div class="radio-options">
              <label class="radio-card" :class="{ selected: form.memory_mode === 'local' }">
                <input type="radio" value="local" v-model="form.memory_mode" />
                <div class="radio-text">
                  <strong>{{ $t('settings.memoryLocal') }}</strong>
                  <p>Memori graf dijalankan sepenuhnya di komputer lokal menggunakan SQLite. Tanpa akun, tanpa biaya API Zep Cloud.</p>
                </div>
              </label>

              <label class="radio-card" :class="{ selected: form.memory_mode === 'zep' }">
                <input type="radio" value="zep" v-model="form.memory_mode" />
                <div class="radio-text">
                  <strong>{{ $t('settings.memoryZep') }}</strong>
                  <p>Menghubungkan ke Zep Cloud API resmi untuk GraphRAG tersinkronisasi di cloud.</p>
                </div>
              </label>
            </div>
          </div>

          <div v-if="form.memory_mode === 'zep'" class="form-group">
            <label class="form-label">{{ $t('settings.zepApiKey') }}</label>
            <input
              type="password"
              class="form-input mono"
              v-model="form.zep_api_key"
              :placeholder="zepKeyMaskedPlaceholder"
            />
          </div>
        </div>

        <!-- 3. Preferences Tab -->
        <div v-if="currentTab === 'preferences'" class="tab-panel">
          <div class="form-group">
            <label class="form-label">{{ $t('settings.timezone') }}</label>
            <select class="form-select" v-model="form.simulation_timezone">
              <option value="WIB">WIB (Waktu Indonesia Barat, UTC+7 - Jakarta/Bandung/Surabaya)</option>
              <option value="WITA">WITA (Waktu Indonesia Tengah, UTC+8 - Bali/Makassar/Balikpapan)</option>
              <option value="WIT">WIT (Waktu Indonesia Timur, UTC+9 - Maluku/Papua)</option>
              <option value="CHINA">CST (China Standard Time, UTC+8 - Beijing)</option>
              <option value="DEFAULT">UTC / Universal Standard Time</option>
            </select>
            <span class="field-hint">Mengatur pola sirkadian (jam bangun, jam kerja, dan jam sibuk media sosial) agar realistis dengan kebiasaan masyarakat setempat.</span>
          </div>
        </div>
      </div>

      <!-- Footer Buttons -->
      <div class="dialog-footer">
        <button class="btn-cancel" @click="close">{{ $t('common.cancel') }}</button>
        <button class="btn-save" :disabled="saving" @click="saveSettings">
          <span v-if="saving" class="spinner"></span>
          {{ saving ? $t('common.processing') : $t('settings.saveSettings') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'saved'])

const { t } = useI18n()

const currentTab = ref('llm')
const showApiKey = ref(false)
const testingConnection = ref(false)
const saving = ref(false)
const testResult = ref(null)

const apiKeyMaskedPlaceholder = ref('Kunci API aktif tersimpan')
const zepKeyMaskedPlaceholder = ref('Kunci Zep API tersimpan')

const form = reactive({
  llm_base_url: 'https://api.openai.com/v1',
  llm_api_key: '',
  llm_model_name: 'gpt-4o-mini',
  llm_model_tier2: '',
  memory_mode: 'local',
  zep_api_key: '',
  simulation_timezone: 'WIB'
})

const fetchCurrentConfig = async () => {
  try {
    const res = await fetch('/api/settings/config')
    const text = await res.text()
    if (!text) return
    const data = JSON.parse(text)
    if (data.success && data.config) {
      const cfg = data.config
      if (cfg.llm_base_url) form.llm_base_url = cfg.llm_base_url
      if (cfg.llm_model_name) form.llm_model_name = cfg.llm_model_name
      if (cfg.llm_model_tier2) form.llm_model_tier2 = cfg.llm_model_tier2
      if (cfg.memory_mode) form.memory_mode = cfg.memory_mode
      if (cfg.simulation_timezone) form.simulation_timezone = cfg.simulation_timezone
      if (cfg.llm_api_key_masked) {
        apiKeyMaskedPlaceholder.value = `Tersimpan: ${cfg.llm_api_key_masked}`
      }
      if (cfg.zep_api_key_masked) {
        zepKeyMaskedPlaceholder.value = `Tersimpan: ${cfg.zep_api_key_masked}`
      }
    }
  } catch (e) {
    console.warn('Backend server not connected yet:', e.message)
  }
}

const testLLMConnection = async () => {
  testingConnection.value = true
  testResult.value = null
  try {
    const res = await fetch('/api/settings/test-llm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        llm_base_url: form.llm_base_url,
        llm_api_key: form.llm_api_key,
        llm_model_name: form.llm_model_name
      })
    })

    const text = await res.text()
    let data
    try {
      data = JSON.parse(text)
    } catch (parseErr) {
      if (!res.ok || !text) {
        throw new Error(`Server Backend belum aktif di port 5001 (Status: ${res.status}). Jalankan ./start.sh atau 'cd backend && python run.py'`)
      }
      throw new Error(`Respons tidak valid: ${text.slice(0, 100)}`)
    }

    if (data.success) {
      testResult.value = {
        success: true,
        message: data.message || t('settings.testSuccess')
      }
    } else {
      testResult.value = {
        success: false,
        message: data.error || t('settings.testFailed', { error: 'Unknown' })
      }
    }
  } catch (e) {
    testResult.value = {
      success: false,
      message: t('settings.testFailed', { error: e.message })
    }
  } finally {
    testingConnection.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const payload = {
      llm_base_url: form.llm_base_url,
      llm_model_name: form.llm_model_name,
      llm_model_tier2: form.llm_model_tier2,
      memory_mode: form.memory_mode,
      simulation_timezone: form.simulation_timezone
    }
    if (form.llm_api_key) {
      payload.llm_api_key = form.llm_api_key
    }
    if (form.zep_api_key) {
      payload.zep_api_key = form.zep_api_key
    }

    const res = await fetch('/api/settings/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const text = await res.text()
    let data
    try {
      data = JSON.parse(text)
    } catch (parseErr) {
      throw new Error(`Backend belum aktif di port 5001 (Status: ${res.status})`)
    }

    if (data.success) {
      alert(t('settings.saveSuccess'))
      emit('saved', payload)
      close()
    } else {
      alert(t('settings.saveError', { error: data.error || 'Unknown' }))
    }
  } catch (e) {
    alert(t('settings.saveError', { error: e.message }))
  } finally {
    saving.value = false
  }
}

const close = () => {
  emit('update:visible', false)
}

onMounted(() => {
  fetchCurrentConfig()
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(10, 15, 25, 0.75);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', -apple-system, sans-serif;
}

.settings-dialog {
  background: #121824;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  width: 90%;
  max-width: 620px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
  color: #E2E8F0;
  overflow: hidden;
}

.dialog-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #172033;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title .icon {
  font-size: 1.25rem;
}

.header-title h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #F8FAFC;
}

.close-btn {
  background: transparent;
  border: none;
  color: #94A3B8;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #FFF;
}

.dialog-tabs {
  display: flex;
  background: #0D131F;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0 16px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #94A3B8;
  padding: 12px 18px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn.active {
  color: #38BDF8;
  border-bottom-color: #38BDF8;
}

.dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #CBD5E1;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input, .form-select {
  width: 100%;
  background: #1A2234;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #F8FAFC;
  padding: 9px 12px;
  font-size: 0.85rem;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-input.mono {
  font-family: 'JetBrains Mono', monospace;
}

.form-input:focus, .form-select:focus {
  border-color: #38BDF8;
}

.input-with-button {
  display: flex;
  gap: 8px;
}

.toggle-eye-btn {
  background: #1E293B;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #CBD5E1;
  padding: 0 14px;
  cursor: pointer;
}

.field-hint {
  display: block;
  font-size: 0.75rem;
  color: #64748B;
  margin-top: 4px;
}

.test-connection-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
}

.btn-test {
  background: #1E293B;
  border: 1px solid #38BDF8;
  color: #38BDF8;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-test:hover:not(:disabled) {
  background: #38BDF8;
  color: #0F172A;
}

.btn-test:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.test-feedback {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 0.8rem;
  line-height: 1.4;
}

.test-feedback.success {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid #22C55E;
  color: #4ADE80;
}

.test-feedback.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid #EF4444;
  color: #F87171;
}

.radio-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-card {
  display: flex;
  gap: 12px;
  padding: 12px 14px;
  background: #1A2234;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-card.selected {
  border-color: #38BDF8;
  background: rgba(56, 189, 248, 0.08);
}

.radio-text strong {
  display: block;
  font-size: 0.85rem;
  color: #F1F5F9;
  margin-bottom: 2px;
}

.radio-text p {
  margin: 0;
  font-size: 0.75rem;
  color: #94A3B8;
  line-height: 1.35;
}

.dialog-footer {
  padding: 14px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background: #172033;
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #CBD5E1;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.82rem;
  cursor: pointer;
}

.btn-save {
  background: #0284C7;
  border: none;
  color: #FFF;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-save:hover:not(:disabled) {
  background: #0369A1;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>