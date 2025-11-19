"""
LLM客户端工具类
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from app.core.config import settings


class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_chat(self, messages: list, **kwargs) -> str:
        """生成对话"""
        pass


class AzureOpenAIClient(BaseLLMClient):
    """Azure OpenAI客户端"""
    
    def __init__(self):
        from openai import AsyncAzureOpenAI
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        response = await self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', settings.AZURE_OPENAI_TEMPERATURE),
            max_tokens=kwargs.get('max_tokens', settings.AZURE_OPENAI_MAX_TOKENS)
        )
        return response.choices[0].message.content
    
    async def generate_chat(self, messages: list, **kwargs) -> str:
        """生成对话"""
        response = await self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            temperature=kwargs.get('temperature', settings.AZURE_OPENAI_TEMPERATURE),
            max_tokens=kwargs.get('max_tokens', settings.AZURE_OPENAI_MAX_TOKENS)
        )
        return response.choices[0].message.content


class AlibabaQwenClient(BaseLLMClient):
    """阿里云通义千问客户端"""
    
    def __init__(self):
        import dashscope
        from app.core.config import settings
        
        # 从settings获取API key
        api_key = settings.ALIBABA_QWEN_API_KEY
        if not api_key:
            raise ValueError("ALIBABA_QWEN_API_KEY 未配置，请检查环境变量设置")
        
        # 验证API key格式
        if not api_key.startswith('sk-'):
            raise ValueError(f"ALIBABA_QWEN_API_KEY 格式错误，应以'sk-'开头，当前值: {api_key[:10]}...")
        
        dashscope.api_key = api_key
        self.dashscope = dashscope
        
        # 设置超时时间为10分钟（600秒）
        import requests
        dashscope.api_timeout = settings.ALIBABA_QWEN_TIMEOUT  # 使用配置文件中的超时设置
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        from dashscope import Generation
        
        try:
            response = Generation.call(
                model=settings.ALIBABA_QWEN_MODEL,
                prompt=prompt,
                temperature=kwargs.get('temperature', settings.ALIBABA_QWEN_TEMPERATURE),
                max_tokens=kwargs.get('max_tokens', settings.ALIBABA_QWEN_MAX_TOKENS)
            )
            
            if response.status_code == 200:
                if hasattr(response.output, 'choices') and response.output.choices:
                    return response.output.choices[0].message.content
                elif hasattr(response.output, 'text') and response.output.text:
                    return response.output.text
                else:
                    raise Exception("阿里云API响应格式异常，无法获取文本内容")
            else:
                error_msg = f"阿里云API调用失败 (状态码: {response.status_code})"
                if hasattr(response, 'message'):
                    error_msg += f": {response.message}"
                if hasattr(response, 'code'):
                    error_msg += f" (错误代码: {response.code})"
                raise Exception(error_msg)
        except Exception as e:
            if "No api key provided" in str(e):
                raise ValueError("DashScope API密钥未正确设置，请检查ALIBABA_QWEN_API_KEY环境变量")
            raise
    
    async def generate_chat(self, messages: list, **kwargs) -> str:
        """生成对话"""
        from dashscope import Generation
        
        try:
            # 将messages转换为阿里云格式
            prompt = self._convert_messages_to_prompt(messages)
            
            response = Generation.call(
                model=settings.ALIBABA_QWEN_MODEL,
                prompt=prompt,
                temperature=kwargs.get('temperature', settings.ALIBABA_QWEN_TEMPERATURE),
                max_tokens=kwargs.get('max_tokens', settings.ALIBABA_QWEN_MAX_TOKENS)
            )
            
            if response.status_code == 200:
                if hasattr(response.output, 'choices') and response.output.choices:
                    return response.output.choices[0].message.content
                elif hasattr(response.output, 'text') and response.output.text:
                    return response.output.text
                else:
                    raise Exception("阿里云API响应格式异常，无法获取文本内容")
            else:
                error_msg = f"阿里云API调用失败 (状态码: {response.status_code})"
                if hasattr(response, 'message'):
                    error_msg += f": {response.message}"
                if hasattr(response, 'code'):
                    error_msg += f" (错误代码: {response.code})"
                raise Exception(error_msg)
        except Exception as e:
            if "No api key provided" in str(e):
                raise ValueError("DashScope API密钥未正确设置，请检查ALIBABA_QWEN_API_KEY环境变量")
            raise
    
    def _convert_messages_to_prompt(self, messages: list) -> str:
        """将OpenAI格式的messages转换为阿里云格式的prompt"""
        prompt_parts = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"系统: {content}")
            elif role == 'user':
                prompt_parts.append(f"用户: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"助手: {content}")
        
        return "\n\n".join(prompt_parts)






class LLMClientFactory:
    """LLM客户端工厂类"""
    
    _clients: Dict[str, BaseLLMClient] = {}
    
    @classmethod
    def get_client(cls, provider: str = None) -> BaseLLMClient:
        """获取LLM客户端"""
        if provider is None:
            provider = settings.LLM_PROVIDER
        
        if provider not in cls._clients:
            if provider == "azure":
                cls._clients[provider] = AzureOpenAIClient()
            elif provider == "alibaba":
                cls._clients[provider] = AlibabaQwenClient()
            else:
                raise ValueError(f"不支持的LLM提供商: {provider}")
        else:
            pass  # 使用缓存的客户端
        
        return cls._clients[provider]
    
    @classmethod
    def clear_cache(cls):
        """清理客户端缓存"""
        cls._clients.clear()


# 全局LLM客户端实例
def get_llm_client(provider: str = None) -> BaseLLMClient:
    """获取LLM客户端实例"""
    return LLMClientFactory.get_client(provider)


# 全局客户端实例（保持向后兼容）
class LazyLLMClient:
    """延迟初始化的LLM客户端"""
    def __init__(self):
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            self._client = get_llm_client()
        return self._client
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        return await self._get_client().generate_text(prompt, **kwargs)
    
    async def generate_chat(self, messages: list, **kwargs) -> str:
        return await self._get_client().generate_chat(messages, **kwargs)

llm_client = LazyLLMClient()
