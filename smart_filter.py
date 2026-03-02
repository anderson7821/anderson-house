"""
智能筛选器模块 - 基于用户建议的智能记忆管理
实现重要性识别、自动检索、压缩存储和睡眠整理
"""

import os
import re
import json
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib


class SmartFilter:
    """智能筛选器 - 基于用户建议的智能记忆管理"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.importance_patterns = self._load_importance_patterns()
        self.topic_counter = {}  # 话题出现次数计数器
        self.tag_patterns = self._load_tag_patterns()  # 标签模式
        self.importance_scorer = self._load_importance_scorer()  # 重要性评分器
        
    def _load_importance_patterns(self) -> Dict:
        """加载重要性识别模式"""
        return {
            "high_importance": [
                r"记住[：:].*",  # "记住：..."
                r"我叫[：:].*",   # "我叫：..."
                r"项目重点是[：:].*",  # "项目重点是：..."
                r"项目核心[：:].*",  # "项目核心：..."
                r"重要[：:].*",  # "重要：..."
                r"关键[：:].*",  # "关键：..."
                r"必须[：:].*",   # "必须：..."
            ],
            "medium_importance": [
                r"需要[：:].*",   # "需要：..."
                r"应该[：:].*",   # "应该：..."
                r"建议[：:].*",   # "建议：..."
            ]
        }
    
    def _load_tag_patterns(self) -> Dict:
        """加载自动打标签模式"""
        return {
            "decision": [
                r"决定[：:].*",  # "决定：..."
                r"选择[：:].*",  # "选择：..."
                r"采用[：:].*",  # "采用：..."
                r"确定[：:].*",  # "确定：..."
                r"最终方案[：:].*",  # "最终方案：..."
            ],
            "bug": [
                r"错误[：:].*",  # "错误：..."
                r"问题[：:].*",  # "问题：..."
                r"修复[：:].*",  # "修复：..."
                r"解决[：:].*",  # "解决：..."
                r"异常[：:].*",  # "异常：..."
            ],
            "feature": [
                r"功能[：:].*",  # "功能：..."
                r"特性[：:].*",  # "特性：..."
                r"实现[：:].*",  # "实现：..."
                r"开发[：:].*",  # "开发：..."
                r"新增[：:].*",  # "新增：..."
            ],
            "question": [
                r"如何[：:].*",  # "如何：..."
                r"为什么[：:].*",  # "为什么：..."
                r"怎么[：:].*",  # "怎么：..."
                r"请教[：:].*",  # "请教：..."
            ]
        }
    
    def _load_importance_scorer(self) -> Dict:
        """加载重要性评分规则"""
        return {
            "base_score": 5,  # 基础分
            "keyword_bonus": {
                "记住": 3, "重要": 3, "关键": 3, "必须": 3,
                "决定": 2, "选择": 2, "采用": 2,
                "错误": 2, "问题": 2, "修复": 2,
                "功能": 2, "特性": 2, "实现": 2
            },
            "length_bonus": {
                "short": 0,    # 短文本（<50字符）
                "medium": 1,   # 中等文本（50-200字符）
                "long": 2      # 长文本（>200字符）
            },
            "topic_repetition_bonus": 2,  # 话题重复加分
            "question_penalty": -1        # 问题类文本减分
        }
    
    def analyze_importance(self, user_input: str, ai_response: str) -> Dict:
        """分析信息重要性（包含自动打标签和评分）"""
        
        # 自动打标签
        tags = self._auto_tag_content(user_input)
        
        # 重要性评分（0-10分）
        importance_score = self._calculate_importance_score(user_input, tags)
        
        # 确定记忆层级
        memory_level = self._determine_memory_level(importance_score, user_input)
        
        return {
            "level": memory_level,  # L1/L2/L3
            "score": importance_score,  # 0-10分
            "tags": tags,  # [type:decision/bug/feature/question]
            "topic": self._extract_topic(user_input)  # 主要话题
        }
    
    def _auto_tag_content(self, text: str) -> List[str]:
        """自动打标签（优化版）"""
        tags = []
        
        # 简化的关键词匹配（更灵敏）
        tag_keywords = {
            "decision": ["决定", "选择", "采用", "确定", "最终方案"],
            "bug": ["错误", "问题", "修复", "解决", "异常", "bug"],
            "feature": ["功能", "特性", "实现", "开发", "新增"],
            "question": ["如何", "为什么", "怎么", "请教", "?"]
        }
        
        for tag_type, keywords in tag_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    tags.append(f"type:{tag_type}")
                    break  # 每个类型只添加一次标签
        
        return tags
    
    def _calculate_importance_score(self, text: str, tags: List[str]) -> int:
        """计算重要性评分（0-10分）"""
        score = self.importance_scorer["base_score"]
        
        # 关键词加分
        for keyword, bonus in self.importance_scorer["keyword_bonus"].items():
            if keyword in text:
                score += bonus
        
        # 文本长度加分
        text_length = len(text)
        if text_length < 50:
            score += self.importance_scorer["length_bonus"]["short"]
        elif text_length < 200:
            score += self.importance_scorer["length_bonus"]["medium"]
        else:
            score += self.importance_scorer["length_bonus"]["long"]
        
        # 话题重复加分
        topic = self._extract_topic(text)
        if topic and self.topic_counter.get(topic, 0) >= 3:
            score += self.importance_scorer["topic_repetition_bonus"]
        
        # 问题类文本减分
        if "type:question" in tags:
            score += self.importance_scorer["question_penalty"]
        
        # 确保分数在0-10之间
        return max(0, min(10, score))
    
    def _determine_memory_level(self, score: int, text: str) -> str:
        """根据评分确定记忆层级（优化阈值）"""
        
        # 检查高重要性模式（最高优先级）
        for pattern in self.importance_patterns["high_importance"]:
            if re.search(pattern, text, re.IGNORECASE):
                return "L1"  # 长期记忆
        
        # 根据评分确定层级（优化阈值）
        if score >= 7:
            return "L1"  # 长期记忆
        elif score >= 4:
            return "L2"  # 情景记忆
        else:
            return "L3"  # 会话记忆
    
    def _extract_topic(self, text: str) -> Optional[str]:
        """提取话题关键词"""
        # 简单的话题提取逻辑
        topics = ["记忆", "架构", "API", "数据", "报告", "错误", "配置", "Python"]
        for topic in topics:
            if topic.lower() in text.lower():
                return topic
        return None
    
    def auto_retrieve_relevant_memories(self, current_topic: str, days: int = 3) -> List[Dict]:
        """自动检索相关记忆（RAG+Memory融合）"""
        
        relevant_memories = []
        
        # 获取最近N天的记忆
        recent_memories = self._get_recent_memories(days)
        
        for memory in recent_memories:
            relevance_score = self._calculate_relevance(memory, current_topic)
            if relevance_score > 0.5:  # 相关性阈值
                memory["relevance_score"] = relevance_score
                relevant_memories.append(memory)
        
        # 按相关性排序
        relevant_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_memories[:10]  # 返回前10个相关记忆
    
    def _get_recent_memories(self, days: int) -> List[Dict]:
        """获取最近N天的记忆"""
        # 简化实现 - 实际应该从存储管理器获取
        memories = []
        today = datetime.now()
        
        for i in range(days):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            memory_file = Path(f".memory/{date_str}.md")
            
            if memory_file.exists():
                memories.extend(self._parse_memory_file(memory_file))
        
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
                        "ai_response": lines[3].replace("**AI**: ", "") if len(lines) > 3 and lines[3].startswith("**AI**: ") else ""
                    }
                    memories.append(memory)
        except Exception as e:
            print(f"解析记忆文件失败: {e}")
        
        return memories
    
    def _calculate_relevance(self, memory: Dict, current_topic: str) -> float:
        """计算记忆相关性"""
        score = 0.0
        
        # 关键词匹配
        keywords = current_topic.lower().split()
        text_to_search = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}".lower()
        
        for keyword in keywords:
            if keyword in text_to_search:
                score += 0.3
        
        # 话题匹配
        memory_topic = self._extract_topic(text_to_search)
        if memory_topic and memory_topic in current_topic:
            score += 0.5
        
        return min(score, 1.0)
    
    def generate_conversation_summary(self, conversation_rounds: List[Dict]) -> Dict:
        """生成对话摘要（每10轮自动生成）"""
        
        if len(conversation_rounds) < 10:
            return {"summary": "对话轮次不足，无需摘要"}
        
        # 提取关键信息
        key_points = []
        for round_data in conversation_rounds:
            importance = self.analyze_importance(
                round_data.get("user_input", ""), 
                round_data.get("ai_response", "")
            )
            
            if importance in ["L1", "L2"]:  # 重要内容
                key_points.append({
                    "timestamp": round_data.get("timestamp", ""),
                    "user_input": self._summarize_text(round_data.get("user_input", "")),
                    "ai_response": self._summarize_text(round_data.get("ai_response", "")),
                    "importance": importance
                })
        
        summary = {
            "summary_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8],
            "generated_at": datetime.now().isoformat(),
            "total_rounds": len(conversation_rounds),
            "key_points_count": len(key_points),
            "key_points": key_points,
            "main_topics": self._extract_main_topics(conversation_rounds)
        }
        
        return summary
    
    def _summarize_text(self, text: str, max_length: int = 100) -> str:
        """文本摘要"""
        if len(text) <= max_length:
            return text
        
        # 简单的摘要逻辑 - 提取前N个字符
        return text[:max_length] + "..."
    
    def _extract_main_topics(self, conversation_rounds: List[Dict]) -> List[str]:
        """提取主要话题"""
        topics = {}
        
        for round_data in conversation_rounds:
            text = f"{round_data.get('user_input', '')} {round_data.get('ai_response', '')}"
            topic = self._extract_topic(text)
            if topic:
                topics[topic] = topics.get(topic, 0) + 1
        
        # 返回出现次数最多的前3个话题
        return [topic for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    def compress_conversation(self, conversation_data: List[Dict], output_path: Path) -> bool:
        """压缩对话数据（节省90%空间）"""
        
        try:
            # 创建临时JSON文件
            temp_file = output_path.with_suffix('.json')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            # 压缩为ZIP
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_file, 'conversation.json')
            
            # 删除临时文件
            temp_file.unlink()
            
            print(f"✅ 对话压缩完成: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 对话压缩失败: {e}")
            return False
    
    def sleep_organize_memories(self, older_than_days: int = 30) -> Dict:
        """睡眠整理机制 - 后台整理记忆"""
        
        organization_report = {
            "started_at": datetime.now().isoformat(),
            "processed_files": 0,
            "merged_memories": 0,
            "compressed_files": 0,
            "cleaned_files": 0,
            "errors": []
        }
        
        try:
            # 获取旧记忆文件
            old_memory_files = self._get_old_memory_files(older_than_days)
            
            for memory_file in old_memory_files:
                organization_report["processed_files"] += 1
                
                # 解析记忆文件
                memories = self._parse_memory_file(memory_file)
                
                if len(memories) > 0:
                    # 生成摘要
                    summary = self.generate_conversation_summary(memories)
                    
                    # 保存摘要到L2
                    summary_file = Path(f".memory/summaries/{memory_file.stem}_summary.json")
                    summary_file.parent.mkdir(exist_ok=True)
                    
                    with open(summary_file, 'w', encoding='utf-8') as f:
                        json.dump(summary, f, ensure_ascii=False, indent=2)
                    
                    # 压缩原始对话
                    compressed_file = Path(f".memory/compressed/{memory_file.stem}.zip")
                    compressed_file.parent.mkdir(exist_ok=True)
                    
                    if self.compress_conversation(memories, compressed_file):
                        organization_report["compressed_files"] += 1
                        
                        # 删除原始文件（可选）
                        # memory_file.unlink()
                        # organization_report["cleaned_files"] += 1
                
                # 合并相似记忆（简化实现）
                organization_report["merged_memories"] += self._merge_similar_memories(memories)
            
            organization_report["completed_at"] = datetime.now().isoformat()
            print(f"✅ 睡眠整理完成: {organization_report}")
            
        except Exception as e:
            organization_report["errors"].append(str(e))
            print(f"❌ 睡眠整理失败: {e}")
        
        return organization_report
    
    def _get_old_memory_files(self, older_than_days: int) -> List[Path]:
        """获取旧记忆文件"""
        old_files = []
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        memory_dir = Path(".memory")
        if memory_dir.exists():
            for file_path in memory_dir.glob("*.md"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    old_files.append(file_path)
        
        return old_files
    
    def _merge_similar_memories(self, memories: List[Dict]) -> int:
        """合并相似记忆"""
        merged_count = 0
        
        # 简单的相似度检测（基于话题）
        topic_groups = {}
        
        for memory in memories:
            topic = self._extract_topic(f"{memory.get('user_input', '')} {memory.get('ai_response', '')}")
            if topic:
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(memory)
        
        # 合并同一话题的记忆
        for topic, group_memories in topic_groups.items():
            if len(group_memories) > 1:
                # 这里可以实现更复杂的合并逻辑
                merged_count += len(group_memories) - 1
        
        return merged_count


# 使用示例
def demo_smart_filter():
    """演示智能筛选器功能"""
    
    config = {
        "compression": {
            "enabled": True,
            "keep_original": False
        },
        "summarization": {
            "auto_summarize_after_rounds": 10
        },
        "cleaning": {
            "auto_clean_after_days": 30
        }
    }
    
    filter = SmartFilter(config)
    
    # 测试重要性分析
    test_inputs = [
        "记住：我的名字是Anderson",
        "项目重点是三层记忆系统",
        "今天天气怎么样？",
        "我们需要优化API调用"
    ]
    
    print("🧠 智能筛选器演示")
    print("=" * 50)
    
    for test_input in test_inputs:
        importance = filter.analyze_importance(test_input, "")
        print(f"输入: {test_input}")
        print(f"重要性: {importance}")
        print("-" * 30)


if __name__ == "__main__":
    demo_smart_filter()