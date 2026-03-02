"""
IDE三层记忆系统 - 主插件类
基于OpenClaw三层记忆架构的轻量级实现
集成智能筛选器功能 + 防循环检测功能
"""

import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from storage_manager import StorageManager
from smart_filter import SmartFilter
from smart_retriever import SmartRetriever
from smart_compressor import SmartCompressor
from background_organizer import BackgroundOrganizer
from visualization_panel import VisualizationPanel
from anti_loop_detector import AntiLoopDetector


class MemoryPlugin:
    """记忆系统主插件"""
    
    def __init__(self):
        self.config = None
        self.storage = None
        self.smart_filter = None
        self.smart_retriever = None
        self.smart_compressor = None
        self.background_organizer = None
        self.visualization_panel = None
        self.anti_loop_detector = None  # 防循环检测器
        self.is_initialized = False
        self.conversation_buffer = []  # 对话缓冲区，用于摘要生成
        self.conversation_history = []  # 完整的对话历史，用于话题检测
        self.last_compression_check = None  # 上次压缩检查时间
        
    def initialize(self, config_path: Optional[str] = None) -> bool:
        """初始化插件"""
        try:
            # 加载配置
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = self._get_default_config()
            
            # 初始化存储管理器
            self.storage = StorageManager(self.config)
            
            # 初始化智能筛选器
            self.smart_filter = SmartFilter(self.config)
            
            # 初始化智能检索器
            self.smart_retriever = SmartRetriever(self.config)
            
            # 初始化智能压缩器
            self.smart_compressor = SmartCompressor(self.config)
            
            # 初始化后台整理器
            self.background_organizer = BackgroundOrganizer(self.config)
            
            # 初始化可视化面板
            self.visualization_panel = VisualizationPanel(self.config)
            
            # 初始化防循环检测器
            self.anti_loop_detector = AntiLoopDetector(
                max_conversation_history=10,
                similarity_threshold=0.8
            )
            
            # 首次运行检查
            if not self.storage.check_initialized():
                self._first_time_setup()
            
            self.is_initialized = True
            print("[MemoryPlugin] 记忆系统初始化完成（含智能筛选器、检索器、压缩器、后台整理器、可视化面板和防循环检测器）")
            return True
            
        except Exception as e:
            print(f"[MemoryPlugin] 初始化失败: {e}")
            return False
    

    
    def on_user_input(self, user_input: str, ai_response: str, 
                     metadata: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """用户输入钩子 - 智能记录对话 + 话题检测 + 防循环检测 + 后台整理"""
        if not self.is_initialized:
            return False, None
        
        try:
            # 更新后台整理器的活动时间
            if self.background_organizer:
                self.background_organizer.update_activity_time()
            
            # 防循环检测（在保存之前检测）
            loop_reminder = None
            if self.anti_loop_detector:
                # 添加当前对话轮次到检测器
                self.anti_loop_detector.add_conversation_turn(user_input, ai_response)
                
                # 检测是否重复建议
                loop_detection = self.anti_loop_detector.detect_loop(ai_response)
                if loop_detection and loop_detection['detected']:
                    loop_reminder = self.anti_loop_detector.generate_reminder_message(loop_detection)
                    print(f"[MemoryPlugin] 防循环检测到重复建议，相似度: {loop_detection['similarity']:.1%}")
            
            # 智能重要性分析（包含自动打标签和评分）
            importance_analysis = self.smart_filter.analyze_importance(user_input, ai_response)
            
            # 话题感知检测
            current_topic = self.smart_retriever.detect_current_topic(
                user_input, 
                self.conversation_history
            )
            
            # 构建记忆记录
            memory_record = {
                'timestamp': datetime.now().strftime('%H:%M'),
                'user_input': user_input,
                'ai_response': ai_response,
                'title': self._generate_title(user_input),
                'importance': importance_analysis["level"],  # L1/L2/L3
                'importance_score': importance_analysis["score"],  # 0-10分
                'tags': importance_analysis["tags"],  # [type:decision/bug/feature/question]
                'topic': current_topic,  # 检测到的话题
                'type': metadata.get('type', 'conversation') if metadata else 'conversation',
                'file': metadata.get('file', '') if metadata else ''
            }
            
            # 保存到当日文件
            success = self.storage.save_memory(memory_record)
            
            if success:
                print(f"[MemoryPlugin] 记忆已保存 ({importance_analysis['level']}): {memory_record['title']}")
                
                # 添加到对话缓冲区和历史
                self.conversation_buffer.append(memory_record)
                self.conversation_history.append(memory_record)
                
                # 每10轮自动生成摘要
                if len(self.conversation_buffer) >= 10:
                    self._auto_generate_summary()
            
            # 返回保存结果和防循环提醒
            return success, loop_reminder
            
        except Exception as e:
            print(f"[MemoryPlugin] 用户输入处理失败: {e}")
            return False, None
    
    def on_session_end(self) -> bool:
        """会话结束钩子 - 执行记忆压缩和清理"""
        if not self.is_initialized:
            return False
        
        try:
            # 简单的会话摘要（MVP阶段先记录，后续实现压缩）
            session_summary = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'type': 'session_summary',
                'title': '会话结束摘要',
                'user_input': '会话结束',
                'ai_response': '本次会话记忆已保存'
            }
            
            self.storage.save_memory(session_summary)
            print("[MemoryPlugin] 会话结束处理完成")
            return True
            
        except Exception as e:
            print(f"[MemoryPlugin] 会话结束处理失败: {e}")
            return False
    
    def _auto_generate_summary(self):
        """自动生成对话摘要（阶段三升级：智能压缩）"""
        try:
            if len(self.conversation_buffer) >= 10:
                # 使用智能压缩器生成更专业的摘要
                summary = self.smart_compressor.generate_conversation_summary(self.conversation_buffer)
                
                # 保存摘要到L2情景记忆
                summary_file = Path(f".memory/summaries/{datetime.now().strftime('%Y-%m-%d')}_summary.json")
                summary_file.parent.mkdir(exist_ok=True)
                
                import json
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                
                print(f"[MemoryPlugin] 智能摘要已生成: {summary_file}")
                print(f"   摘要内容: {summary.get('summary', '')[:100]}...")
                
                # 清空缓冲区（保留最后5条用于连续性）
                self.conversation_buffer = self.conversation_buffer[-5:]
                
        except Exception as e:
            print(f"[MemoryPlugin] 自动摘要生成失败: {e}")
    
    def trigger_sleep_organization(self):
        """触发睡眠整理机制"""
        if not self.is_initialized:
            return
        
        try:
            # 触发睡眠整理机制
            organization_report = self.smart_filter.sleep_organize_memories(older_than_days=30)
            
            print(f"[MemoryPlugin] 睡眠整理完成: {organization_report}")
            
        except Exception as e:
            print(f"[MemoryPlugin] 睡眠整理失败: {e}")
    
    def check_and_compress_old_memories(self):
        """检查并压缩旧记忆（阶段三升级：智能压缩）"""
        if not self.is_initialized:
            return
        
        try:
            # 检查是否需要压缩（每天只检查一次）
            now = datetime.now()
            if self.last_compression_check and (now - self.last_compression_check).days < 1:
                return
            
            self.last_compression_check = now
            
            # 检查存储空间
            space_report = self.smart_compressor.check_storage_space()
            
            print(f"[MemoryPlugin] 存储空间检查: {space_report['total_size_mb']}MB, 级别: {space_report['warning_level']}")
            
            # 根据空间级别决定压缩策略
            if space_report["warning_level"] in ["warning", "critical"]:
                print("[MemoryPlugin] 存储空间告警，开始压缩旧记忆...")
                
                # 压缩30天前的旧对话
                compression_report = self.smart_compressor.compress_old_conversations(older_than_days=30)
                
                print(f"[MemoryPlugin] 压缩完成: {compression_report['compressed_files']}个文件, "
                      f"节省空间: {compression_report['saved_space'] / 1024:.2f}MB")
                
                # 如果空间仍然紧张，合并相似记忆
                if space_report["warning_level"] == "critical":
                    print("[MemoryPlugin] 空间严重不足，开始合并相似记忆...")
                    
                    merge_report = self.smart_compressor.merge_similar_memories()
                    
                    print(f"[MemoryPlugin] 合并完成: {merge_report['merged_groups']}组, "
                          f"节省条目: {merge_report['saved_entries']}条")
            
            # 显示建议
            for recommendation in space_report.get("recommendations", []):
                print(f"💡 {recommendation}")
                
        except Exception as e:
            print(f"[MemoryPlugin] 压缩检查失败: {e}")
    
    def on_session_end(self):
        """会话结束钩子 - 触发压缩检查 + 启动后台整理"""
        if not self.is_initialized:
            return
        
        try:
            # 会话结束时检查是否需要压缩
            self.check_and_compress_old_memories()
            
            # 如果对话缓冲区有内容，生成最终摘要
            if self.conversation_buffer:
                self._auto_generate_summary()
            
            # 启动后台整理（睡眠中工作）
            if self.background_organizer:
                self.background_organizer.start_background_organization()
                print("[MemoryPlugin] 后台整理已启动（睡眠中工作模式）")
                
        except Exception as e:
            print(f"[MemoryPlugin] 会话结束处理失败: {e}")
    
    def on_session_start(self, current_topic: str = "") -> str:
        """会话开始钩子 - 话题感知自动检索 + 记忆预热 + 停止后台整理"""
        if not self.is_initialized:
            return ""
        
        try:
            # 停止后台整理（用户活动时停止）
            if self.background_organizer:
                self.background_organizer.stop_background_organization()
                print("[MemoryPlugin] 后台整理已停止（用户活动模式）")
            
            # 阶段二升级：话题感知自动检索
            if not current_topic:
                # 如果未指定话题，尝试从历史中检测
                if self.conversation_history:
                    # 分析最近对话的话题趋势
                    recent_inputs = [h.get('user_input', '') for h in self.conversation_history[-5:]]
                    if recent_inputs:
                        current_topic = self.smart_retriever.detect_current_topic(
                            ' '.join(recent_inputs), 
                            self.conversation_history
                        )
            
            # 记忆预热 - 新会话加载最相关的5条记忆
            warmup_memories = self.smart_retriever.session_warmup(current_topic)
            
            if warmup_memories:
                context = "# 🧠 智能记忆预热（话题感知检索）\n\n"
                
                # 检测到的当前话题
                if current_topic and current_topic != "general":
                    context += f"**检测到话题**: {current_topic}\n\n"
                
                # 应用渐进式披露
                preview_memories = self.smart_retriever.progressive_disclosure(warmup_memories)
                
                for i, memory in enumerate(preview_memories[:5], 1):
                    # 构建记忆条目
                    relevance_indicator = f" (相关性: {memory.get('relevance_score', 0):.2f})"
                    
                    context += f"## {i}. {memory['timestamp']} - {memory['title']}{relevance_indicator}\n"
                    
                    # 根据记忆类型显示不同内容
                    if memory.get('is_title_only'):
                        context += f"*远期记忆摘要*\n\n"
                    elif memory.get('is_preview'):
                        context += f"**用户**: {memory.get('user_input', '')}\n"
                        context += f"**AI**: {memory.get('ai_response', '')}\n\n"
                    else:
                        context += f"**用户**: {memory.get('user_input', '')}\n"
                        context += f"**AI**: {memory.get('ai_response', '')}\n\n"
                
                # 遗忘曲线优化提示
                context += "---\n"
                context += "*💡 记忆已按遗忘曲线优化：近期记忆显示全文，远期记忆显示摘要*\n"
                
                print(f"[MemoryPlugin] 已预热{len(warmup_memories)}条相关记忆到上下文")
                return context
            
            return ""
            
        except Exception as e:
            print(f"[MemoryPlugin] 会话开始处理失败: {e}")
            return ""
    
    def on_memory_recall(self, query: str, context: Dict) -> List[Dict]:
        """主动召回钩子 - AI可以主动查询记忆"""
        if not self.is_initialized:
            return []
        
        try:
            # 阶段二升级：话题感知自动检索
            current_topic = self.smart_retriever.detect_current_topic(
                query, 
                self.conversation_history
            )
            
            # 自动检索相关记忆
            related_memories = self.smart_retriever.auto_retrieve_related_memories(
                current_topic, 
                max_results=5
            )
            
            # 应用遗忘曲线优化
            optimized_memories = self.smart_retriever.optimize_with_forgetting_curve(
                related_memories
            )
            
            print(f"[MemoryPlugin] 主动召回{len(optimized_memories)}条相关记忆")
            return optimized_memories
            
        except Exception as e:
            print(f"[MemoryPlugin] 主动召回失败: {e}")
            return []
    
    def get_sidebar_content(self) -> Dict:
        """获取侧边栏内容 - 阶段五升级：可视化面板"""
        if not self.is_initialized or not self.visualization_panel:
            return {"error": "插件未初始化"}
        
        try:
            sidebar_content = self.visualization_panel.generate_sidebar_content()
            print("[MemoryPlugin] 侧边栏内容已生成")
            return sidebar_content
            
        except Exception as e:
            print(f"[MemoryPlugin] 侧边栏内容生成失败: {e}")
            return {"error": str(e)}
    
    def search_memories(self, query: str, filters: Optional[Dict] = None) -> Dict:
        """搜索记忆 - 阶段五升级：可视化搜索"""
        if not self.is_initialized or not self.visualization_panel:
            return {"error": "插件未初始化"}
        
        try:
            search_results = self.visualization_panel.search_memories(query, filters)
            print(f"[MemoryPlugin] 搜索完成: {search_results['total_count']}条结果")
            return search_results
            
        except Exception as e:
            print(f"[MemoryPlugin] 搜索失败: {e}")
            return {"error": str(e)}
    
    def get_graph_view(self, center_memory_id: Optional[str] = None) -> Dict:
        """获取图谱视图 - 阶段五升级：记忆关联网络"""
        if not self.is_initialized or not self.visualization_panel:
            return {"error": "插件未初始化"}
        
        try:
            graph_data = self.visualization_panel.generate_graph_view(center_memory_id)
            print(f"[MemoryPlugin] 图谱视图已生成: {len(graph_data['nodes'])}个节点")
            return graph_data
            
        except Exception as e:
            print(f"[MemoryPlugin] 图谱视图生成失败: {e}")
            return {"error": str(e)}
    
    def edit_memory(self, memory_id: str, updates: Dict) -> Dict:
        """编辑记忆 - 阶段五升级：手动编辑"""
        if not self.is_initialized or not self.visualization_panel:
            return {"error": "插件未初始化"}
        
        try:
            edit_result = self.visualization_panel.edit_memory(memory_id, updates)
            print(f"[MemoryPlugin] 记忆编辑完成: {memory_id}")
            return edit_result
            
        except Exception as e:
            print(f"[MemoryPlugin] 记忆编辑失败: {e}")
            return {"error": str(e)}
    
    def delete_memory(self, memory_id: str) -> Dict:
        """删除记忆 - 阶段五升级：手动删除"""
        if not self.is_initialized or not self.visualization_panel:
            return {"error": "插件未初始化"}
        
        try:
            delete_result = self.visualization_panel.delete_memory(memory_id)
            print(f"[MemoryPlugin] 记忆删除完成: {memory_id}")
            return delete_result
            
        except Exception as e:
            print(f"[MemoryPlugin] 记忆删除失败: {e}")
            return {"error": str(e)}
    
    def handle_command(self, command: str, args: List[str] = None) -> str:
        """处理记忆相关命令"""
        if not self.is_initialized:
            return "记忆系统未初始化"
        
        try:
            if command == "/memory" or command == "/memory list":
                return self._handle_list_command(args)
            elif command == "/memory stats":
                return self._handle_stats_command()
            elif command == "/memory help":
                return self._handle_help_command()
            else:
                return "未知命令，使用 /memory help 查看帮助"
                
        except Exception as e:
            return f"命令处理失败: {e}"
    
    def _handle_list_command(self, args: List[str]) -> str:
        """处理列表命令"""
        days = 1
        if args and len(args) > 0 and args[0].isdigit():
            days = min(int(args[0]), 7)  # 最多显示7天
        
        memories = self.storage.get_recent_memories(days)
        
        if not memories:
            return f"最近{days}天内没有记忆记录"
        
        result = f"# 最近{days}天记忆记录\n\n"
        
        current_date = ""
        for memory in memories:
            memory_date = memory['timestamp'][:10] if len(memory['timestamp']) > 10 else memory['timestamp']
            
            if memory_date != current_date:
                result += f"## {memory_date}\n"
                current_date = memory_date
            
            result += f"- **{memory['timestamp']}** - {memory['title']} [type:{memory['type']}]\n"
        
        return result
    
    def _handle_stats_command(self) -> str:
        """处理统计命令"""
        stats = self.storage.get_memory_stats()
        
        return f"""# 记忆系统统计

📊 **存储统计**
- 项目记忆目录: {stats['project_path']}
- 用户记忆目录: {stats['user_path']}
- 总记忆数量: {stats['total_memories']}
- 最近7天记忆: {stats['recent_7_days']}

📅 **文件统计**
- 记忆文件数量: {stats['memory_files']}
- 最早记忆日期: {stats['earliest_date']}
- 最新记忆日期: {stats['latest_date']}
"""
    
    def _handle_help_command(self) -> str:
        """处理帮助命令"""
        return """# 记忆系统帮助

## 可用命令
- `/memory list [天数]` - 显示最近记忆（默认1天）
- `/memory stats` - 显示统计信息
- `/memory help` - 显示此帮助

## 自动功能
- ✅ 会话自动记录
- ✅ 会话开始自动注入最近记忆
- ✅ 支持主动记忆召回

## 存储位置
- 项目记忆: `.memory/` 目录
- 用户配置: `~/.ide-memory/` 目录
"""
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'storage_paths': {
                'project': '.memory/',
                'user': '~/.ide-memory/'
            },
            'auto_injection': True,
            'retention_days': 7,
            'max_memories_per_day': 100
        }
    
    def _generate_title(self, user_input: str) -> str:
        """根据用户输入生成记忆标题"""
        # 简单的标题生成逻辑
        if len(user_input) <= 30:
            return user_input
        
        # 提取关键词或生成摘要
        words = user_input.split()
        if len(words) > 5:
            return ' '.join(words[:5]) + '...'
        else:
            return user_input[:30] + '...'
    
    def _first_time_setup(self) -> None:
        """首次运行设置"""
        print("[MemoryPlugin] 首次运行，进行初始化设置...")
        
        # 创建欢迎文件
        welcome_content = """# 欢迎使用IDE记忆系统 🧠

## 系统已就绪
您的对话将自动记录在此文件中，新的会话会自动加载相关记忆。

## 使用方法
- 正常对话即可，系统会自动记录
- 新会话会自动注入最近记忆
- 使用 `/memory list` 查看记录
- 使用 `/memory help` 获取帮助

## 存储说明
- 项目记忆保存在 `.memory/` 目录
- 用户配置保存在 `~/.ide-memory/` 目录
- 所有记忆均为纯文本，可手动编辑

💡 **提示**: 记忆系统会帮助AI更好地理解您的项目背景和需求！
"""
        
        self.storage.save_welcome_message(welcome_content)
        print("[MemoryPlugin] 首次运行设置完成")