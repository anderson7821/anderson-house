"""
智能检索模块 - 阶段二升级：话题感知自动检索
实现从"手动查询"到"话题触发自动检索"的升级
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math


class SmartRetriever:
    """智能检索器 - 实现话题感知自动检索"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.topic_keywords = self._load_topic_keywords()
        self.forgetting_curve = self._load_forgetting_curve()
        
    def _load_topic_keywords(self) -> Dict:
        """加载话题关键词库（优化版）"""
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
            "today": 1.0,      # 今天 - 权重最高
            "yesterday": 0.8,   # 昨天 - 权重较高
            "this_week": 0.6,   # 本周 - 权重中等
            "last_week": 0.4,   # 上周 - 权重较低
            "this_month": 0.2,  # 本月 - 权重低
            "older": 0.1        # 更早 - 权重最低
        }
    
    def detect_current_topic(self, user_input: str, conversation_history: List[Dict]) -> str:
        """检测当前话题关键词"""
        
        # 分析用户输入中的关键词
        input_keywords = self._extract_keywords(user_input)
        
        # 分析对话历史中的话题趋势
        history_topics = self._analyze_conversation_trend(conversation_history)
        
        # 合并关键词和话题趋势
        all_keywords = input_keywords + history_topics
        
        # 确定主要话题
        main_topic = self._determine_main_topic(all_keywords)
        
        return main_topic
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        
        # 简单的关键词提取（可扩展为更复杂的NLP方法）
        for topic, topic_keywords in self.topic_keywords.items():
            for keyword in topic_keywords:
                if keyword in text:
                    keywords.append(keyword)
                    break  # 每个话题只添加一个关键词
        
        return keywords
    
    def _analyze_conversation_trend(self, conversation_history: List[Dict]) -> List[str]:
        """分析对话历史中的话题趋势"""
        if not conversation_history:
            return []
        
        # 统计最近对话中的关键词频率
        keyword_frequency = {}
        
        for memory in conversation_history[-10:]:  # 分析最近10条对话
            text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
            keywords = self._extract_keywords(text)
            
            for keyword in keywords:
                keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
        
        # 返回出现频率最高的前3个关键词
        sorted_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:3]]
    
    def _determine_main_topic(self, keywords: List[str]) -> str:
        """确定主要话题"""
        if not keywords:
            return "general"  # 默认话题
        
        # 统计关键词所属的话题
        topic_scores = {}
        
        for keyword in keywords:
            for topic, topic_keywords in self.topic_keywords.items():
                if keyword in topic_keywords:
                    topic_scores[topic] = topic_scores.get(topic, 0) + 1
        
        # 返回得分最高的话题
        if topic_scores:
            main_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
            return main_topic
        
        return "general"
    
    def auto_retrieve_related_memories(self, current_topic: str, max_results: int = 5) -> List[Dict]:
        """话题感知自动检索相关记忆"""
        
        # 获取所有记忆
        all_memories = self._get_all_memories()
        
        # 计算每个记忆的相关性得分
        scored_memories = []
        for memory in all_memories:
            relevance_score = self._calculate_topic_relevance(memory, current_topic)
            time_weight = self._calculate_time_weight(memory)
            
            # 综合得分 = 相关性 × 时间权重
            final_score = relevance_score * time_weight
            
            if final_score > 0:  # 只返回有相关性的记忆
                memory["relevance_score"] = final_score
                memory["time_weight"] = time_weight
                scored_memories.append(memory)
        
        # 按综合得分排序
        scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # 返回前N个结果
        return scored_memories[:max_results]
    
    def _get_all_memories(self) -> List[Dict]:
        """获取所有记忆（简化实现）"""
        memories = []
        
        # 读取记忆目录中的所有文件
        memory_dir = Path(".memory")
        if memory_dir.exists():
            for file_path in memory_dir.glob("*.md"):
                memories.extend(self._parse_memory_file(file_path))
        
        return memories
    
    def _parse_memory_file(self, file_path: Path) -> List[Dict]:
        """解析记忆文件"""
        memories = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的Markdown解析
            sections = content.split("## ")
            for section in sections[1:]:  # 跳过第一个空部分
                lines = section.strip().split('\n')
                if len(lines) >= 3:
                    memory = {
                        "timestamp": lines[0].split(" - ")[0] if " - " in lines[0] else "",
                        "title": lines[0].split(" - ")[1] if " - " in lines[0] else lines[0],
                        "user_input": lines[2].replace("**用户**: ", "") if lines[2].startswith("**用户**: ") else "",
                        "ai_response": lines[3].replace("**AI**: ", "") if len(lines) > 3 and lines[3].startswith("**AI**: ") else "",
                        "file_date": file_path.stem  # 文件日期
                    }
                    memories.append(memory)
        except Exception as e:
            print(f"解析记忆文件失败: {e}")
        
        return memories
    
    def _calculate_topic_relevance(self, memory: Dict, current_topic: str) -> float:
        """计算记忆与当前话题的相关性"""
        score = 0.0
        
        # 获取记忆文本
        text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
        
        # 提取记忆中的关键词
        memory_keywords = self._extract_keywords(text)
        
        # 获取当前话题的关键词
        current_keywords = self.topic_keywords.get(current_topic, [])
        
        # 计算关键词匹配度
        if current_keywords and memory_keywords:
            matched_keywords = set(current_keywords) & set(memory_keywords)
            score = len(matched_keywords) / len(current_keywords)
        
        return min(score, 1.0)  # 确保不超过1.0
    
    def _calculate_time_weight(self, memory: Dict) -> float:
        """根据遗忘曲线计算时间权重"""
        
        # 获取记忆日期
        memory_date_str = memory.get("file_date", "")
        if not memory_date_str:
            return self.forgetting_curve["older"]
        
        try:
            memory_date = datetime.strptime(memory_date_str, "%Y-%m-%d")
            today = datetime.now()
            days_diff = (today - memory_date).days
            
            # 根据时间差确定权重
            if days_diff == 0:
                return self.forgetting_curve["today"]
            elif days_diff == 1:
                return self.forgetting_curve["yesterday"]
            elif days_diff <= 7:
                return self.forgetting_curve["this_week"]
            elif days_diff <= 14:
                return self.forgetting_curve["last_week"]
            elif days_diff <= 30:
                return self.forgetting_curve["this_month"]
            else:
                return self.forgetting_curve["older"]
                
        except Exception:
            return self.forgetting_curve["older"]
    
    def progressive_disclosure(self, memories: List[Dict], max_preview_length: int = 100) -> List[Dict]:
        """渐进式披露 - 先显示摘要，需要时再展开全文"""
        
        disclosed_memories = []
        
        for memory in memories:
            # 创建摘要版本
            preview_memory = memory.copy()
            
            # 截断用户输入和AI回复
            if len(preview_memory.get("user_input", "")) > max_preview_length:
                preview_memory["user_input"] = preview_memory["user_input"][:max_preview_length] + "..."
            
            if len(preview_memory.get("ai_response", "")) > max_preview_length:
                preview_memory["ai_response"] = preview_memory["ai_response"][:max_preview_length] + "..."
            
            # 标记为预览版本
            preview_memory["is_preview"] = True
            preview_memory["full_memory_id"] = hash(str(memory))  # 简单ID生成
            
            disclosed_memories.append(preview_memory)
        
        return disclosed_memories
    
    def session_warmup(self, current_topic: str = "") -> List[Dict]:
        """记忆预热 - 新会话加载最相关的5条记忆"""
        
        # 如果没有指定话题，使用默认检索
        if not current_topic:
            current_topic = "general"
        
        # 自动检索相关记忆
        related_memories = self.auto_retrieve_related_memories(current_topic, max_results=5)
        
        # 应用渐进式披露
        warmup_memories = self.progressive_disclosure(related_memories)
        
        return warmup_memories
    
    def optimize_with_forgetting_curve(self, memories: List[Dict]) -> List[Dict]:
        """遗忘曲线优化 - 近期记忆权重高，远期记忆摘要化"""
        
        optimized_memories = []
        
        for memory in memories:
            time_weight = self._calculate_time_weight(memory)
            
            # 根据时间权重决定显示方式
            if time_weight >= 0.6:  # 近期记忆 - 显示全文
                optimized_memories.append(memory)
            elif time_weight >= 0.2:  # 中期记忆 - 显示摘要
                preview_memory = memory.copy()
                preview_memory["user_input"] = preview_memory.get("user_input", "")[:50] + "..."
                preview_memory["ai_response"] = preview_memory.get("ai_response", "")[:50] + "..."
                preview_memory["is_summary"] = True
                optimized_memories.append(preview_memory)
            else:  # 远期记忆 - 仅显示标题
                title_only_memory = {
                    "timestamp": memory.get("timestamp", ""),
                    "title": memory.get("title", ""),
                    "relevance_score": memory.get("relevance_score", 0),
                    "time_weight": time_weight,
                    "is_title_only": True
                }
                optimized_memories.append(title_only_memory)
        
        # 按时间权重排序（近期优先）
        optimized_memories.sort(key=lambda x: x.get("time_weight", 0), reverse=True)
        
        return optimized_memories
    
    def get_memory_expansion(self, memory_id: int) -> Optional[Dict]:
        """获取完整记忆内容（用于渐进式披露）"""
        
        # 在实际实现中，这里应该根据ID查找完整记忆
        # 简化实现：返回示例数据
        return {
            "memory_id": memory_id,
            "full_content": "这是完整记忆内容...",
            "expanded_at": datetime.now().isoformat()
        }


def test_smart_retriever():
    """测试智能检索器功能"""
    
    config = {
        "smart_retriever": {
            "max_results": 5,
            "preview_length": 100
        }
    }
    
    retriever = SmartRetriever(config)
    
    # 测试话题检测
    user_input = "我们需要优化记忆系统的检索功能"
    topic = retriever.detect_current_topic(user_input, [])
    print(f"检测到话题: {topic}")
    
    # 测试会话预热
    warmup_memories = retriever.session_warmup(topic)
    print(f"记忆预热结果: {len(warmup_memories)} 条记忆")
    
    # 测试渐进式披露
    if warmup_memories:
        preview_memories = retriever.progressive_disclosure(warmup_memories)
        print("渐进式披露示例:")
        for memory in preview_memories[:2]:
            print(f"  - {memory.get('title', '')}: {memory.get('user_input', '')[:50]}...")


if __name__ == "__main__":
    test_smart_retriever()
