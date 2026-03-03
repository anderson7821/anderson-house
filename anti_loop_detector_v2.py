"""
增强版会话内防循环检测器 v2.0
新增功能：注意力权重自动衰减 + 高频信息抑制 + 智能话题过滤
"""

import re
import difflib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque, defaultdict
import math


class EnhancedAntiLoopDetector:
    """增强版防循环检测器"""
    
    def __init__(self, max_conversation_history: int = 10, similarity_threshold: float = 0.8):
        """
        初始化增强版防循环检测器
        
        Args:
            max_conversation_history: 最大对话历史记录数
            similarity_threshold: 相似度阈值（>80%视为重复）
        """
        self.max_conversation_history = max_conversation_history
        self.similarity_threshold = similarity_threshold
        self.conversation_history = deque(maxlen=max_conversation_history)
        self.last_detection_time = None
        self.detection_count = 0
        
        # 新增：高频信息统计
        self.suggestion_frequency = defaultdict(int)  # 建议内容出现次数统计
        self.topic_keywords = defaultdict(int)        # 话题关键词频率统计
        
        # 新增：注意力权重衰减参数
        self.attention_decay_rate = 0.1  # 注意力衰减率（每轮衰减10%）
        self.attention_weights = {}     # 各建议的注意力权重
        
        # 新增：推理参数调整
        self.inference_params = {
            'temperature': 0.7,          # 默认推理温度
            'top_p': 0.9,                # 核采样参数
            'frequency_penalty': 0.2,    # 频率惩罚
            'presence_penalty': 0.1      # 存在惩罚
        }
        
    def add_conversation_turn(self, user_input: str, ai_response: str, timestamp: datetime = None):
        """
        添加对话轮次（增强版：包含高频统计和注意力更新）
        
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
            'turn_id': len(self.conversation_history) + 1,
            'topic': self._extract_topic(user_input)  # 新增：话题提取
        }
        
        self.conversation_history.append(conversation_turn)
        
        # 新增：更新高频统计
        self._update_frequency_statistics(ai_response)
        
        # 新增：更新注意力权重衰减
        self._update_attention_weights()
        
    def detect_loop(self, current_ai_response: str, current_topic: str = None) -> Optional[Dict]:
        """
        检测当前回复是否与历史重复（增强版：包含话题过滤和注意力加权）
        
        Args:
            current_ai_response: 当前AI回复
            current_topic: 当前话题（可选）
            
        Returns:
            Optional[Dict]: 如果检测到重复，返回检测信息；否则返回None
        """
        if len(self.conversation_history) < 2:
            return None
            
        # 提取AI回复的核心建议部分
        current_suggestions = self._extract_suggestions(current_ai_response)
        if not current_suggestions:
            return None
            
        # 新增：应用高频抑制
        current_suggestions = self._apply_frequency_suppression(current_suggestions)
        
        # 检查最近的历史对话（增强：包含话题过滤）
        for i, past_turn in enumerate(reversed(self.conversation_history)):
            if i >= self.max_conversation_history - 1:  # 跳过当前轮次
                break
                
            # 新增：话题相关性过滤
            if current_topic and not self._is_topic_relevant(past_turn, current_topic):
                continue
                
            past_suggestions = self._extract_suggestions(past_turn['ai_response'])
            if not past_suggestions:
                continue
                
            # 计算相似度（增强：包含注意力权重）
            similarity = self._calculate_weighted_similarity(
                current_suggestions, past_suggestions, past_turn
            )
            
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
                    'detection_time': datetime.now(),
                    'attention_weight': self._get_attention_weight(past_suggestions),  # 新增
                    'frequency_penalty': self._get_frequency_penalty(past_suggestions)  # 新增
                }
                
        return None
        
    def _update_frequency_statistics(self, ai_response: str):
        """
        更新高频信息统计
        
        Args:
            ai_response: AI回复内容
        """
        suggestions = self._extract_suggestions(ai_response)
        for suggestion in suggestions:
            # 提取关键词进行统计
            keywords = self._extract_keywords(suggestion)
            for keyword in keywords:
                self.suggestion_frequency[keyword] += 1
                
    def _update_attention_weights(self):
        """更新注意力权重衰减"""
        # 对所有现有权重进行衰减
        for key in list(self.attention_weights.keys()):
            self.attention_weights[key] *= (1 - self.attention_decay_rate)
            
            # 如果权重过低，移除
            if self.attention_weights[key] < 0.01:
                del self.attention_weights[key]
                
    def _apply_frequency_suppression(self, suggestions: List[str]) -> List[str]:
        """
        应用高频信息抑制
        
        Args:
            suggestions: 原始建议列表
            
        Returns:
            List[str]: 抑制后的建议列表
        """
        suppressed_suggestions = []
        
        for suggestion in suggestions:
            keywords = self._extract_keywords(suggestion)
            max_frequency = max([self.suggestion_frequency.get(kw, 0) for kw in keywords], default=0)
            
            # 如果最高频次超过阈值，进行抑制
            if max_frequency <= 3:  # 允许出现3次以内
                suppressed_suggestions.append(suggestion)
                
        return suppressed_suggestions if suppressed_suggestions else suggestions
        
    def _calculate_weighted_similarity(self, current_suggestions: List[str], 
                                     past_suggestions: List[str], past_turn: Dict) -> float:
        """
        计算加权相似度（包含注意力权重和频率惩罚）
        
        Args:
            current_suggestions: 当前建议列表
            past_suggestions: 历史建议列表
            past_turn: 历史对话轮次
            
        Returns:
            float: 加权相似度
        """
        # 基础相似度计算
        base_similarity = self._calculate_similarity(current_suggestions, past_suggestions)
        
        # 应用注意力权重
        attention_weight = self._get_attention_weight(past_suggestions)
        
        # 应用频率惩罚
        frequency_penalty = self._get_frequency_penalty(past_suggestions)
        
        # 计算加权相似度
        weighted_similarity = base_similarity * attention_weight * (1 - frequency_penalty)
        
        return min(weighted_similarity, 1.0)  # 确保不超过1.0
        
    def _get_attention_weight(self, suggestions: List[str]) -> float:
        """
        获取注意力权重
        
        Args:
            suggestions: 建议列表
            
        Returns:
            float: 注意力权重（0.0-1.0）
        """
        suggestion_key = '|'.join(sorted(suggestions))
        
        if suggestion_key not in self.attention_weights:
            # 新建议，赋予高权重
            self.attention_weights[suggestion_key] = 1.0
            
        return self.attention_weights[suggestion_key]
        
    def _get_frequency_penalty(self, suggestions: List[str]) -> float:
        """
        获取频率惩罚
        
        Args:
            suggestions: 建议列表
            
        Returns:
            float: 频率惩罚（0.0-0.5）
        """
        keywords = []
        for suggestion in suggestions:
            keywords.extend(self._extract_keywords(suggestion))
            
        if not keywords:
            return 0.0
            
        # 计算平均频率
        avg_frequency = sum(self.suggestion_frequency.get(kw, 0) for kw in keywords) / len(keywords)
        
        # 应用对数惩罚（频率越高，惩罚越大）
        penalty = min(math.log(avg_frequency + 1) * 0.1, 0.5)
        
        return penalty
        
    def _is_topic_relevant(self, past_turn: Dict, current_topic: str) -> bool:
        """
        判断历史对话是否与当前话题相关
        
        Args:
            past_turn: 历史对话轮次
            current_topic: 当前话题
            
        Returns:
            bool: 是否相关
        """
        if not current_topic or current_topic == "general":
            return True
            
        past_topic = past_turn.get('topic', '')
        
        # 简单的话题匹配逻辑
        if current_topic in past_topic or past_topic in current_topic:
            return True
            
        # 提取关键词进行匹配
        current_keywords = set(self._extract_keywords(current_topic))
        past_keywords = set(self._extract_keywords(past_topic))
        
        # 如果有共同关键词，认为相关
        return len(current_keywords & past_keywords) > 0
        
    def _extract_topic(self, user_input: str) -> str:
        """
        从用户输入中提取话题
        
        Args:
            user_input: 用户输入
            
        Returns:
            str: 提取的话题
        """
        # 简单的关键词提取
        topic_keywords = [
            '优化', '性能', '缓存', '异步', '错误', '调试', '测试',
            '代码', '函数', '类', '模块', '数据库', 'API', '前端',
            '后端', '部署', '配置', '安全', '日志', '监控'
        ]
        
        for keyword in topic_keywords:
            if keyword in user_input:
                return keyword
                
        return "general"
        
    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 关键词列表
        """
        # 移除标点符号和常见词
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', ' ', text)
        words = cleaned.split()
        
        # 过滤常见词和短词
        stop_words = {'的', '了', '在', '是', '我', '你', '他', '她', '它', '这', '那', '有', '没有', '可以', '应该', '需要'}
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return keywords[:10]  # 返回前10个关键词
        
    def adjust_inference_params(self, loop_detected: bool = False) -> Dict:
        """
        根据循环检测结果调整推理参数
        
        Args:
            loop_detected: 是否检测到循环
            
        Returns:
            Dict: 调整后的推理参数
        """
        params = self.inference_params.copy()
        
        if loop_detected:
            # 检测到循环时，增加随机性和惩罚
            params['temperature'] = min(params['temperature'] + 0.2, 1.0)
            params['frequency_penalty'] = min(params['frequency_penalty'] + 0.1, 0.5)
            params['presence_penalty'] = min(params['presence_penalty'] + 0.1, 0.3)
        else:
            # 正常状态下，使用默认参数
            params = self.inference_params.copy()
            
        return params
        
    def get_detection_analytics(self) -> Dict:
        """
        获取检测分析数据
        
        Returns:
            Dict: 分析数据
        """
        return {
            'total_conversation_turns': len(self.conversation_history),
            'detection_count': self.detection_count,
            'suggestion_frequency': dict(self.suggestion_frequency),
            'attention_weights': self.attention_weights.copy(),
            'current_inference_params': self.inference_params.copy()
        }

    # 保留原有的基础方法（简化版）
    def _extract_suggestions(self, text: str) -> List[str]:
        """从文本中提取建议部分"""
        cleaned_text = self._clean_text(text)
        
        suggestion_patterns = [
            r'(?:建议|推荐|可以|应该|需要|考虑|尝试|使用|采用|实现|添加|优化|改进|修复|解决)[^。！？]*[。！？]',
            r'(?:建议|推荐|可以|应该|需要)[^，；]*[，；]',
        ]
        
        suggestions = []
        for pattern in suggestion_patterns:
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            suggestions.extend(matches)
            
        return suggestions if suggestions and len(cleaned_text) > 20 else []
        
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        greetings = ['好的', '明白了', '了解', '收到', '谢谢', '不客气', '你好', '您好']
        cleaned = text
        for greeting in greetings:
            cleaned = cleaned.replace(greeting, '')
        return re.sub(r'\s+', ' ', cleaned).strip()
        
    def _calculate_similarity(self, current_suggestions: List[str], past_suggestions: List[str]) -> float:
        """计算相似度"""
        if not current_suggestions or not past_suggestions:
            return 0.0
        current_text = ' '.join(current_suggestions)
        past_text = ' '.join(past_suggestions)
        return difflib.SequenceMatcher(None, current_text, past_text).ratio()
        
    def _calculate_time_diff(self, past_timestamp: datetime) -> str:
        """计算时间差"""
        diff = datetime.now() - past_timestamp
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}秒"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() // 60)}分钟"
        else:
            return f"{int(diff.total_seconds() // 3600)}小时"
            
    def _record_loop_detection_to_l2(self, current_suggestions: List[str], 
                                   past_suggestions: List[str], 
                                   similarity: float, time_diff: str):
        """记录到L2情景记忆"""
        self.detection_count += 1
        self.last_detection_time = datetime.now()