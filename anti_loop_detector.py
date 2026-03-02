"""
会话内防循环检测器
实时监控对话，防止AI助手重复建议相同方案
"""

import re
import difflib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque


class AntiLoopDetector:
    """防循环检测器"""
    
    def __init__(self, max_conversation_history: int = 10, similarity_threshold: float = 0.8):
        """
        初始化防循环检测器
        
        Args:
            max_conversation_history: 最大对话历史记录数
            similarity_threshold: 相似度阈值（>80%视为重复）
        """
        self.max_conversation_history = max_conversation_history
        self.similarity_threshold = similarity_threshold
        self.conversation_history = deque(maxlen=max_conversation_history)
        self.last_detection_time = None
        self.detection_count = 0
        
    def add_conversation_turn(self, user_input: str, ai_response: str, timestamp: datetime = None):
        """
        添加对话轮次
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            timestamp: 时间戳
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        conversation_turn = {
            'user_input': user_input,
            'ai_response': ai_response,
            'timestamp': timestamp,
            'turn_id': len(self.conversation_history) + 1
        }
        
        self.conversation_history.append(conversation_turn)
        
    def detect_loop(self, current_ai_response: str) -> Optional[Dict]:
        """
        检测当前回复是否与历史重复
        
        Args:
            current_ai_response: 当前AI回复
            
        Returns:
            Optional[Dict]: 如果检测到重复，返回检测信息；否则返回None
        """
        if len(self.conversation_history) < 2:
            return None
            
        # 提取AI回复的核心建议部分
        current_suggestions = self._extract_suggestions(current_ai_response)
        if not current_suggestions:
            return None
            
        # 检查最近的历史对话
        for i, past_turn in enumerate(reversed(self.conversation_history)):
            if i >= self.max_conversation_history - 1:  # 跳过当前轮次
                break
                
            past_suggestions = self._extract_suggestions(past_turn['ai_response'])
            if not past_suggestions:
                continue
                
            # 计算相似度
            similarity = self._calculate_similarity(current_suggestions, past_suggestions)
            
            if similarity >= self.similarity_threshold:
                # 检测到重复
                time_diff = self._calculate_time_diff(past_turn['timestamp'])
                
                # 记录到L2情景记忆
                self._record_loop_detection_to_l2(
                    current_suggestions, past_suggestions, similarity, time_diff
                )
                
                return {
                    'detected': True,
                    'similarity': similarity,
                    'past_turn': past_turn,
                    'time_diff': time_diff,
                    'current_suggestions': current_suggestions,
                    'past_suggestions': past_suggestions,
                    'detection_time': datetime.now()
                }
                
        return None
        
    def _extract_suggestions(self, text: str) -> List[str]:
        """
        从文本中提取建议部分
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 提取的建议列表
        """
        # 移除常见的问候语和无关内容
        cleaned_text = self._clean_text(text)
        
        # 提取建议性语句（包含动词和行动指示）
        suggestions = []
        
        # 匹配建议模式
        suggestion_patterns = [
            r'(?:建议|推荐|可以|应该|需要|考虑|尝试|使用|采用|实现|添加|优化|改进|修复|解决)[^。！？]*[。！？]',
            r'(?:建议|推荐|可以|应该|需要)[^，；]*[，；]',
            r'[.!?]\s*(?:另外|此外|同时|还有)[^.!?]*[.!?]'
        ]
        
        for pattern in suggestion_patterns:
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            suggestions.extend(matches)
            
        # 如果没有匹配到模式，使用整个文本（但排除太短的内容）
        if not suggestions and len(cleaned_text) > 20:
            suggestions = [cleaned_text]
            
        return suggestions
        
    def _clean_text(self, text: str) -> str:
        """
        清理文本，移除无关内容
        
        Args:
            text: 输入文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除常见的问候语
        greetings = [
            '好的', '明白了', '了解', '收到', '谢谢', '不客气',
            '你好', '您好', '嗨', 'hello', 'hi'
        ]
        
        cleaned = text
        for greeting in greetings:
            cleaned = cleaned.replace(greeting, '')
            
        # 移除多余的空格和换行
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
        
    def _calculate_similarity(self, current_suggestions: List[str], past_suggestions: List[str]) -> float:
        """
        计算建议之间的相似度
        
        Args:
            current_suggestions: 当前建议列表
            past_suggestions: 历史建议列表
            
        Returns:
            float: 相似度分数（0-1）
        """
        if not current_suggestions or not past_suggestions:
            return 0.0
            
        # 将建议列表合并为单个字符串进行比较
        current_text = ' '.join(current_suggestions)
        past_text = ' '.join(past_suggestions)
        
        # 使用difflib计算相似度
        similarity = difflib.SequenceMatcher(None, current_text, past_text).ratio()
        
        return similarity
        
    def _calculate_time_diff(self, past_timestamp: datetime) -> str:
        """
        计算时间差，返回友好的时间描述
        
        Args:
            past_timestamp: 过去的时间戳
            
        Returns:
            str: 时间差描述
        """
        now = datetime.now()
        diff = now - past_timestamp
        
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}秒"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() // 60)}分钟"
        else:
            return f"{int(diff.total_seconds() // 3600)}小时"
            
    def generate_reminder_message(self, detection_info: Dict) -> str:
        """
        生成提醒消息
        
        Args:
            detection_info: 检测信息
            
        Returns:
            str: 提醒消息
        """
        time_diff = detection_info['time_diff']
        similarity = detection_info['similarity']
        
        # 提取关键建议内容
        past_suggestions = detection_info['past_suggestions']
        key_suggestion = past_suggestions[0] if past_suggestions else "这个方案"
        
        # 限制建议内容长度
        if len(key_suggestion) > 50:
            key_suggestion = key_suggestion[:47] + "..."
            
        # 根据相似度调整提醒强度
        if similarity > 0.9:
            strength = "强烈"
        elif similarity > 0.8:
            strength = "明显"
        else:
            strength = "可能"
            
        reminder_message = f"\n\n💡 **防循环提醒**: {strength}检测到重复建议！\n"
        reminder_message += f"注意：你{time_diff}前已经建议过『{key_suggestion}』\n"
        reminder_message += f"相似度：{similarity:.1%} | 需要换思路吗？\n"
        reminder_message += "---\n"
        
        return reminder_message
        
    def get_detection_stats(self) -> Dict:
        """
        获取检测统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'total_conversation_turns': len(self.conversation_history),
            'detection_count': self.detection_count,
            'last_detection_time': self.last_detection_time,
            'similarity_threshold': self.similarity_threshold
        }
        
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history.clear()
        self.detection_count = 0
        self.last_detection_time = None
        
    def _record_loop_detection_to_l2(self, current_suggestions: List[str], 
                                   past_suggestions: List[str], 
                                   similarity: float, time_diff: str):
        """
        将防循环检测结果记录到L2情景记忆
        
        Args:
            current_suggestions: 当前建议列表
            past_suggestions: 历史建议列表
            similarity: 相似度
            time_diff: 时间差描述
        """
        try:
            # 构建L2记忆记录
            loop_detection_record = {
                'type': 'loop_detection',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'similarity': similarity,
                'time_diff': time_diff,
                'current_suggestions': current_suggestions,
                'past_suggestions': past_suggestions,
                'detection_count': self.detection_count + 1,
                'severity': self._calculate_severity(similarity)
            }
            
            # 保存到L2情景记忆文件
            self._save_to_l2_memory(loop_detection_record)
            
            # 更新检测统计
            self.detection_count += 1
            self.last_detection_time = datetime.now()
            
        except Exception as e:
            print(f"[AntiLoopDetector] L2记忆记录失败: {e}")
            
    def _calculate_severity(self, similarity: float) -> str:
        """
        根据相似度计算严重程度
        
        Args:
            similarity: 相似度分数
            
        Returns:
            str: 严重程度（low/medium/high）
        """
        if similarity >= 0.9:
            return "high"
        elif similarity >= 0.8:
            return "medium"
        else:
            return "low"
            
    def _save_to_l2_memory(self, record: Dict):
        """
        保存到L2情景记忆文件
        
        Args:
            record: 记忆记录
        """
        try:
            import json
            from pathlib import Path
            
            # 创建L2记忆目录
            l2_dir = Path(".memory/l2_loop_detections")
            l2_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"loop_detection_{timestamp}.json"
            filepath = l2_dir / filename
            
            # 保存记录
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
                
            print(f"[AntiLoopDetector] 防循环检测已记录到L2记忆: {filepath}")
            
        except Exception as e:
            print(f"[AntiLoopDetector] L2记忆保存失败: {e}")
            
    def get_loop_analysis_report(self) -> Dict:
        """
        获取防循环分析报告
        
        Returns:
            Dict: 分析报告
        """
        try:
            import json
            from pathlib import Path
            
            l2_dir = Path(".memory/l2_loop_detections")
            if not l2_dir.exists():
                return {"total_detections": 0, "recent_detections": []}
                
            # 读取所有检测记录
            detection_files = list(l2_dir.glob("loop_detection_*.json"))
            
            # 分析最近7天的检测记录
            recent_detections = []
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            for filepath in detection_files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        record = json.load(f)
                        
                    # 检查时间
                    record_time = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if record_time >= seven_days_ago:
                        recent_detections.append(record)
                        
                except Exception as e:
                    print(f"[AntiLoopDetector] 读取检测记录失败 {filepath}: {e}")
                    
            # 生成分析报告
            report = {
                "total_detections": len(detection_files),
                "recent_detections_count": len(recent_detections),
                "recent_detections": recent_detections[:10],  # 最多显示10条
                "detection_stats": self.get_detection_stats()
            }
            
            return report
            
        except Exception as e:
            print(f"[AntiLoopDetector] 分析报告生成失败: {e}")
            return {"error": str(e)}