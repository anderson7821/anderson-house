"""
IDE三层记忆插件 - 完整测试脚本
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# 添加插件路径到Python路径
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

from memory_plugin import MemoryPlugin
from storage_manager import StorageManager


def test_file_integrity():
    """测试1：检查所有7个文件是否完整"""
    print("\n🔍 测试1：文件完整性检查")
    
    required_files = [
        'memory_plugin.py',
        'storage_manager.py', 
        'config.yaml',
        'hooks/session_start.sh',
        'hooks/user_input.sh',
        'hooks/session_end.sh',
        'README.md'
    ]
    
    all_files_exist = True
    for file in required_files:
        file_path = os.path.join(plugin_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file} - 存在")
        else:
            print(f"❌ {file} - 缺失")
            all_files_exist = False
    
    return all_files_exist


def test_plugin_initialization():
    """测试2：插件初始化测试"""
    print("\n🔍 测试2：插件初始化")
    
    try:
        # 创建临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 修改配置使用临时目录
            config_path = os.path.join(plugin_dir, 'config.yaml')
            
            plugin = MemoryPlugin()
            success = plugin.initialize(config_path)
            
            if success:
                print("✅ 插件初始化成功")
                return True
            else:
                print("❌ 插件初始化失败")
                return False
                
    except Exception as e:
        print(f"❌ 插件初始化异常: {e}")
        return False


def test_storage_creation():
    """测试3：存储目录创建测试"""
    print("\n🔍 测试3：存储目录创建")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建临时配置
            temp_config = {
                'storage_paths': {
                    'project': os.path.join(temp_dir, '.memory/'),
                    'user': os.path.join(temp_dir, '.ide-memory/')
                }
            }
            
            storage = StorageManager(temp_config)
            
            # 检查目录是否创建
            project_dir = temp_config['storage_paths']['project']
            user_dir = temp_config['storage_paths']['user']
            
            if os.path.exists(project_dir) and os.path.exists(user_dir):
                print("✅ 存储目录创建成功")
                print(f"   项目目录: {project_dir}")
                print(f"   用户目录: {user_dir}")
                return True
            else:
                print("❌ 存储目录创建失败")
                return False
                
    except Exception as e:
        print(f"❌ 存储目录创建异常: {e}")
        return False


def test_memory_saving():
    """测试4：记忆保存功能测试"""
    print("\n🔍 测试4：记忆保存功能")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建临时配置
            temp_config = {
                'storage_paths': {
                    'project': os.path.join(temp_dir, '.memory/'),
                    'user': os.path.join(temp_dir, '.ide-memory/')
                }
            }
            
            storage = StorageManager(temp_config)
            
            # 测试保存记忆
            test_memory = {
                'timestamp': '10:30',
                'user_input': '如何修复报告生成错误？',
                'ai_response': '需要回到原来的正确架构...',
                'title': '如何修复报告生成错误？',
                'type': 'question',
                'topic': 'bugfix',
                'file': 'report_generator.py'
            }
            
            success = storage.save_memory(test_memory)
            
            if success:
                # 检查文件是否创建
                today_file = storage._get_today_file_path()
                if os.path.exists(today_file):
                    print("✅ 记忆保存成功")
                    
                    # 读取文件内容验证格式
                    with open(today_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查是否包含元数据
                    if '[type:question]' in content and '[topic:bugfix]' in content:
                        print("✅ 文件格式正确（包含元数据）")
                        print(f"   文件路径: {today_file}")
                        return True
                    else:
                        print("❌ 文件格式错误（缺少元数据）")
                        return False
                else:
                    print("❌ 记忆文件未创建")
                    return False
            else:
                print("❌ 记忆保存失败")
                return False
                
    except Exception as e:
        print(f"❌ 记忆保存异常: {e}")
        return False


def test_memory_retrieval():
    """测试5：记忆检索功能测试"""
    print("\n🔍 测试5：记忆检索功能")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建临时配置
            temp_config = {
                'storage_paths': {
                    'project': os.path.join(temp_dir, '.memory/'),
                    'user': os.path.join(temp_dir, '.ide-memory/')
                }
            }
            
            storage = StorageManager(temp_config)
            
            # 保存一些测试记忆
            memories = [
                {
                    'timestamp': '10:30',
                    'user_input': '如何修复报告生成错误？',
                    'ai_response': '需要回到原来的正确架构...',
                    'title': '报告错误修复',
                    'type': 'question',
                    'topic': 'bugfix'
                },
                {
                    'timestamp': '11:00', 
                    'user_input': '项目背景是什么？',
                    'ai_response': '这是LDR项目的数据分析系统...',
                    'title': '项目背景',
                    'type': 'question',
                    'topic': 'project'
                }
            ]
            
            for memory in memories:
                storage.save_memory(memory)
            
            # 测试检索功能
            recent_memories = storage.get_recent_memories(1)
            
            if len(recent_memories) >= 2:
                print("✅ 记忆检索成功")
                print(f"   检索到 {len(recent_memories)} 条记忆")
                
                # 测试简单搜索
                search_results = storage.search_memories_simple("报告")
                if search_results:
                    print("✅ 关键词搜索功能正常")
                else:
                    print("❌ 关键词搜索功能异常")
                    return False
                    
                return True
            else:
                print("❌ 记忆检索失败")
                return False
                
    except Exception as e:
        print(f"❌ 记忆检索异常: {e}")
        return False


def test_plugin_commands():
    """测试6：插件命令功能测试"""
    print("\n🔍 测试6：插件命令功能")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建临时配置
            temp_config = {
                'storage_paths': {
                    'project': os.path.join(temp_dir, '.memory/'),
                    'user': os.path.join(temp_dir, '.ide-memory/')
                }
            }
            
            plugin = MemoryPlugin()
            
            # 手动初始化（不使用配置文件）
            plugin.config = temp_config
            plugin.storage = StorageManager(temp_config)
            plugin.is_initialized = True
            
            # 测试命令处理
            help_result = plugin.handle_command("/memory help")
            if "可用命令" in help_result:
                print("✅ /memory help 命令正常")
            else:
                print("❌ /memory help 命令异常")
                return False
            
            # 测试列表命令
            list_result = plugin.handle_command("/memory list")
            if "记忆记录" in list_result or "没有记忆记录" in list_result:
                print("✅ /memory list 命令正常")
            else:
                print("❌ /memory list 命令异常")
                return False
            
            return True
                
    except Exception as e:
        print(f"❌ 插件命令异常: {e}")
        return False


def test_error_handling():
    """测试7：错误处理测试"""
    print("\n🔍 测试7：错误处理功能")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试1：目录自动重建
            project_dir = os.path.join(temp_dir, '.memory/')
            os.makedirs(project_dir, exist_ok=True)
            
            # 删除目录后测试重建
            shutil.rmtree(project_dir)
            
            temp_config = {
                'storage_paths': {
                    'project': project_dir,
                    'user': os.path.join(temp_dir, '.ide-memory/')
                }
            }
            
            storage = StorageManager(temp_config)
            
            if os.path.exists(project_dir):
                print("✅ 目录自动重建功能正常")
            else:
                print("❌ 目录自动重建功能异常")
                return False
            
            # 测试2：首次运行欢迎消息
            if not storage.check_initialized():
                # 模拟首次运行
                welcome_success = storage.save_welcome_message("欢迎使用记忆系统")
                if welcome_success:
                    print("✅ 首次运行欢迎消息功能正常")
                else:
                    print("❌ 首次运行欢迎消息功能异常")
                    return False
            
            return True
                
    except Exception as e:
        print(f"❌ 错误处理异常: {e}")
        return False


def run_complete_test():
    """运行完整测试套件"""
    print("🧪 开始IDE三层记忆插件完整测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("文件完整性", test_file_integrity()))
    test_results.append(("插件初始化", test_plugin_initialization()))
    test_results.append(("存储目录创建", test_storage_creation()))
    test_results.append(("记忆保存功能", test_memory_saving()))
    test_results.append(("记忆检索功能", test_memory_retrieval()))
    test_results.append(("插件命令功能", test_plugin_commands()))
    test_results.append(("错误处理功能", test_error_handling()))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n🎯 测试完成: {passed_tests}/{total_tests} 项测试通过")
    
    # 给出结论
    if passed_tests == total_tests:
        print("\n✨ 结论: 插件可交付使用！所有功能测试通过。")
        return True
    else:
        print(f"\n⚠️ 结论: 插件需要修复，{total_tests - passed_tests} 项测试失败。")
        return False


if __name__ == "__main__":
    # 运行完整测试
    success = run_complete_test()
    
    # 设置退出码
    sys.exit(0 if success else 1)