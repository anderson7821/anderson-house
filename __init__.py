"""
IDE三层记忆系统插件
基于OpenClaw三层记忆架构的轻量级实现
"""

__version__ = "1.0.0"
__author__ = "IDE Memory System Team"
__description__ = "轻量级三层记忆系统插件，为IDE提供智能记忆能力"

from .memory_plugin import MemoryPlugin

# 导出主要类和函数
__all__ = ['MemoryPlugin']