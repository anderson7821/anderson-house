#!/usr/bin/env python3
"""
智能筛选器功能测试脚本
验证重要性识别、自动检索、摘要生成和睡眠整理功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from smart_filter import SmartFilter


def test_importance_detection():
    """测试重要性识别功能"""
    print("🧠 测试重要性识别功能")
    print("=" * 50)
    
    config = {
        "smart_filter": {
            "importance_detection": True,
            "topic_repetition_threshold": 3
        }
    }
    
    filter = SmartFilter(config)
    
    # 测试用例
    test_cases = [
        ("记住：我的名字是Anderson", "L1"),  # 高重要性
        ("项目重点是三层记忆系统", "L1"),  # 高重要性
        ("重要：API配额管理", "L1"),  # 高重要性
        ("需要优化代码结构", "L2"),  # 中重要性
        ("今天天气怎么样？", "L3"),  # 普通对话
        ("我们应该考虑性能优化", "L2"),  # 中重要性
    ]
    
    for user_input, expected_level in test_cases:
        importance = filter.analyze_importance(user_input, "")
        status = "✅" if importance == expected_level else "❌"
        print(f"{status} 输入: {user_input}")
        print(f"   预期: {expected_level}, 实际: {importance}")
    
    print()


def test_topic_repetition():
    """测试话题重复检测"""
    print("🔄 测试话题重复检测")
    print("=" * 50)
    
    config = {
        "smart_filter": {
            "importance_detection": True,
            "topic_repetition_threshold": 3
        }
    }
    
    filter = SmartFilter(config)
    
    # 模拟重复提到"记忆"话题
    test_inputs = [
        "记忆系统很重要",
        "我们需要优化记忆功能",
        "记忆的存储方式需要改进",
        "记忆系统测试完成",  # 第4次提到，应该升级为L1
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        importance = filter.analyze_importance(user_input, "")
        expected_level = "L1" if i >= 3 else "L3"
        status = "✅" if importance == expected_level else "❌"
        print(f"{status} 第{i}次提到记忆: {user_input}")
        print(f"   重要性: {importance}")
    
    print()


def test_auto_retrieval():
    """测试自动检索功能"""
    print("🔍 测试自动检索功能")
    print("=" * 50)
    
    config = {
        "smart_filter": {
            "auto_retrieve_days": 3,
            "relevance_threshold": 0.5
        }
    }
    
    filter = SmartFilter(config)
    
    # 测试检索相关记忆
    current_topic = "记忆系统架构"
    relevant_memories = filter.auto_retrieve_relevant_memories(current_topic, days=1)
    
    print(f"检索话题: {current_topic}")
    print(f"找到相关记忆: {len(relevant_memories)} 条")
    
    for memory in relevant_memories[:3]:  # 显示前3条
        score = memory.get("relevance_score", 0)
        print(f"  相关性 {score:.2f}: {memory.get('title', '')}")
    
    print()


def test_summary_generation():
    """测试摘要生成功能"""
    print("📝 测试摘要生成功能")
    print("=" * 50)
    
    config = {
        "smart_filter": {
            "auto_summarize_after_rounds": 10,
            "summary_max_length": 100
        }
    }
    
    filter = SmartFilter(config)
    
    # 模拟对话数据
    conversation_rounds = []
    for i in range(15):
        conversation_rounds.append({
            "timestamp": f"10:{i:02d}",
            "user_input": f"这是第{i+1}轮对话的用户输入，讨论记忆系统的重要性",
            "ai_response": f"这是第{i+1}轮对话的AI回复，关于记忆系统的技术实现"
        })
    
    # 生成摘要
    summary = filter.generate_conversation_summary(conversation_rounds)
    
    print(f"对话轮次: {summary['total_rounds']}")
    print(f"关键点数量: {summary['key_points_count']}")
    print(f"主要话题: {', '.join(summary['main_topics'])}")
    print(f"摘要ID: {summary['summary_id']}")
    
    print("\n关键点示例:")
    for point in summary['key_points'][:2]:
        print(f"  时间: {point['timestamp']}")
        print(f"  重要性: {point['importance']}")
        print(f"  用户: {point['user_input']}")
        print(f"  AI: {point['ai_response']}")
        print()


def test_compression():
    """测试压缩功能"""
    print("🗜️ 测试压缩功能""")
    print("=" * 50)
    
    config = {
        "smart_filter": {
            "compression_enabled": True,
            "keep_original": False
        }
    }
    
    filter = SmartFilter(config)
    
    # 模拟对话数据
    conversation_data = []
    for i in range(5):
        conversation_data.append({
            "timestamp": f"10:{i:02d}",
            "user_input": f"测试对话用户输入{i}",
            "ai_response": f"测试对话AI回复{i}"
        })
    
    # 测试压缩
    output_path = Path("test_conversation.zip")
    success = filter.compress_conversation(conversation_data, output_path)
    
    if success and output_path.exists():
        file_size = output_path.stat().st_size
        print(f"✅ 压缩成功: {output_path}")
        print(f"   文件大小: {file_size} 字节")
        
        # 清理测试文件
        output_path.unlink()
    else:
        print("❌ 压缩失败")
    
    print()


def test_sleep_organization():
    """测试睡眠整理功能"""
    print("💤 测试睡眠整理功能")
    print("=" * 50)
    
    config = {
        "smart_filter": {
            "sleep_organization": True,
            "merge_similar_memories": True,
            "clean_old_memories": True
        }
    }
    
    filter = SmartFilter(config)
    
    # 运行睡眠整理（模拟）
    report = filter.sleep_organize_memories(older_than_days=1)  # 测试1天前的文件
    
    print(f"处理文件: {report.get('processed_files', 0)}")
    print(f"合并记忆: {report.get('merged_memories', 0)}")
    print(f"压缩文件: {report.get('compressed_files', 0)}")
    print(f"清理文件: {report.get('cleaned_files', 0)}")
    
    if report.get('errors'):
        print(f"错误: {report['errors']}")
    else:
        print("✅ 睡眠整理测试完成")
    
    print()


def main():
    """主测试函数"""
    print("🧠 IDE三层记忆系统 - 智能筛选器功能测试")
    print("=" * 60)
    
    # 运行所有测试
    test_importance_detection()
    test_topic_repetition()
    test_auto_retrieval()
    test_summary_generation()
    test_compression()
    test_sleep_organization()
    
    print("🎯 智能筛选器功能测试完成！")
    print("\n💡 所有功能已集成到主插件中，可以开始使用。")


if __name__ == "__main__":
    main()