"""
系统配置与连通性测试 API 路由
支持在 Web 界面可视化修改 API Key、切换模型和存储模式，无需重启后端
"""

import os
from flask import Blueprint, request, jsonify
from openai import OpenAI

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.api.settings')

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


def _mask_key(key: str) -> str:
    """脱敏显示 API Key"""
    if not key:
        return ""
    key = str(key).strip()
    if len(key) <= 8:
        return "********"
    return f"{key[:4]}****{key[-4:]}"


@settings_bp.route('/config', methods=['GET'])
def get_config():
    """获取当前系统运行配置（敏感信息脱敏）"""
    return jsonify({
        "success": True,
        "config": {
            "llm_base_url": Config.LLM_BASE_URL,
            "llm_model_name": Config.LLM_MODEL_NAME,
            "llm_model_tier2": Config.LLM_MODEL_TIER2,
            "llm_api_key_masked": _mask_key(Config.LLM_API_KEY),
            "has_llm_api_key": bool(Config.LLM_API_KEY),
            "memory_mode": Config.MEMORY_MODE,
            "zep_api_key_masked": _mask_key(Config.ZEP_API_KEY),
            "has_zep_api_key": bool(Config.ZEP_API_KEY),
            "simulation_timezone": Config.SIMULATION_TIMEZONE,
        }
    })


@settings_bp.route('/config', methods=['POST'])
def save_config():
    """保存并持久化系统运行配置"""
    try:
        data = request.get_json() or {}
        
        # 处理更新字段
        update_payload = {}
        
        if 'llm_base_url' in data and data['llm_base_url']:
            update_payload['llm_base_url'] = data['llm_base_url'].strip()
            
        if 'llm_model_name' in data and data['llm_model_name']:
            update_payload['llm_model_name'] = data['llm_model_name'].strip()
            
        if 'llm_model_tier2' in data:
            update_payload['llm_model_tier2'] = (data['llm_model_tier2'] or '').strip()
            
        # 如果传入了新的 API Key（非脱敏星号格式）
        if 'llm_api_key' in data and data['llm_api_key'] and '****' not in data['llm_api_key']:
            update_payload['llm_api_key'] = data['llm_api_key'].strip()
            
        if 'memory_mode' in data and data['memory_mode']:
            update_payload['memory_mode'] = data['memory_mode'].strip()
            
        if 'zep_api_key' in data and data['zep_api_key'] and '****' not in data['zep_api_key']:
            update_payload['zep_api_key'] = data['zep_api_key'].strip()
            
        if 'simulation_timezone' in data and data['simulation_timezone']:
            update_payload['simulation_timezone'] = data['simulation_timezone'].strip()
            
        Config.update_settings(update_payload)
        logger.info(f"System settings updated via Web UI: {list(update_payload.keys())}")
        
        return jsonify({
            "success": True,
            "message": "Pengaturan berhasil disimpan dan langsung aktif!",
            "updated_fields": list(update_payload.keys())
        })
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@settings_bp.route('/test-llm', methods=['POST'])
def test_llm():
    """测试指定 LLM 配置的连通性"""
    try:
        data = request.get_json() or {}
        
        # 优先使用传入的参数，否则使用当前全局配置
        api_key = data.get('llm_api_key') or Config.LLM_API_KEY
        base_url = data.get('llm_base_url') or Config.LLM_BASE_URL
        model_name = data.get('llm_model_name') or Config.LLM_MODEL_NAME
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": "API Key belum diisi!"
            }), 400
            
        if not base_url:
            return jsonify({
                "success": False,
                "error": "Base URL belum diisi!"
            }), 400
            
        if not model_name:
            return jsonify({
                "success": False,
                "error": "Nama Model belum dipilih!"
            }), 400

        # 发送极简测试请求
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=15.0
        )
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Ping! Jawab hanya dengan 1 kata: OK"}
            ],
            max_tokens=10
        )
        
        reply = response.choices[0].message.content.strip()
        
        return jsonify({
            "success": True,
            "message": f"Koneksi berhasil! Respons model ({model_name}): '{reply}'",
            "model_tested": model_name
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"LLM connection test failed: {error_msg}")
        return jsonify({
            "success": False,
            "error": f"Gagal terhubung ke API: {error_msg}"
        }), 400
