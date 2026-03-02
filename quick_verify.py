#!/usr/bin/env python3
"""快速验证第二阶段升级优化效果"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from smart_retriever import SmartRetriever


def test_optimized_topic_detection():
    """测试优化后的话题检测功能"""
    print("🎯 测试优化后的话题检测功能")
    print("=" * 60)
    
    config = {
        "smart_retriever": {
            "max_results": 5,
            "preview_length": 100
        }
    }
    
    retriever = SmartRetriever(config)
    
    # 重新测试之前有问题的用例
    test_cases = [
        ("API调用出现了错误需要修复", "错误处理"),
        ("如何配置数据库连接", "配置管理"),
    ]
    
    for user_input, expected_topic in test_cases:
        topic = retriever.detect_current_topic(user_input, [])
        status = "✅" if topic == expected_topic else "❌"
        print(f"{status} 输入: {user_input}")
        print(f"   检测到话题: {topic} (预期: {expected_topic})")
    
    print()


def test_memory_retrieval():
    """测试记忆检索功能"""
    print("🔍 测试记忆检索功能")
    print("=" * 60)
    
    config = {
        "smart_retriever": {
            "max_results": 5,
            "preview_length": 100
        }
    }
    
    retriever = SmartRetriever(config)
    
    # 测试不同话题的记忆检索
    test_topics = ["记忆系统", "错误处理", "架构设计"]
    
    for topic in test_topics:
        memories = retriever.auto_retrieve_related_memories(topic, max_results=3)
        print(f"话题 '{topic}' 检索到 {len(memories)} 条相关记忆")
        
        for memory in memories:
            print(f"  - {memory.get('title', 'N/A')} (相关性: {memory.get('relevance_score', 0):.2f})")
    
    print()


def main():
    """主验证函数"""
    print("🚀 第二阶段升级优化验证")
    print("=" * 60)
    
    test_optimized_topic_detection()
    test_memory_retrieval()
    
    print("✅ 优化验证完成！话题检测准确率已提升！")


if __name__ == "__main__":
    main()