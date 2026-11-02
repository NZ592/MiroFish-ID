"""\n配置管理\n统一从项目根目录的 .env 文件加载配置\n"""

import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
# 路径: MiroFish/.env (相对于 backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    # 如果根目录没有 .env，尝试加载环境变量（用于生产环境）
    load_dotenv(override=True)


class Config:
    """Flask配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # JSON配置 - 禁用ASCII转义，让中文直接显示
    JSON_AS_ASCII = False
    
    # LLM配置（统一使用OpenAI格式）
    LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')
    LLM_MODEL_TIER2 = os.environ.get('LLM_MODEL_TIER2', '')  # 辅助模型（快速/廉价）
    
    # 内存与图谱模式配置 ('local' 或 'zep')
    MEMORY_MODE = os.environ.get('MEMORY_MODE', 'local' if not os.environ.get('ZEP_API_KEY') else 'zep')
    
    # 模拟时区配置 (WIB, WITA, WIT, CHINA, DEFAULT)
    SIMULATION_TIMEZONE = os.environ.get('SIMULATION_TIMEZONE', 'WIB')

    # Zep配置
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY', '')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # 文本处理配置
    DEFAULT_CHUNK_SIZE = 500  # 默认切块大小
    DEFAULT_CHUNK_OVERLAP = 50  # 默认重叠大小
    
    # OASIS模拟配置
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    
    # OASIS平台可用动作配置
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    # Report Agent配置
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))
    
    @classmethod
    def validate(cls) -> list[str]:
        """验证必要配置"""
        errors: list[str] = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY 未配置")
        if cls.MEMORY_MODE == 'zep' and not cls.ZEP_API_KEY:
            errors.append("ZEP_API_KEY 未配置（当前设置为 Zep Cloud 模式）")
        if os.environ.get("ZEP_API_URL"):
            errors.append("ZEP_API_URL 不受支持；MiroFish 仅连接 Zep Cloud")
        if cls.DEBUG:
            import warnings
            warnings.warn("Flask DEBUG mode is enabled. Do not use in production.", RuntimeWarning)
        return errors

    @classmethod
    def update_settings(cls, settings: dict) -> None:
        """动态更新配置并持久化写入 .env 文件"""
        env_keys = {
            'llm_api_key': 'LLM_API_KEY',
            'llm_base_url': 'LLM_BASE_URL',
            'llm_model_name': 'LLM_MODEL_NAME',
            'llm_model_tier2': 'LLM_MODEL_TIER2',
            'memory_mode': 'MEMORY_MODE',
            'zep_api_key': 'ZEP_API_KEY',
            'simulation_timezone': 'SIMULATION_TIMEZONE',
        }
        
        # 1. 更新运行时 Config 类属性与 os.environ
        for key, val in settings.items():
            env_var = env_keys.get(key)
            if env_var and val is not None:
                val_str = str(val).strip()
                setattr(cls, env_var, val_str)
                os.environ[env_var] = val_str

        # 2. 写入/更新项目根目录的 .env 文件
        env_path = project_root_env
        existing_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                existing_lines = f.readlines()
        
        env_dict = {}
        for line in existing_lines:
            line_str = line.strip()
            if line_str and not line_str.startswith('#') and '=' in line_str:
                k, v = line_str.split('=', 1)
                env_dict[k.strip()] = v.strip()
        
        for key, val in settings.items():
            env_var = env_keys.get(key)
            if env_var and val is not None:
                env_dict[env_var] = str(val).strip()

        # 重新生成并写入 .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# MiroFish Environment Configuration (Auto-updated via UI)\n")
            for k, v in env_dict.items():
                f.write(f"{k}={v}\n")
