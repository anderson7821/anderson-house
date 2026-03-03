"""
推理参数管理器 v1.0
动态调整AI推理参数，防止重复和提升多样性
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
import math


class InferenceParamManager:
    """推理参数管理器"""
    
    def __init__(self):
        # 基础推理参数配置
        self.base_params = {
            'temperature': 0.7,          # 温度：控制随机性（0.0-1.0）
            'top_p': 0.9,                # 核采样：控制多样性（0.0-1.0）
            'frequency_penalty': 0.2,    # 频率惩罚：抑制重复词（0.0-2.0）
            'presence_penalty': 0.1,     # 存在惩罚：抑制已出现词（0.0-2.0）
            'max_tokens': 2048,          # 最大输出长度
            'stop': None                 # 停止词
        }
        
        # 参数调整策略
        self.adjustment_strategies = {
            'loop_detected': {
                'temperature': 0.3,      # 检测到循环时增加温度
                'frequency_penalty': 0.2, # 增加频率惩罚
                'presence_penalty': 0.1,  # 增加存在惩罚
                'top_p': 0.1             # 稍微降低top_p
            },
            'high_repetition': {
                'temperature': 0.4,      # 高重复率时大幅增加温度
                'frequency_penalty': 0.3, # 大幅增加频率惩罚
                'presence_penalty': 0.2, # 大幅增加存在惩罚
                'top_p': 0.2             # 降低top_p增加多样性
            },
            'low_diversity': {
                'temperature': 0.2,      # 低多样性时增加温度
                'top_p': 0.2,            # 降低top_p
                'frequency_penalty': 0.1 # 轻微增加频率惩罚
            },
            'normal': {
                'temperature': 0.0,      # 正常状态微调
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0,
                'top_p': 0.0
            }
        }
        
        # 状态跟踪
        self.conversation_history = deque(maxlen=20)
        self.loop_detection_history = deque(maxlen=10)
        self.repetition_stats = defaultdict(int)
        self.diversity_scores = deque(maxlen=10)
        
        # 自适应学习参数
        self.learning_rate = 0.1  # 学习率
        self.adaptive_weights = {
            'temperature': 1.0,
            'frequency_penalty': 1.0,
            'presence_penalty': 1.0
        }
        
    def get_adjusted_params(self, current_state: Dict) -> Dict:
        """
        获取调整后的推理参数
        
        Args:
            current_state: 当前状态信息
            
        Returns:
            Dict: 调整后的推理参数
        """
        # 分析当前状态
        state_analysis = self._analyze_current_state(current_state)
        
        # 确定调整策略
        strategy = self._determine_adjustment_strategy(state_analysis)
        
        # 应用策略调整
        adjusted_params = self._apply_strategy_adjustment(strategy, state_analysis)
        
        # 更新状态跟踪
        self._update_state_tracking(current_state, state_analysis)
        
        return adjusted_params
        
    def _analyze_current_state(self, current_state: Dict) -> Dict:
        """
        分析当前状态
        
        Args:
            current_state: 当前状态信息
            
        Returns:
            Dict: 状态分析结果
        """
        analysis = {
            'loop_detected': current_state.get('loop_detected', False),
            'repetition_rate': self._calculate_repetition_rate(),
            'diversity_score': self._calculate_diversity_score(),
            'conversation_length': len(self.conversation_history),
            'recent_loop_count': self._count_recent_loops(),
            'topic_consistency': self._calculate_topic_consistency()
        }
        
        return analysis
        
    def _determine_adjustment_strategy(self, analysis: Dict) -> str:
        """
        确定调整策略
        
        Args:
            analysis: 状态分析结果
            
        Returns:
            str: 策略名称
        """
        # 检测到循环
        if analysis['loop_detected']:
            return 'loop_detected'
            
        # 高重复率
        if analysis['repetition_rate'] > 0.3:
            return 'high_repetition'
            
        # 低多样性
        if analysis['diversity_score'] < 0.3:
            return 'low_diversity'
            
        # 近期循环频繁
        if analysis['recent_loop_count'] > 2:
            return 'high_repetition'
            
        return 'normal'
        
    def _apply_strategy_adjustment(self, strategy: str, analysis: Dict) -> Dict:
        """
        应用策略调整
        
        Args:
            strategy: 策略名称
            analysis: 状态分析结果
            
        Returns:
            Dict: 调整后的参数
        """
        # 获取基础参数
        params = self.base_params.copy()
        
        # 获取策略调整量
        strategy_adjustment = self.adjustment_strategies.get(strategy, self.adjustment_strategies['normal'])
        
        # 应用调整（考虑自适应权重）
        for param_name, adjustment in strategy_adjustment.items():
            if param_name in params:
                # 计算加权调整量
                weighted_adjustment = adjustment * self.adaptive_weights.get(param_name, 1.0)
                
                # 应用调整（限制在合理范围内）
                if param_name == 'temperature':
                    params[param_name] = min(max(params[param_name] + weighted_adjustment, 0.1), 1.0)
                elif param_name in ['frequency_penalty', 'presence_penalty']:
                    params[param_name] = min(max(params[param_name] + weighted_adjustment, 0.0), 2.0)
                elif param_name == 'top_p':
                    params[param_name] = min(max(params[param_name] - weighted_adjustment, 0.1), 1.0)
                    
        # 根据分析结果进行微调
        params = self._apply_fine_tuning(params, analysis)
        
        return params
        
    def _apply_fine_tuning(self, params: Dict, analysis: Dict) -> Dict:
        """
        应用精细调整
        
        Args:
            params: 当前参数
            analysis: 状态分析
            
        Returns:
            Dict: 精细调整后的参数
        """
        # 根据对话长度调整温度
        if analysis['conversation_length'] > 10:
            # 长对话增加多样性
            params['temperature'] = min(params['temperature'] + 0.1, 1.0)
            
        # 根据话题一致性调整惩罚
        if analysis['topic_consistency'] > 0.8:
            # 话题一致时增加惩罚防止重复
            params['frequency_penalty'] = min(params['frequency_penalty'] + 0.1, 2.0)
            
        return params
        
    def _calculate_repetition_rate(self) -> float:
        """计算重复率"""
        if len(self.conversation_history) < 2:
            return 0.0
            
        # 分析最近对话的重复程度
        recent_responses = [turn.get('ai_response', '') for turn in list(self.conversation_history)[-5:]]
        
        if len(recent_responses) < 2:
            return 0.0
            
        # 计算相似度矩阵
        total_similarity = 0.0
        comparison_count = 0
        
        for i in range(len(recent_responses)):
            for j in range(i + 1, len(recent_responses)):
                similarity = self._calculate_text_similarity(recent_responses[i], recent_responses[j])
                total_similarity += similarity
                comparison_count += 1
                
        return total_similarity / comparison_count if comparison_count > 0 else 0.0
        
    def _calculate_diversity_score(self) -> float:
        """计算多样性得分"""
        if len(self.conversation_history) < 2:
            return 1.0  # 初始对话多样性最高
            
        # 分析词汇多样性
        recent_texts = [turn.get('ai_response', '') for turn in list(self.conversation_history)[-5:]]
        
        if not recent_texts:
            return 1.0
            
        # 提取所有词汇
        all_words = []
        for text in recent_texts:
            words = self._extract_words(text)
            all_words.extend(words)
            
        if not all_words:
            return 1.0
            
        # 计算词汇多样性（唯一词比例）
        unique_words = set(all_words)
        diversity = len(unique_words) / len(all_words)
        
        return min(diversity, 1.0)
        
    def _count_recent_loops(self) -> int:
        """统计近期循环次数"""
        return sum(1 for detection in self.loop_detection_history 
                  if detection.get('detected', False))
        
    def _calculate_topic_consistency(self) -> float:
        """计算话题一致性"""
        if len(self.conversation_history) < 2:
            return 0.0
            
        # 提取最近对话的话题关键词
        recent_topics = []
        for turn in list(self.conversation_history)[-5:]:
            topic = self._extract_topic(turn.get('user_input', ''))
            if topic:
                recent_topics.append(topic)
                
        if len(recent_topics) < 2:
            return 0.0
            
        # 计算话题一致性（相同话题比例）
        if len(set(recent_topics)) == 1:
            return 1.0  # 所有话题相同
        else:
            # 计算主要话题的比例
            topic_counts = {}
            for topic in recent_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
            max_count = max(topic_counts.values())
            return max_count / len(recent_topics)
            
    def _update_state_tracking(self, current_state: Dict, analysis: Dict):
        """更新状态跟踪"""
        # 添加当前对话轮次
        if 'user_input' in current_state and 'ai_response' in current_state:
            self.conversation_history.append({
                'user_input': current_state['user_input'],
                'ai_response': current_state['ai_response'],
                'timestamp': datetime.now()
            })
            
        # 添加循环检测记录
        if analysis['loop_detected']:
            self.loop_detection_history.append({
                'detected': True,
                'timestamp': datetime.now(),
                'analysis': analysis
            })
            
        # 更新自适应权重
        self._update_adaptive_weights(analysis)
        
    def _update_adaptive_weights(self, analysis: Dict):
        """更新自适应权重"""
        # 根据效果调整权重
        if analysis['loop_detected']:
            # 检测到循环，增加惩罚权重
            self.adaptive_weights['frequency_penalty'] = min(
                self.adaptive_weights['frequency_penalty'] + self.learning_rate, 2.0
            )
            self.adaptive_weights['presence_penalty'] = min(
                self.adaptive_weights['presence_penalty'] + self.learning_rate, 2.0
            )
        
        if analysis['diversity_score'] < 0.3:
            # 多样性低，增加温度权重
            self.adaptive_weights['temperature'] = min(
                self.adaptive_weights['temperature'] + self.learning_rate, 2.0
            )
            
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if not text1 or not text2:
            return 0.0
            
        # 简单的相似度计算（可替换为更复杂的算法）
        words1 = set(self._extract_words(text1))
        words2 = set(self._extract_words(text2))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
        
    def _extract_words(self, text: str) -> List[str]:
        """从文本中提取词汇"""
        # 简单的分词（中文按字符，英文按单词）
        import re
        
        # 移除标点符号
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', ' ', text)
        
        # 分割词汇
        words = cleaned.split()
        
        # 过滤停用词和短词
        stop_words = {'的', '了', '在', '是', '我', '你', '他', '她', '它', '这', '那'}
        filtered_words = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return filtered_words
        
    def _extract_topic(self, text: str) -> str:
        """从文本中提取话题"""
        # 简单的关键词匹配
        topic_keywords = {
            '记忆系统': ['记忆', '回忆', '存储', '检索'],
            '架构设计': ['架构', '设计', '系统', '模块'],
            'API开发': ['API', '接口', '调用', '请求'],
            '错误处理': ['错误', '异常', '修复', '解决']
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return topic
                    
        return 'general'
        
    def get_param_analytics(self) -> Dict:
        """获取参数分析数据"""
        return {
            'current_params': self.base_params.copy(),
            'adaptive_weights': self.adaptive_weights.copy(),
            'conversation_stats': {
                'total_turns': len(self.conversation_history),
                'recent_loop_count': self._count_recent_loops(),
                'avg_repetition_rate': self._calculate_repetition_rate(),
                'avg_diversity_score': self._calculate_diversity_score()
            },
            'adjustment_history': list(self.loop_detection_history)
        }
        
    def reset_adaptive_weights(self):
        """重置自适应权重"""
        self.adaptive_weights = {
            'temperature': 1.0,
            'frequency_penalty': 1.0,
            'presence_penalty': 1.0
        }
        
    def export_config(self) -> Dict:
        """导出配置"""
        return {
            'base_params': self.base_params,
            'adjustment_strategies': self.adjustment_strategies,
            'adaptive_weights': self.adaptive_weights,
            'learning_rate': self.learning_rate
        }
        
    def import_config(self, config: Dict):
        """导入配置"""
        if 'base_params' in config:
            self.base_params.update(config['base_params'])
        if 'adjustment_strategies' in config:
            self.adjustment_strategies.update(config['adjustment_strategies'])
        if 'adaptive_weights' in config:
            self.adaptive_weights.update(config['adaptive_weights'])
        if 'learning_rate' in config:
            self.learning_rate = config['learning_rate']