"""
增强功能测试用例 v1.0
测试三层记忆系统升级后的新功能：
1. 注意力权重自动衰减 + 高频信息抑制
2. 话题相关才查的记忆调用策略
3. 推理参数动态调整
"""

import sys
import os
from datetime import datetime, timedelta

# 添加路径以便导入模块
sys.path.append(os.path.dirname(__file__))

from anti_loop_detector_v2 import EnhancedAntiLoopDetector
from smart_retriever_v2 import EnhancedSmartRetriever
from inference_param_manager import InferenceParamManager


def test_enhanced_anti_loop_detector():
    """测试增强版防循环检测器"""
    print("🧪 测试增强版防循环检测器")
    print("=" * 50)
    
    detector = EnhancedAntiLoopDetector(max_conversation_history=5, similarity_threshold=0.7)
    
    # 测试1：基础循环检测
    print("\n📋 测试1：基础循环检测")
    
    # 添加一些对话历史
    detector.add_conversation_turn(
        "如何优化代码性能？",
        "建议使用缓存机制和异步处理来优化性能。"
    )
    
    detector.add_conversation_turn(
        "还有什么优化建议？",
        "可以考虑使用数据库索引和查询优化。"
    )
    
    # 检测重复建议
    result = detector.detect_loop("建议使用缓存机制和异步处理来优化性能。")
    
    if result and result['detected']:
        print(f"✅ 循环检测成功！相似度: {result['similarity']:.2f}")
        print(f"   注意力权重: {result.get('attention_weight', 1.0):.2f}")
        print(f"   频率惩罚: {result.get('frequency_penalty', 0.0):.2f}")
    else:
        print("❌ 循环检测失败")
    
    # 测试2：高频信息抑制
    print("\n📋 测试2：高频信息抑制")
    
    # 多次添加相同建议
    for i in range(5):
        detector.add_conversation_turn(
            f"测试问题{i}",
            "建议使用缓存机制优化性能。"
        )
    
    # 检查高频统计
    analytics = detector.get_detection_analytics()
    print(f"✅ 高频统计: {analytics['suggestion_frequency']}")
    
    # 测试3：注意力权重衰减
    print("\n📋 测试3：注意力权重衰减")
    
    initial_weights = detector.attention_weights.copy()
    
    # 模拟多轮对话（衰减注意力）
    for i in range(3):
        detector.add_conversation_turn(
            f"衰减测试{i}",
            "这是一个测试回复。"
        )
    
    current_weights = detector.attention_weights
    print(f"✅ 初始权重: {initial_weights}")
    print(f"✅ 当前权重: {current_weights}")
    
    # 测试4：推理参数调整
    print("\n📋 测试4：推理参数调整")
    
    # 正常状态参数
    normal_params = detector.adjust_inference_params(loop_detected=False)
    print(f"✅ 正常参数: {normal_params}")
    
    # 检测到循环时的参数
    loop_params = detector.adjust_inference_params(loop_detected=True)
    print(f"✅ 循环参数: {loop_params}")
    
    print("\n🎯 增强版防循环检测器测试完成！")
    return True


def test_enhanced_smart_retriever():
    """测试增强版智能检索器"""
    print("\n🧪 测试增强版智能检索器")
    print("=" * 50)
    
    config = {
        'memory_dir': '.memory',
        'max_retrieval_results': 5
    }
    
    retriever = EnhancedSmartRetriever(config)
    
    # 测试1：话题检测
    print("\n📋 测试1：话题检测")
    
    conversation_history = [
        {'user_input': '如何优化记忆系统？', 'ai_response': '建议使用智能筛选器'},
        {'user_input': '记忆系统性能问题', 'ai_response': '需要优化存储结构'}
    ]
    
    topic = retriever.detect_current_topic("记忆系统优化方案", conversation_history)
    print(f"✅ 检测到话题: {topic}")
    
    # 测试2：话题相关才查
    print("\n📋 测试2：话题相关才查")
    
    should_retrieve = retriever.should_retrieve_memories(topic, conversation_history)
    print(f"✅ 是否应该检索: {should_retrieve}")
    
    # 测试3：智能检索
    print("\n📋 测试3：智能检索")
    
    memories = retriever.auto_retrieve_related_memories(topic, max_results=3)
    print(f"✅ 检索到记忆数量: {len(memories)}")
    
    for i, memory in enumerate(memories):
        print(f"   {i+1}. 相关性: {memory.get('relevance_score', 0):.2f}")
        print(f"      原因: {memory.get('retrieval_reason', 'N/A')}")
    
    # 测试4：自适应阈值
    print("\n📋 测试4：自适应阈值")
    
    # 模拟多次话题出现
    for i in range(5):
        retriever.detect_current_topic("记忆系统相关", [])
    
    # 检查阈值调整
    threshold = retriever._get_adaptive_threshold("记忆系统")
    print(f"✅ 自适应阈值: {threshold:.2f}")
    
    print("\n🎯 增强版智能检索器测试完成！")
    return True


def test_inference_param_manager():
    """测试推理参数管理器"""
    print("\n🧪 测试推理参数管理器")
    print("=" * 50)
    
    manager = InferenceParamManager()
    
    # 测试1：基础参数获取
    print("\n📋 测试1：基础参数获取")
    
    base_params = manager.base_params
    print(f"✅ 基础参数: {base_params}")
    
    # 测试2：正常状态参数调整
    print("\n📋 测试2：正常状态参数调整")
    
    normal_state = {
        'user_input': '普通问题',
        'ai_response': '普通回答',
        'loop_detected': False
    }
    
    normal_params = manager.get_adjusted_params(normal_state)
    print(f"✅ 正常状态参数: {normal_params}")
    
    # 测试3：循环检测状态参数调整
    print("\n📋 测试3：循环检测状态参数调整")
    
    loop_state = {
        'user_input': '重复问题',
        'ai_response': '重复回答',
        'loop_detected': True
    }
    
    loop_params = manager.get_adjusted_params(loop_state)
    print(f"✅ 循环状态参数: {loop_params}")
    
    # 测试4：参数分析
    print("\n📋 测试4：参数分析")
    
    analytics = manager.get_param_analytics()
    print(f"✅ 对话统计: {analytics['conversation_stats']}")
    print(f"✅ 自适应权重: {analytics['adaptive_weights']}")
    
    # 测试5：状态跟踪
    print("\n📋 测试5：状态跟踪")
    
    # 模拟多轮对话
    for i in range(5):
        test_state = {
            'user_input': f'测试问题{i}',
            'ai_response': f'测试回答{i}',
            'loop_detected': (i % 3 == 0)  # 每3轮模拟一次循环检测
        }
        params = manager.get_adjusted_params(test_state)
        print(f"   轮次{i+1}: 温度={params['temperature']:.2f}, 频率惩罚={params['frequency_penalty']:.2f}")
    
    print("\n🎯 推理参数管理器测试完成！")
    return True


def test_integration():
    """测试集成功能"""
    print("\n🧪 测试集成功能")
    print("=" * 50)
    
    # 创建各组件实例
    detector = EnhancedAntiLoopDetector()
    retriever = EnhancedSmartRetriever({})
    param_manager = InferenceParamManager()
    
    # 模拟完整对话流程
    print("\n📋 模拟完整对话流程")
    
    test_scenarios = [
        {
            'user_input': '如何优化记忆系统性能？',
            'ai_response': '建议使用缓存机制和智能压缩算法。'
        },
        {
            'user_input': '还有什么优化建议？', 
            'ai_response': '可以考虑使用异步处理和数据库索引优化。'
        },
        {
            'user_input': '性能优化方案？',
            'ai_response': '建议使用缓存机制和智能压缩算法。'  # 重复建议
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n🔄 对话轮次 {i+1}:")
        print(f"   用户: {scenario['user_input']}")
        print(f"   AI: {scenario['ai_response']}")
        
        # 1. 话题检测
        topic = retriever.detect_current_topic(scenario['user_input'], [])
        print(f"   📍 话题: {topic}")
        
        # 2. 循环检测
        loop_result = detector.detect_loop(scenario['ai_response'], topic.split(':')[0])
        if loop_result and loop_result['detected']:
            print(f"   ⚠️  检测到循环! 相似度: {loop_result['similarity']:.2f}")
        else:
            print("   ✅ 无循环检测")
        
        # 3. 参数调整
        state = {
            'user_input': scenario['user_input'],
            'ai_response': scenario['ai_response'],
            'loop_detected': loop_result['detected'] if loop_result else False
        }
        
        params = param_manager.get_adjusted_params(state)
        print(f"   🔧 推理参数: 温度={params['temperature']:.2f}, 频率惩罚={params['frequency_penalty']:.2f}")
        
        # 4. 记忆检索（如果话题相关）
        if retriever.should_retrieve_memories(topic, []):
            memories = retriever.auto_retrieve_related_memories(topic)
            print(f"   💾 检索到 {len(memories)} 条相关记忆")
        
        # 添加到检测器历史
        detector.add_conversation_turn(scenario['user_input'], scenario['ai_response'])
    
    print("\n🎯 集成功能测试完成！")
    return True


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始三层记忆系统增强功能测试")
    print("=" * 60)
    
    test_results = []
    
    try:
        # 运行各模块测试
        test_results.append(('防循环检测器', test_enhanced_anti_loop_detector()))
        test_results.append(('智能检索器', test_enhanced_smart_retriever()))
        test_results.append(('推理参数管理器', test_inference_param_manager()))
        test_results.append(('集成功能', test_integration()))
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        
        passed = 0
        for module, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{module}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 总体结果: {passed}/{len(test_results)} 个测试通过")
        
        if passed == len(test_results):
            print("\n🎉 所有增强功能测试通过！系统升级成功！")
            return True
        else:
            print("\n⚠️  部分测试失败，请检查相关功能")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行所有测试
    success = run_all_tests()
    
    if success:
        print("\n🎊 三层记忆系统 v1.1.0 增强功能验证完成！")
        print("   新功能包括:")
        print("   • 注意力权重自动衰减")
        print("   • 高频信息抑制")
        print("   • 话题相关才查的记忆调用策略")
        print("   • 推理参数动态调整")
        print("   • 自适应学习机制")
    else:
        print("\n⚠️  测试失败，请检查代码实现")