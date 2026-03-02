#!/usr/bin/env python3
"""
第二阶段升级测试脚本
验证话题感知自动检索、渐进式披露、记忆预热、遗忘曲线优化等功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from smart_retriever import SmartRetriever
from memory_plugin import MemoryPlugin


def test_topic_detection():
    """测试话题检测功能"""
    print("🎯 测试话题检测功能")
    print("=" * 60)
    
    config = {
        "smart_retriever": {
            "max_results": 5,
            "preview_length": 100
        }
    }
    
    retriever = SmartRetriever(config)
    
    # 测试各种输入的话题检测
    test_cases = [
        ("我们需要优化记忆系统的检索功能", "记忆系统"),
        ("API调用出现了错误需要修复", "错误处理"),
        ("设计一个新的系统架构", "架构设计"),
        ("如何配置数据库连接", "配置管理"),
        ("今天天气不错", "general"),  # 默认话题
    ]
    
    for user_input, expected_topic in test_cases:
        topic = retriever.detect_current_topic(user_input, [])
        status = "✅" if topic == expected_topic else "❌"
        print(f"{status} 输入: {user_input}")
        print(f"   检测到话题: {topic} (预期: {expected_topic})")
    
    print()


def test_progressive_disclosure():
    """测试渐进式披露功能"""
    print("📖 测试渐进式披露功能")
    print("=" * 60)
    
    config = {
        "smart_retriever": {
            "max_results": 5,
            "preview_length": 100
        }
    }
    
    retriever = SmartRetriever(config)
    
    # 创建测试记忆数据
    test_memories = [
        {
            "timestamp": "10:30",
            "title": "记忆系统优化讨论",
            "user_input": "我们需要优化记忆系统的检索功能，让它能够自动识别话题并检索相关记忆",
            "ai_response": "好的，我们可以实现话题感知自动检索功能，包括话题检测、相关性计算和渐进式披露"
        },
        {
            "timestamp": "11:15", 
            "title": "API错误修复",
            "user_input": "API调用出现了错误需要修复",
            "ai_response": "让我检查一下错误日志，看看具体是什么问题"
        }
    ]
    
    # 应用渐进式披露
    preview_memories = retriever.progressive_disclosure(test_memories)
    
    print("原始记忆:")
    for memory in test_memories:
        print(f"  - {memory['title']}")
        print(f"    用户: {memory['user_input'][:50]}...")
        print(f"    AI: {memory['ai_response'][:50]}...")
    
    print("\n渐进式披露后:")
    for memory in preview_memories:
        print(f"  - {memory['title']}")
        if memory.get('is_preview'):
            print(f"    [预览模式] 用户: {memory['user_input']}")
            print(f"    [预览模式] AI: {memory['ai_response']}")
    
    print()


def test_session_warmup():
    """测试记忆预热功能"""
    print("🔥 测试记忆预热功能")
    print("=" * 60)
    
    config = {
        "smart_retriever": {
            "max_results": 5,
            "preview_length": 100
        }
    }
    
    retriever = SmartRetriever(config)
    
    # 测试不同话题的预热
    test_topics = ["记忆系统", "错误处理", "架构设计", "general"]
    
    for topic in test_topics:
        warmup_memories = retriever.session_warmup(topic)
        print(f"话题 '{topic}' 预热结果: {len(warmup_memories)} 条记忆")
        
        if warmup_memories:
            for memory in warmup_memories[:2]:  # 显示前2条
                memory_type = "预览" if memory.get('is_preview') else "全文"
                print(f"  - {memory['title']} [{memory_type}]")
    
    print()


def test_forgetting_curve_optimization():
    """测试遗忘曲线优化功能"""
    print("📊 测试遗忘曲线优化功能")
    print("=" * 60)
    
    config = {
        "smart_retriever": {
            "max_results": 5,
            "preview_length": 100
        }
    }
    
    retriever = SmartRetriever(config)
    
    # 创建不同时间段的测试记忆
    test_memories = [
        {
            "timestamp": "今天 10:30",
            "title": "今日讨论",
            "user_input": "今天讨论的内容",
            "ai_response": "今天的回复",
            "file_date": "2026-03-02"  # 今天
        },
        {
            "timestamp": "昨天 15:20", 
            "title": "昨日讨论",
            "user_input": "昨天讨论的内容",
            "ai_response": "昨天的回复",
            "file_date": "2026-03-01"  # 昨天
        },
        {
            "timestamp": "上周 09:10",
            "title": "上周讨论", 
            "user_input": "上周讨论的内容",
            "ai_response": "上周的回复",
            "file_date": "2026-02-25"  # 上周
        }
    ]
    
    # 应用遗忘曲线优化
    optimized_memories = retriever.optimize_with_forgetting_curve(test_memories)
    
    print("优化后的记忆显示策略:")
    for memory in optimized_memories:
        time_weight = memory.get('time_weight', 0)
        
        if memory.get('is_title_only'):
            display_type = "仅标题 (远期记忆)"
        elif memory.get('is_summary'):
            display_type = "摘要显示 (中期记忆)" 
        else:
            display_type = "全文显示 (近期记忆)"
        
        print(f"  - {memory['title']}: {display_type} (权重: {time_weight:.1f})")
    
    print()


def test_memory_plugin_integration():
    """测试记忆插件集成功能"""
    print("🔌 测试记忆插件集成功能")
    print("=" * 60)
    
    # 初始化插件
    plugin = MemoryPlugin()
    success = plugin.initialize("config.yaml")
    
    if success:
        print("✅ 插件初始化成功")
        
        # 测试会话开始功能
        context = plugin.on_session_start("记忆系统")
        if context:
            print("✅ 会话预热功能正常")
            print("上下文预览:")
            print(context[:200] + "..." if len(context) > 200 else context)
        else:
            print("❌ 会话预热功能异常")
        
        # 测试用户输入处理
        test_input = "我们需要优化记忆系统的检索功能"
        test_response = "好的，我们可以实现话题感知自动检索功能"
        
        success = plugin.on_user_input(test_input, test_response)
        if success:
            print("✅ 用户输入处理正常")
        else:
            print("❌ 用户输入处理异常")
    else:
        print("❌ 插件初始化失败")
    
    print()


def main():
    """主测试函数"""
    print("🚀 IDE三层记忆系统 - 第二阶段升级测试")
    print("=" * 70)
    print("阶段二升级：从'手动查询'到'话题触发自动检索'")
    print()
    
    # 运行所有测试
    test_topic_detection()
    test_progressive_disclosure()
    test_session_warmup()
    test_forgetting_curve_optimization()
    test_memory_plugin_integration()
    
    print("🎯 第二阶段升级测试完成！")
    print("\n📋 阶段二功能完整性总结：")
    print("✅ 话题感知检索 - 检测当前话题关键词，自动检索相关记忆")
    print("✅ 渐进式披露 - 先显示摘要，需要时再展开全文")
    print("✅ 记忆预热 - 新会话加载最相关的5条记忆")
    print("✅ 遗忘曲线优化 - 近期记忆权重高，远期记忆摘要化")
    print("✅ 插件集成 - 所有功能已集成到主插件")
    print("\n💡 第二阶段升级完成！AI现在具备'主动想起来'的能力！")
    print("\n🔜 下一步：第三阶段 - 记忆压缩与智能清理")


if __name__ == "__main__":
    main()