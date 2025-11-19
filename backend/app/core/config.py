"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "小说生成智能体框架"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://novel_user:novel_password@localhost:5432/novel_generate"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Azure OpenAI配置
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None
    AZURE_OPENAI_MODEL: str = "gpt-4"
    AZURE_OPENAI_TEMPERATURE: float = 0.7
    AZURE_OPENAI_MAX_TOKENS: int = 4000
    
    # 阿里云通义千问配置
    ALIBABA_QWEN_API_KEY: Optional[str] = None
    ALIBABA_QWEN_ENDPOINT: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    ALIBABA_QWEN_MODEL: str = "qwen3-max"
    ALIBABA_QWEN_TEMPERATURE: float = 0.7
    ALIBABA_QWEN_MAX_TOKENS: int = 20000
    ALIBABA_QWEN_TIMEOUT: int = 600  # 10分钟超时
    
    # LLM 提供商选择
    LLM_PROVIDER: str = "alibaba"  # 可选: "azure", "alibaba"
    
    # 兼容性配置 - 从现有环境变量映射
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_AZURE_DEPLOYMENT: Optional[str] = None
    
    # 文件输出配置
    NOVEL_OUTPUT_DIR: str = "novel"
    OUTPUT_FORMAT: str = "markdown"
    
    # 本地LLM配置
    LOCAL_LLM_ENABLED: bool = False
    LOCAL_LLM_MODEL_PATH: Optional[str] = None
    LOCAL_LLM_DEVICE: str = "cpu"
    
    # 评分配置
    SCORING_WEIGHTS: dict = {
        "logic_consistency": 0.3,
        "dramatic_conflict": 0.2,
        "character_consistency": 0.2,
        "writing_quality": 0.15,
        "innovation": 0.1,
        "user_preference": 0.05
    }
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    CACHE_PREFIX: str = "novel_generate"
    
    # 任务队列配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = "../.env"  # 环境变量文件在项目根目录
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的字段
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 自动映射兼容性配置
        self._map_compatibility_config()
    
    def _map_compatibility_config(self):
        """映射兼容性配置"""
        # 如果Azure配置为空，尝试从OpenAI配置映射
        if not self.AZURE_OPENAI_API_KEY and self.OPENAI_API_KEY:
            self.AZURE_OPENAI_API_KEY = self.OPENAI_API_KEY
        
        if not self.AZURE_OPENAI_ENDPOINT and self.OPENAI_BASE_URL:
            self.AZURE_OPENAI_ENDPOINT = self.OPENAI_BASE_URL
        
        if not self.AZURE_OPENAI_DEPLOYMENT_NAME and self.OPENAI_AZURE_DEPLOYMENT:
            self.AZURE_OPENAI_DEPLOYMENT_NAME = self.OPENAI_AZURE_DEPLOYMENT


# 创建全局配置实例
settings = Settings()
