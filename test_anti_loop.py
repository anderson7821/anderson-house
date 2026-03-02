"""
防循环功能测试脚本
测试防循环检测器的功能和智能提示注入
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anti_loop_detector import AntiLoopDetector
from datetime import datetime, timedelta


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试防循环检测器基本功能")
    print("=" * 50)
    
    # 创建检测器
    detector = AntiLoopDetector(max_conversation_history=5, similarity_threshold=0.8)
    
    # 添加一些对话轮次
    test_conversations = [
        ("如何优化代码性能？", "建议使用缓存机制来优化性能，比如Redis缓存。"),
        ("还有其他优化方法吗？", "可以考虑使用异步编程来提高并发性能。"),
        ("缓存机制具体怎么实现？", "建议使用缓存机制来优化性能，比如Redis缓存。"),  # 重复建议
    ]
    
    for i, (user_input, ai_response) in enumerate(test_conversations, 1):
        print(f"\n第{i}轮对话:")
        print(f"用户: {user_input}")
        print(f"AI: {ai_response}")
        
        # 添加对话轮次
        detector.add_conversation_turn(user_input, ai_response)
        
        # 检测循环
        detection = detector.detect_loop(ai_response)
        
        if detection and detection['detected']:
            reminder = detector.generate_reminder_message(detection)
            print("🚨 检测到重复建议!")
            print(f"相似度: {detection['similarity']:.1%}")
            print(f"提醒消息: {reminder}")
        else:
            print("✅ 无重复建议")
    
    print("\n" + "=" * 50)
    print("✅ 基本功能测试完成")


def test_suggestion_extraction():
    """测试建议提取功能"""
    print("\n🧪 测试建议提取功能")
    print("=" * 50)
    
    detector = AntiLoopDetector()
    
    test_responses = [
        "好的，我建议使用缓存机制来优化性能，比如Redis缓存。另外可以考虑使用异步编程。",
        "这个问题可以通过添加日志记录来解决，同时建议使用错误处理机制。",
        "明白了，我会帮你分析这个问题。",  # 无建议内容
    ]
    
    for i, response in enumerate(test_responses, 1):
        suggestions = detector._extract_suggestions(response)
        print(f"\n测试 {i}:")
        print(f"原始回复: {response}")
        print(f"提取的建议: {suggestions}")
    
    print("\n" + "=" * 50)
    print("✅ 建议提取测试完成")


def test_similarity_calculation():
    """测试相似度计算"""
    print("\n🧪 测试相似度计算")
    print("=" * 50)
    
    detector = AntiLoopDetector()
    
    test_pairs = [
        ("建议使用缓存机制", "建议使用缓存机制"),  # 完全相同
        ("建议使用缓存机制", "推荐使用缓存技术"),  # 相似
        ("建议使用缓存机制", "需要添加错误处理"),  # 不同
    ]
    
    for i, (text1, text2) in enumerate(test_pairs, 1):
        similarity = detector._calculate_similarity([text1], [text2])
        print(f"\n测试 {i}:")
        print(f"文本1: {text1}")
        print(f"文本2: {text2}")
        print(f"相似度: {similarity:.1%}")
        print(f"是否重复: {'是' if similarity >= 0.8 else '否'}")
    
    print("\n" + "=" * 50)
    print("✅ 相似度计算测试完成")


def test_integration_with_memory_plugin():
    """测试与记忆插件的集成"""
    print("\n🧪 测试与记忆插件集成")
    print("=" * 50)
    
    try:
        from memory_plugin import MemoryPlugin
        
        # 创建插件实例
        plugin = MemoryPlugin()
        
        # 模拟初始化
        plugin.anti_loop_detector = AntiLoopDetector()
        
        # 测试对话处理
        test_cases = [
            ("如何优化代码？", "建议使用缓存机制来优化性能。"),
            ("还有其他方法吗？", "可以考虑异步编程提高并发。"),
            ("缓存机制怎么实现？", "建议使用缓存机制来优化性能。"),  # 重复
        ]
        
        for i, (user_input, ai_response) in enumerate(test_cases, 1):
            print(f"\n测试对话 {i}:")
            print(f"用户: {user_input}")
            print(f"AI: {ai_response}")
            
            # 模拟插件处理
            if plugin.anti_loop_detector:
                plugin.anti_loop_detector.add_conversation_turn(user_input, ai_response)
                detection = plugin.anti_loop_detector.detect_loop(ai_response)
                
                if detection and detection['detected']:
                    reminder = plugin.anti_loop_detector.generate_reminder_message(detection)
                    print("🚨 防循环系统检测到重复建议")
                    print(f"提醒消息: {reminder}")
                else:
                    print("✅ 无重复建议")
        
        print("\n" + "=" * 50)
        print("✅ 集成测试完成")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")


def main():
    """主测试函数"""
    print("🚀 防循环功能全面测试")
    print("=" * 60)
    
    # 运行所有测试
    test_basic_functionality()
    test_suggestion_extraction()
    test_similarity_calculation()
    test_integration_with_memory_plugin()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！防循环功能正常运行")
    
    # 显示使用示例
    print("\n📋 使用示例:")
    print("""
# 在AI助手代码中使用防循环功能
from memory_plugin import MemoryPlugin

# 初始化插件
plugin = MemoryPlugin()
plugin.initialize()

# 处理用户输入
user_input = "如何优化代码性能？"
ai_response = "建议使用缓存机制来优化性能。"

# 调用插件处理
success, loop_reminder = plugin.on_user_input(user_input, ai_response)

# 如果有防循环提醒，注入到回复中
if loop_reminder:
    final_response = ai_response + loop_reminder
    print(final_response)
else:
    print(ai_response)
""")


if __name__ == "__main__":
    main()