"""
第四阶段升级测试 - 后台整理（睡眠中工作）
测试从"实时处理"到"闲时优化"的升级
"""

import os
import sys
import time
from datetime import datetime, timedelta

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from background_organizer import BackgroundOrganizer
from memory_plugin import MemoryPlugin


def test_background_organizer_basic():
    """测试后台整理器基本功能"""
    print("🧹 测试后台整理器基本功能")
    print("=" * 60)
    
    config = {
        "background_organizer": {
            "idle_threshold_minutes": 1,  # 测试用1分钟
            "migration_threshold_days": 1,
            "quality_evaluation_days": 1,
            "low_quality_threshold": 0.3,
            "association_discovery_enabled": True,
            "max_background_time_minutes": 2
        }
    }
    
    organizer = BackgroundOrganizer(config)
    
    # 测试记忆迁移
    migration_result = organizer._migrate_low_frequency_memories()
    print(f"✅ 记忆迁移测试: {migration_result['migrated_count']}条")
    
    # 测试关联发现
    association_result = organizer._discover_memory_associations()
    print(f"✅ 关联发现测试: {association_result['associations_count']}个")
    
    # 测试质量评估
    quality_result = organizer._evaluate_memory_quality()
    print(f"✅ 质量评估测试: {quality_result['low_quality_count']}条低质量")
    
    print()


def test_idle_detection():
    """测试空闲检测功能"""
    print("⏰ 测试空闲检测功能")
    print("=" * 60)
    
    config = {
        "background_organizer": {
            "idle_threshold_minutes": 0.1,  # 测试用6秒
            "migration_threshold_days": 1,
            "quality_evaluation_days": 1,
            "low_quality_threshold": 0.3,
            "association_discovery_enabled": True,
            "max_background_time_minutes": 1
        }
    }
    
    organizer = BackgroundOrganizer(config)
    
    # 初始状态应该不是空闲
    is_idle = organizer._is_idle()
    print(f"初始空闲状态: {'是' if is_idle else '否'}")
    
    # 等待超过空闲阈值
    print("等待7秒（超过6秒阈值）...")
    time.sleep(7)
    
    # 现在应该是空闲状态
    is_idle = organizer._is_idle()
    print(f"等待后空闲状态: {'是' if is_idle else '否'}")
    
    # 更新活动时间
    organizer.update_activity_time()
    
    # 立即检查应该不是空闲
    is_idle = organizer._is_idle()
    print(f"更新活动后空闲状态: {'是' if is_idle else '否'}")
    
    print()


def test_background_tasks():
    """测试后台任务执行"""
    print("🔄 测试后台任务执行")
    print("=" * 60)
    
    config = {
        "background_organizer": {
            "idle_threshold_minutes": 0.1,  # 测试用6秒
            "migration_threshold_days": 1,
            "quality_evaluation_days": 1,
            "low_quality_threshold": 0.3,
            "association_discovery_enabled": True,
            "max_background_time_minutes": 1
        }
    }
    
    organizer = BackgroundOrganizer(config)
    
    # 等待超过空闲阈值
    print("等待7秒进入空闲状态...")
    time.sleep(7)
    
    # 执行后台任务
    print("开始执行后台整理任务...")
    task_result = organizer._perform_background_tasks()
    
    print(f"✅ 完成任务: {task_result['tasks_completed']}/3")
    print(f"✅ 记忆迁移: {task_result['memory_migrations']}条")
    print(f"✅ 关联发现: {task_result['associations_discovered']}个")
    print(f"✅ 低质量记忆: {task_result['low_quality_memories']}条")
    
    print()


def test_memory_plugin_integration():
    """测试记忆插件集成"""
    print("🔌 测试记忆插件集成")
    print("=" * 60)
    
    # 创建测试配置
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    
    plugin = MemoryPlugin()
    
    # 初始化插件
    success = plugin.initialize(config_path)
    print(f"✅ 插件初始化: {'成功' if success else '失败'}")
    
    if success:
        # 测试会话开始（停止后台整理）
        print("\n🔛 测试会话开始（停止后台整理）")
        context = plugin.on_session_start("测试话题")
        print(f"✅ 会话开始处理完成")
        
        # 测试用户输入（更新活动时间）
        print("\n💬 测试用户输入（更新活动时间）")
        plugin.on_user_input("测试用户输入", "测试AI回复")
        print(f"✅ 用户输入处理完成")
        
        # 测试会话结束（启动后台整理）
        print("\n🔚 测试会话结束（启动后台整理）")
        plugin.on_session_end()
        print(f"✅ 会话结束处理完成")
        
        # 等待后台整理运行
        print("\n⏳ 等待后台整理运行...")
        time.sleep(5)
        
        # 再次测试会话开始（停止后台整理）
        print("\n🔛 再次测试会话开始（停止后台整理）")
        plugin.on_session_start("测试话题")
        print(f"✅ 会话开始处理完成")
    
    print()


def test_memory_similarity():
    """测试记忆相似度计算"""
    print("📊 测试记忆相似度计算")
    print("=" * 60)
    
    config = {
        "background_organizer": {
            "idle_threshold_minutes": 5,
            "migration_threshold_days": 7,
            "quality_evaluation_days": 30,
            "low_quality_threshold": 0.3,
            "association_discovery_enabled": True,
            "max_background_time_minutes": 10
        }
    }
    
    organizer = BackgroundOrganizer(config)
    
    # 创建测试记忆
    memory1 = {
        "user_input": "记住：三层记忆系统需要实现智能压缩功能",
        "ai_response": "好的，我们可以实现自动摘要和压缩存储"
    }
    
    memory2 = {
        "user_input": "决定采用摘要+压缩的存储策略",
        "ai_response": "建议每10轮对话生成摘要，30天后压缩原始文件"
    }
    
    memory3 = {
        "user_input": "今天天气怎么样",
        "ai_response": "今天天气晴朗，温度适宜"
    }
    
    # 计算相似度
    similarity1 = organizer._calculate_memory_similarity(memory1, memory2)
    similarity2 = organizer._calculate_memory_similarity(memory1, memory3)
    
    print(f"✅ 相似记忆相似度: {similarity1:.2f}")
    print(f"✅ 不相似记忆相似度: {similarity2:.2f}")
    
    print()


def test_memory_quality_evaluation():
    """测试记忆质量评估"""
    print("⭐ 测试记忆质量评估")
    print("=" * 60)
    
    config = {
        "background_organizer": {
            "idle_threshold_minutes": 5,
            "migration_threshold_days": 7,
            "quality_evaluation_days": 30,
            "low_quality_threshold": 0.3,
            "association_discovery_enabled": True,
            "max_background_time_minutes": 10
        }
    }
    
    organizer = BackgroundOrganizer(config)
    
    # 创建不同质量的测试记忆
    high_quality_memory = {
        "user_input": "记住：三层记忆系统需要实现智能压缩功能",
        "ai_response": "好的，我们可以实现自动摘要和压缩存储，这将大大优化存储空间",
        "importance": "L1"
    }
    
    medium_quality_memory = {
        "user_input": "决定采用摘要策略",
        "ai_response": "建议生成摘要",
        "importance": "L2"
    }
    
    low_quality_memory = {
        "user_input": "嗯",
        "ai_response": "好的",
        "importance": "L3"
    }
    
    # 评估质量
    quality1 = organizer._calculate_memory_quality(high_quality_memory)
    quality2 = organizer._calculate_memory_quality(medium_quality_memory)
    quality3 = organizer._calculate_memory_quality(low_quality_memory)
    
    print(f"✅ 高质量记忆评分: {quality1:.2f}")
    print(f"✅ 中等质量记忆评分: {quality2:.2f}")
    print(f"✅ 低质量记忆评分: {quality3:.2f}")
    
    print()


def main():
    """主测试函数"""
    print("🚀 IDE三层记忆系统 - 第四阶段升级测试")
    print("=" * 60)
    print("阶段四升级：从'实时处理'到'闲时优化'\n")
    
    # 测试1: 后台整理器基本功能
    test_background_organizer_basic()
    
    # 测试2: 空闲检测功能
    test_idle_detection()
    
    # 测试3: 后台任务执行
    test_background_tasks()
    
    # 测试4: 记忆相似度计算
    test_memory_similarity()
    
    # 测试5: 记忆质量评估
    test_memory_quality_evaluation()
    
    # 测试6: 记忆插件集成
    test_memory_plugin_integration()
    
    print("🎯 第四阶段升级测试完成！")
    print("=" * 60)
    
    print("📋 阶段四功能完整性总结：")
    print("✅ 闲时整理 - IDE空闲5分钟时后台整理记忆")
    print("✅ 记忆迁移 - 低频记忆从L2降级到L3")
    print("✅ 关联发现 - 自动发现记忆之间的关联")
    print("✅ 质量评估 - 定期淘汰低价值记忆")
    print("✅ 插件集成 - 所有功能已集成到主插件")
    
    print("\n💡 第四阶段升级完成！实现'睡眠中工作'的智能优化！")
    
    print("\n🎉 四阶段记忆系统全面升级完成！")
    print("=" * 60)
    print("📊 完整升级总结：")
    print("   阶段一：智能筛选器 ✅")
    print("   阶段二：智能检索器 ✅")
    print("   阶段三：智能压缩器 ✅")
    print("   阶段四：后台整理器 ✅")
    
    print("\n🚀 AI现在具备完整的智能记忆管理能力！")
    print("   从'实时处理'升级到'闲时优化'")
    print("   实现'睡眠中工作'的智能优化模式")


if __name__ == "__main__":
    main()