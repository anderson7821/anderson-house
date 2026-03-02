"""
存储管理器 - 负责记忆数据的存储和检索
"""

import os
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import glob


class StorageManager:
    """存储管理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.project_path = self._expand_path(config['storage_paths']['project'])
        self.user_path = self._expand_path(config['storage_paths']['user'])
        
        # 确保目录存在
        self._ensure_directories()
    
    def check_initialized(self) -> bool:
        """检查是否已经初始化"""
        # 检查项目记忆目录是否存在且有内容
        if not os.path.exists(self.project_path):
            return False
        
        # 检查是否有记忆文件
        memory_files = glob.glob(os.path.join(self.project_path, "*.md"))
        return len(memory_files) > 0
    
    def save_memory(self, memory_record: Dict) -> bool:
        """保存记忆记录"""
        try:
            # 获取当日文件路径
            today_file = self._get_today_file_path()
            
            # 构建Markdown格式的记忆记录
            memory_content = self._format_memory_record(memory_record)
            
            # 追加到文件
            with open(today_file, 'a', encoding='utf-8') as f:
                f.write(memory_content)
                f.write('\n')  # 添加空行分隔
            
            return True
            
        except Exception as e:
            print(f"[StorageManager] 保存记忆失败: {e}")
            return False
    
    def get_recent_memories(self, days: int = 1) -> List[Dict]:
        """获取最近N天的记忆"""
        memories = []
        
        try:
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                file_path = os.path.join(self.project_path, f"{date_str}.md")
                
                if os.path.exists(file_path):
                    day_memories = self._parse_memory_file(file_path, date_str)
                    memories.extend(day_memories)
            
            # 按时间倒序排列
            memories.sort(key=lambda x: x.get('sort_key', ''), reverse=True)
            
        except Exception as e:
            print(f"[StorageManager] 获取最近记忆失败: {e}")
        
        return memories
    
    def search_memories_simple(self, query: str) -> List[Dict]:
        """简单关键词搜索记忆"""
        # MVP阶段：简单的文件内容搜索
        memories = []
        
        try:
            # 搜索最近3天的文件
            recent_memories = self.get_recent_memories(3)
            
            for memory in recent_memories:
                # 简单的关键词匹配
                if (query.lower() in memory.get('user_input', '').lower() or
                    query.lower() in memory.get('ai_response', '').lower() or
                    query.lower() in memory.get('title', '').lower()):
                    memories.append(memory)
            
        except Exception as e:
            print(f"[StorageManager] 搜索记忆失败: {e}")
        
        return memories
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计信息"""
        stats = {
            'project_path': self.project_path,
            'user_path': self.user_path,
            'total_memories': 0,
            'recent_7_days': 0,
            'memory_files': 0,
            'earliest_date': '无',
            'latest_date': '无'
        }
        
        try:
            # 获取所有记忆文件
            memory_files = glob.glob(os.path.join(self.project_path, "*.md"))
            stats['memory_files'] = len(memory_files)
            
            if memory_files:
                # 按文件名排序
                memory_files.sort()
                
                # 最早和最晚日期
                stats['earliest_date'] = Path(memory_files[0]).stem
                stats['latest_date'] = Path(memory_files[-1]).stem
                
                # 统计记忆数量
                total_count = 0
                recent_count = 0
                
                seven_days_ago = datetime.now() - timedelta(days=7)
                
                for file_path in memory_files:
                    file_date_str = Path(file_path).stem
                    
                    try:
                        file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                        
                        # 读取文件统计记忆数量
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 简单的记忆计数（基于标题行）
                            memory_count = content.count('## ')
                            total_count += memory_count
                            
                            if file_date >= seven_days_ago:
                                recent_count += memory_count
                                
                    except ValueError:
                        continue
                
                stats['total_memories'] = total_count
                stats['recent_7_days'] = recent_count
                
        except Exception as e:
            print(f"[StorageManager] 获取统计信息失败: {e}")
        
        return stats
    
    def save_welcome_message(self, content: str) -> bool:
        """保存欢迎消息"""
        try:
            welcome_file = os.path.join(self.project_path, "WELCOME.md")
            
            with open(welcome_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"[StorageManager] 保存欢迎消息失败: {e}")
            return False
    
    def _expand_path(self, path: str) -> str:
        """扩展路径（处理~等特殊字符）"""
        if path.startswith('~/'):
            return os.path.expanduser(path)
        return os.path.abspath(path)
    
    def _ensure_directories(self) -> None:
        """确保存储目录存在"""
        os.makedirs(self.project_path, exist_ok=True)
        os.makedirs(self.user_path, exist_ok=True)
    
    def _get_today_file_path(self) -> str:
        """获取当日文件路径"""
        today_str = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.project_path, f"{today_str}.md")
    
    def _format_memory_record(self, record: Dict) -> str:
        """格式化记忆记录为Markdown（支持自动打标签和评分）"""
        # 构建元数据标签
        metadata_parts = []
        
        # 基础标签
        if record.get('type'):
            metadata_parts.append(f"type:{record['type']}")
        if record.get('topic'):
            metadata_parts.append(f"topic:{record['topic']}")
        if record.get('file'):
            metadata_parts.append(f"file:{record['file']}")
        
        # 智能标签（自动打标签）
        if record.get('tags'):
            metadata_parts.extend(record['tags'])
        
        # 重要性评分
        if record.get('importance_score') is not None:
            metadata_parts.append(f"score:{record['importance_score']}")
        
        metadata = ' '.join([f"[{part}]" for part in metadata_parts])
        
        # 构建重要性指示器
        importance_indicator = ""
        if record.get('importance'):
            importance_emoji = {
                "L1": "🔴",  # 长期记忆 - 红色
                "L2": "🟡",  # 情景记忆 - 黄色
                "L3": "🔵"   # 会话记忆 - 蓝色
            }
            importance_indicator = importance_emoji.get(record['importance'], "⚪")
        
        content = f"""## {record['timestamp']} - {record['title']} {importance_indicator} {metadata}

**用户**: {record['user_input']}

**AI**: {record['ai_response']}
"""
        
        return content
    
    def _parse_memory_file(self, file_path: str, date_str: str) -> List[Dict]:
        """解析记忆文件"""
        memories = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按记忆块分割（基于##标题）
            memory_blocks = content.split('## ')[1:]  # 跳过第一个空块
            
            for block in memory_blocks:
                memory = self._parse_memory_block(block, date_str)
                if memory:
                    memories.append(memory)
                    
        except Exception as e:
            print(f"[StorageManager] 解析记忆文件失败 {file_path}: {e}")
        
        return memories
    
    def _parse_memory_block(self, block: str, date_str: str) -> Optional[Dict]:
        """解析单个记忆块"""
        try:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                return None
            
            # 解析标题行
            title_line = lines[0]
            parts = title_line.split(' - ', 1)
            if len(parts) < 2:
                return None
            
            timestamp = parts[0].strip()
            title = parts[1].strip()
            
            # 解析元数据
            metadata = {}
            import re
            metadata_matches = re.findall(r'\[(\w+):([^\]]+)\]', title)
            for key, value in metadata_matches:
                metadata[key] = value
            
            # 清理标题（移除元数据）
            title = re.sub(r'\s*\[\w+:[^\]]+\]', '', title).strip()
            
            # 解析用户输入和AI响应
            user_input = ""
            ai_response = ""
            
            for i, line in enumerate(lines[1:], 1):
                if line.startswith('**用户**:'):
                    user_input = line.replace('**用户**:', '').strip()
                elif line.startswith('**AI**:'):
                    ai_response = line.replace('**AI**:', '').strip()
                elif line.strip() and not user_input:
                    # 处理多行用户输入
                    user_input = line.strip()
                elif line.strip() and user_input and not ai_response:
                    # 处理多行AI响应
                    ai_response = line.strip()
            
            # 构建完整的时间戳用于排序
            full_timestamp = f"{date_str} {timestamp}" if ':' in timestamp else date_str
            
            return {
                'timestamp': timestamp,
                'full_timestamp': full_timestamp,
                'sort_key': full_timestamp,
                'title': title,
                'user_input': user_input,
                'ai_response': ai_response,
                'type': metadata.get('type', 'conversation'),
                'topic': metadata.get('topic', 'general'),
                'file': metadata.get('file', '')
            }
            
        except Exception as e:
            print(f"[StorageManager] 解析记忆块失败: {e}")
            return None