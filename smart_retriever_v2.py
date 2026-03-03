"""
增强版智能检索器 v2.0
新增功能：话题相关才查 + 智能记忆调用策略 + 动态阈值调整
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math
from collections import defaultdict


class EnhancedSmartRetriever:
    """增强版智能检索器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.topic_keywords = self._load_topic_keywords()
        self.forgetting_curve = self._load_forgetting_curve()
        
        # 新增：话题相关性统计
        self.topic_relevance_stats = defaultdict(int)
        self.topic_retrieval_thresholds = defaultdict(lambda: 0.3)  # 默认阈值
        
        # 新增：记忆调用策略参数
        self.retrieval_strategy = {
            'min_relevance_score': 0.2,      # 最低相关性阈值
            'max_retrieval_count': 3,        # 最大检索数量
            'topic_boost_factor': 1.5,       # 话题相关度提升因子
            'recent_boost_factor': 1.3,      # 近期记忆提升因子
            'adaptive_threshold': True       # 自适应阈值
        }
        
    def detect_current_topic(self, user_input: str, conversation_history: List[Dict]) -> str:
        """
        检测当前话题关键词（增强版：包含话题强度分析）
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史
            
        Returns:
            str: 检测到的话题和强度（格式：topic:strength）
        """
        # 分析用户输入中的关键词
        input_keywords = self._extract_keywords(user_input)
        
        # 分析对话历史中的话题趋势
        history_topics = self._analyze_conversation_trend(conversation_history)
        
        # 合并关键词和话题趋势
        all_keywords = input_keywords + history_topics
        
        # 确定主要话题和强度
        main_topic, topic_strength = self._determine_main_topic_with_strength(all_keywords)
        
        # 更新话题相关性统计
        self._update_topic_relevance_stats(main_topic)
        
        return f"{main_topic}:{topic_strength}"
        
    def should_retrieve_memories(self, current_topic: str, conversation_history: List[Dict]) -> bool:
        """
        判断是否应该检索记忆（话题相关才查）
        
        Args:
            current_topic: 当前话题
            conversation_history: 对话历史
            
        Returns:
            bool: 是否应该检索记忆
        """
        # 解析话题和强度
        topic_parts = current_topic.split(':')
        if len(topic_parts) != 2:
            return False
            
        topic, strength_str = topic_parts
        try:
            strength = float(strength_str)
        except:
            return False
            
        # 话题强度过低时不检索
        if strength < 0.1:
            return False
            
        # 检查话题相关性
        if not self._is_topic_relevant_for_retrieval(topic, conversation_history):
            return False
            
        # 自适应阈值调整
        threshold = self._get_adaptive_threshold(topic)
        
        return strength >= threshold
        
    def auto_retrieve_related_memories(self, current_topic: str, max_results: int = 5) -> List[Dict]:
        """
        话题感知自动检索相关记忆（增强版：智能调用策略）
        
        Args:
            current_topic: 当前话题
            max_results: 最大结果数
            
        Returns:
            List[Dict]: 相关记忆列表
        """
        # 首先判断是否应该检索
        if not self.should_retrieve_memories(current_topic, []):
            return []
            
        # 获取所有记忆
        all_memories = self._get_all_memories()
        
        # 解析话题和强度
        topic_parts = current_topic.split(':')
        if len(topic_parts) != 2:
            return []
            
        topic, strength_str = topic_parts
        
        # 计算每个记忆的相关性得分（增强版）
        scored_memories = []
        for memory in all_memories:
            relevance_score = self._calculate_enhanced_relevance(memory, topic, float(strength_str))
            
            if relevance_score >= self.retrieval_strategy['min_relevance_score']:
                memory["relevance_score"] = relevance_score
                memory["retrieval_reason"] = self._get_retrieval_reason(memory, topic)
                scored_memories.append(memory)
        
        # 按综合得分排序
        scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # 应用智能调用策略
        filtered_memories = self._apply_retrieval_strategy(scored_memories, topic)
        
        # 返回前N个结果
        return filtered_memories[:max_results]
        
    def _determine_main_topic_with_strength(self, keywords: List[str]) -> Tuple[str, float]:
        """
        确定主要话题和强度
        
        Args:
            keywords: 关键词列表
            
        Returns:
            Tuple[str, float]: (话题, 强度)
        """
        if not keywords:
            return "general", 0.0
            
        # 统计关键词所属的话题
        topic_scores = defaultdict(int)
        
        for keyword in keywords:
            for topic, topic_keywords in self.topic_keywords.items():
                if keyword in topic_keywords:
                    topic_scores[topic] += 1
                    
        # 计算话题强度（归一化到0-1）
        if topic_scores:
            max_score = max(topic_scores.values())
            total_score = sum(topic_scores.values())
            
            # 强度 = (最大得分 / 总得分) * (最大得分 / 关键词数量)
            main_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
            strength = (max_score / total_score) * (max_score / len(keywords))
            
            return main_topic, min(strength, 1.0)
            
        return "general", 0.0
        
    def _is_topic_relevant_for_retrieval(self, topic: str, conversation_history: List[Dict]) -> bool:
        """
        判断话题是否适合检索记忆
        
        Args:
            topic: 话题
            conversation_history: 对话历史
            
        Returns:
            bool: 是否适合检索
        """
        # 排除通用话题
        if topic == "general":
            return False
            
        # 检查话题在历史中的出现频率
        topic_frequency = self._calculate_topic_frequency(topic, conversation_history)
        
        # 如果话题频繁出现，可能不需要频繁检索
        if topic_frequency > 5:  # 出现超过5次
            return topic_frequency < 10  # 但不超过10次
            
        return True
        
    def _get_adaptive_threshold(self, topic: str) -> float:
        """
        获取自适应阈值
        
        Args:
            topic: 话题
            
        Returns:
            float: 自适应阈值
        """
        if not self.retrieval_strategy['adaptive_threshold']:
            return self.retrieval_strategy['min_relevance_score']
            
        # 根据话题相关性统计调整阈值
        topic_relevance = self.topic_relevance_stats.get(topic, 0)
        
        # 话题越相关，阈值越低（更容易检索）
        base_threshold = self.retrieval_strategy['min_relevance_score']
        adjustment = min(topic_relevance * 0.05, 0.1)  # 最多降低0.1
        
        return max(base_threshold - adjustment, 0.1)  # 最低0.1
        
    def _calculate_enhanced_relevance(self, memory: Dict, topic: str, topic_strength: float) -> float:
        """
        计算增强版相关性得分
        
        Args:
            memory: 记忆记录
            topic: 当前话题
            topic_strength: 话题强度
            
        Returns:
            float: 增强相关性得分
        """
        # 基础话题相关性
        base_relevance = self._calculate_topic_relevance(memory, topic)
        
        # 时间权重
        time_weight = self._calculate_time_weight(memory)
        
        # 话题强度提升
        topic_boost = 1.0 + (topic_strength * (self.retrieval_strategy['topic_boost_factor'] - 1.0))
        
        # 近期记忆提升
        recency_boost = 1.0
        if time_weight > 0.8:  # 近期记忆
            recency_boost = self.retrieval_strategy['recent_boost_factor']
            
        # 综合得分
        enhanced_score = base_relevance * time_weight * topic_boost * recency_boost
        
        return min(enhanced_score, 1.0)
        
    def _apply_retrieval_strategy(self, memories: List[Dict], topic: str) -> List[Dict]:
        """
        应用智能调用策略
        
        Args:
            memories: 记忆列表
            topic: 当前话题
            
        Returns:
            List[Dict]: 过滤后的记忆列表
        """
        if not memories:
            return []
            
        # 多样性过滤：避免返回过多相似记忆
        diversified_memories = self._apply_diversity_filter(memories, topic)
        
        # 重要性过滤：优先返回重要性高的记忆
        important_memories = self._apply_importance_filter(diversified_memories)
        
        return important_memories
        
    def _apply_diversity_filter(self, memories: List[Dict], topic: str) -> List[Dict]:
        """应用多样性过滤"""
        if len(memories) <= 3:
            return memories
            
        # 按话题相关性分组
        topic_groups = defaultdict(list)
        for memory in memories:
            memory_topic = self._extract_memory_topic(memory)
            topic_groups[memory_topic].append(memory)
            
        # 从每个话题组中选择最相关的1-2个记忆
        selected_memories = []
        for group_memories in topic_groups.values():
            # 按相关性排序
            group_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # 选择前1-2个
            max_per_group = 2 if len(group_memories) > 3 else 1
            selected_memories.extend(group_memories[:max_per_group])
            
        return selected_memories
        
    def _apply_importance_filter(self, memories: List[Dict]) -> List[Dict]:
        """应用重要性过滤"""
        # 根据记忆的重要性级别进行过滤
        important_memories = []
        
        for memory in memories:
            importance = memory.get('importance', 'L3')  # 默认L3
            
            # L1记忆优先，L2次之，L3最后
            if importance == 'L1':
                important_memories.append(memory)
            elif importance == 'L2' and len(important_memories) < 5:
                important_memories.append(memory)
            elif importance == 'L3' and len(important_memories) < 3:
                important_memories.append(memory)
                
        return important_memories
        
    def _get_retrieval_reason(self, memory: Dict, topic: str) -> str:
        """获取检索原因描述"""
        reasons = []
        
        # 话题相关性
        relevance = memory.get("relevance_score", 0)
        if relevance > 0.7:
            reasons.append("高度相关")
        elif relevance > 0.4:
            reasons.append("中度相关")
        else:
            reasons.append("轻度相关")
            
        # 时间因素
        time_weight = memory.get("time_weight", 0)
        if time_weight > 0.8:
            reasons.append("近期记忆")
        elif time_weight > 0.5:
            reasons.append("中期记忆")
        else:
            reasons.append("远期记忆")
            
        # 重要性级别
        importance = memory.get('importance', 'L3')
        reasons.append(f"{importance}级别")
        
        return " | ".join(reasons)
        
    def _update_topic_relevance_stats(self, topic: str):
        """更新话题相关性统计"""
        self.topic_relevance_stats[topic] += 1
        
        # 限制统计数量，避免无限增长
        if len(self.topic_relevance_stats) > 50:
            # 移除最不常用的话题
            least_common = min(self.topic_relevance_stats.items(), key=lambda x: x[1])[0]
            del self.topic_relevance_stats[least_common]
            
    def _calculate_topic_frequency(self, topic: str, conversation_history: List[Dict]) -> int:
        """计算话题在历史中的出现频率"""
        frequency = 0
        
        for memory in conversation_history[-20:]:  # 检查最近20条对话
            text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
            if topic in text:
                frequency += 1
                
        return frequency
        
    def _extract_memory_topic(self, memory: Dict) -> str:
        """提取记忆的话题"""
        return memory.get('topic', 'general')

    # 保留原有的基础方法
    def _load_topic_keywords(self) -> Dict:
        """加载话题关键词库"""
        return {
            "记忆系统": ["记忆", "回忆", "记住", "存储", "检索", "筛选器", "三层记忆"],
            "架构设计": ["架构", "设计", "系统", "模块", "组件", "框架", "结构"],
            "API开发": ["API", "接口", "调用", "请求", "响应", "配额", "端点"],
            "错误处理": ["错误", "异常", "修复", "解决", "问题", "bug", "故障"],
            "数据管理": ["数据", "存储", "数据库", "文件", "缓存", "备份", "管理"],
            "配置管理": ["配置", "设置", "参数", "环境", "路径", "目录", "配置管理"],
            "测试验证": ["测试", "验证", "调试", "检查", "确认", "结果", "验证"]
        }
        
    def _load_forgetting_curve(self) -> Dict:
        """加载遗忘曲线权重配置"""
        return {
            "today": 1.0, "yesterday": 0.8, "this_week": 0.6, 
            "last_week": 0.4, "this_month": 0.2, "older": 0.1
        }
        
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        for topic, topic_keywords in self.topic_keywords.items():
            for keyword in topic_keywords:
                if keyword in text:
                    keywords.append(keyword)
                    break
        return keywords
        
    def _analyze_conversation_trend(self, conversation_history: List[Dict]) -> List[str]:
        """分析对话历史中的话题趋势"""
        if not conversation_history:
            return []
        keyword_frequency = {}
        for memory in conversation_history[-10:]:
            text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
            keywords = self._extract_keywords(text)
            for keyword in keywords:
                keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
        sorted_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:3]]
        
    def _calculate_topic_relevance(self, memory: Dict, topic: str) -> float:
        """计算话题相关性"""
        text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
        keywords = self._extract_keywords(text)
        
        topic_keywords = self.topic_keywords.get(topic, [])
        if not topic_keywords:
            return 0.0
            
        # 计算匹配的关键词比例
        matched = sum(1 for kw in keywords if kw in topic_keywords)
        return matched / len(topic_keywords) if topic_keywords else 0.0
        
    def _calculate_time_weight(self, memory: Dict) -> float:
        """计算时间权重"""
        timestamp = memory.get('timestamp', '')
        if not timestamp:
            return self.forgetting_curve['older']
            
        # 简化实现：根据日期判断时间权重
        return self.forgetting_curve['today']  # 默认今天权重
        
    def _get_all_memories(self) -> List[Dict]:
        """获取所有记忆（简化实现）"""
        # 返回示例记忆数据
        return [
            {
                'timestamp': '2026-03-02',
                'user_input': '如何优化记忆系统性能？',
                'ai_response': '建议使用缓存机制和智能压缩算法',
                'topic': '记忆系统',
                'importance': 'L1'
            },
            {
                'timestamp': '2026-03-01', 
                'user_input': 'API接口设计要注意什么？',
                'ai_response': '需要注意错误处理和限流机制',
                'topic': 'API开发',
                'importance': 'L2'
            }
        ]