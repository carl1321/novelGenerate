"""
日志工具函数
"""
import logging
from typing import Any


def truncate_log_message(message: str, max_length: int = 200) -> str:
    """
    截断日志消息，超过指定长度则添加省略号
    
    Args:
        message: 原始消息
        max_length: 最大长度，默认200
    
    Returns:
        截断后的消息
    """
    if not isinstance(message, str):
        message = str(message)
    
    if len(message) <= max_length:
        return message
    
    return message[:max_length] + "..."


def debug_log(message: str, data: Any = None, max_length: int = 200):
    """
    输出调试日志，自动截断长消息
    
    Args:
        message: 日志消息
        data: 可选的数据对象
        max_length: 最大长度，默认200
    """
    if data is not None:
        data_str = str(data)
        truncated_data = truncate_log_message(data_str, max_length)
        print(f"[DEBUG] {message}: {truncated_data}")
    else:
        truncated_message = truncate_log_message(message, max_length)
        print(f"[DEBUG] {truncated_message}")


def error_log(message: str, error: Exception = None, max_length: int = 200):
    """
    输出错误日志，自动截断长消息
    
    Args:
        message: 错误消息
        error: 可选的异常对象
        max_length: 最大长度，默认200
    """
    if error is not None:
        error_str = str(error)
        truncated_error = truncate_log_message(error_str, max_length)
        print(f"[ERROR] {message}: {truncated_error}")
    else:
        truncated_message = truncate_log_message(message, max_length)
        print(f"[ERROR] {truncated_message}")


def info_log(message: str, data: Any = None, max_length: int = 200):
    """
    输出信息日志，自动截断长消息
    
    Args:
        message: 日志消息
        data: 可选的数据对象
        max_length: 最大长度，默认200
    """
    if data is not None:
        data_str = str(data)
        truncated_data = truncate_log_message(data_str, max_length)
        print(f"[INFO] {message}: {truncated_data}")
    else:
        truncated_message = truncate_log_message(message, max_length)
        print(f"[INFO] {truncated_message}")
