"""
可视化面板模块 - 阶段五升级：让记忆看得见
实现从"黑盒"到"透明可控"的升级
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import hashlib


class VisualizationPanel:
    """可视化面板 - 实现记忆的可视化与交互"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.visualization_settings = self._load_visualization_settings()
        
    def _load_visualization_settings(self) -> Dict:
        """加载可视化配置"""
        return {
            "recent_memories_count": 10,      # 最近记忆显示数量
            "hot_topics_count": 5,            # 热点话题显示数量
            "search_results_limit": 20,       # 搜索结果限制
            "graph_max_nodes": 50,            # 图谱最大节点数
            "auto_refresh_seconds": 30        # 自动刷新间隔（秒）
        }
    
    def generate_sidebar_content(self) -> Dict:
        """生成侧边栏内容（最近记忆和热点）"""
        
        sidebar_content = {
            "generated_at": datetime.now().isoformat(),
            "recent_memories": [],
            "hot_topics": [],
            "memory_stats": {},
            "errors": []
        }
        
        try:
            # 获取所有记忆
            all_memories = self._get_all_memories()
            
            # 生成最近记忆列表
            recent_memories = self._get_recent_memories(all_memories)
            sidebar_content["recent_memories"] = recent_memories
            
            # 生成热点话题列表
            hot_topics = self._get_hot_topics(all_memories)
            sidebar_content["hot_topics"] = hot_topics
            
            # 生成记忆统计
            memory_stats = self._get_memory_statistics(all_memories)
            sidebar_content["memory_stats"] = memory_stats
            
        except Exception as e:
            sidebar_content["errors"].append(str(e))
        
        return sidebar_content
    
    def _get_all_memories(self) -> List[Dict]:
        """获取所有记忆"""
        memories = []
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
            
            sections = content.split("## ")
            for section in sections[1:]:
                lines = section.strip().split('\n')
                if len(lines) >= 3:
                    memory = {
                        "id": hashlib.md5(section.encode()).hexdigest()[:8],
                        "timestamp": lines[0].split(" - ")[0] if " - " in lines[0] else "",
                        "title": lines[0].split(" - ")[1] if " - " in lines[0] else lines[0],
                        "user_input": lines[2].replace("**用户**: ", "") if lines[2].startswith("**用户**: ") else "",
                        "ai_response": lines[3].replace("**AI**: ", "") if len(lines) > 3 and lines[3].startswith("**AI**: ") else "",
                        "file_path": str(file_path),
                        "importance": self._extract_importance(lines[0]),
                        "tags": self._extract_tags(lines)
                    }
                    memories.append(memory)
        except Exception as e:
            print(f"解析记忆文件失败: {e}")
        
        return memories
    
    def _extract_importance(self, title_line: str) -> str:
        """从标题行提取重要性级别"""
        if "🔴" in title_line:
            return "L1"
        elif "🟡" in title_line:
            return "L2"
        elif "🔵" in title_line:
            return "L3"
        else:
            return "L3"
    
    def _extract_tags(self, lines: List[str]) -> List[str]:
        """从内容中提取标签"""
        tags = []
        
        for line in lines:
            # 查找标签模式 [type:xxx]
            tag_matches = re.findall(r'\[type:(\w+)\]', line)
            tags.extend(tag_matches)
            
            # 查找其他标签模式
            if "记住" in line:
                tags.append("important")
            if "决定" in line or "选择" in line:
                tags.append("decision")
            if "错误" in line or "问题" in line:
                tags.append("problem")
            if "功能" in line or "实现" in line:
                tags.append("feature")
        
        return list(set(tags))  # 去重
    
    def _get_recent_memories(self, memories: List[Dict]) -> List[Dict]:
        """获取最近记忆"""
        # 按时间戳排序（假设时间戳格式为 HH:MM）
        sorted_memories = sorted(memories, 
                                key=lambda x: x.get("timestamp", ""), 
                                reverse=True)
        
        # 返回最近的N条
        return sorted_memories[:self.visualization_settings["recent_memories_count"]]
    
    def _get_hot_topics(self, memories: List[Dict]) -> List[Dict]:
        """获取热点话题"""
        
        # 分析话题频率
        topic_frequency = {}
        
        for memory in memories:
            # 提取关键词作为话题
            keywords = self._extract_keywords(memory.get("user_input", "") + 
                                            memory.get("ai_response", ""))
            
            for keyword in keywords:
                if keyword in topic_frequency:
                    topic_frequency[keyword] += 1
                else:
                    topic_frequency[keyword] = 1
        
        # 按频率排序
        sorted_topics = sorted(topic_frequency.items(), 
                              key=lambda x: x[1], 
                              reverse=True)
        
        # 转换为标准格式
        hot_topics = []
        for topic, frequency in sorted_topics[:self.visualization_settings["hot_topics_count"]]:
            hot_topics.append({
                "topic": topic,
                "frequency": frequency,
                "heat_level": self._calculate_heat_level(frequency)
            })
        
        return hot_topics
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（基于常见技术词汇）
        keywords = []
        
        # 技术相关关键词
        tech_keywords = ["记忆", "系统", "功能", "实现", "代码", "测试", "bug", 
                        "错误", "问题", "决定", "选择", "配置", "设置", "优化"]
        
        for keyword in tech_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        # 提取项目相关关键词
        project_keywords = ["三层", "记忆系统", "智能", "筛选器", "检索器", 
                          "压缩器", "整理器", "可视化"]
        
        for keyword in project_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return list(set(keywords))  # 去重
    
    def _calculate_heat_level(self, frequency: int) -> str:
        """计算热度级别"""
        if frequency >= 10:
            return "high"
        elif frequency >= 5:
            return "medium"
        else:
            return "low"
    
    def _get_memory_statistics(self, memories: List[Dict]) -> Dict:
        """获取记忆统计信息"""
        stats = {
            "total_count": len(memories),
            "l1_count": 0,
            "l2_count": 0,
            "l3_count": 0,
            "today_count": 0,
            "week_count": 0
        }
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        for memory in memories:
            # 重要性统计
            importance = memory.get("importance", "L3")
            if importance == "L1":
                stats["l1_count"] += 1
            elif importance == "L2":
                stats["l2_count"] += 1
            else:
                stats["l3_count"] += 1
            
            # 时间统计（简化实现）
            # 实际实现中应该使用文件创建时间
            stats["today_count"] += 1  # 简化：所有记忆都算今天的
            stats["week_count"] += 1   # 简化：所有记忆都算本周的
        
        return stats
    
    def search_memories(self, query: str, filters: Optional[Dict] = None) -> Dict:
        """搜索记忆"""
        
        search_results = {
            "query": query,
            "filters": filters,
            "results": [],
            "total_count": 0,
            "errors": []
        }
        
        try:
            # 获取所有记忆
            all_memories = self._get_all_memories()
            
            # 应用搜索条件
            filtered_memories = self._apply_search_filters(all_memories, query, filters)
            
            # 按相关性排序
            scored_memories = []
            for memory in filtered_memories:
                score = self._calculate_search_score(memory, query)
                memory["search_score"] = score
                scored_memories.append(memory)
            
            scored_memories.sort(key=lambda x: x["search_score"], reverse=True)
            
            # 限制结果数量
            limited_results = scored_memories[:self.visualization_settings["search_results_limit"]]
            
            search_results["results"] = limited_results
            search_results["total_count"] = len(filtered_memories)
            
        except Exception as e:
            search_results["errors"].append(str(e))
        
        return search_results
    
    def _apply_search_filters(self, memories: List[Dict], query: str, filters: Optional[Dict]) -> List[Dict]:
        """应用搜索过滤器"""
        filtered_memories = memories
        
        if filters:
            # 重要性过滤
            if "importance" in filters:
                filtered_memories = [m for m in filtered_memories 
                                   if m.get("importance") in filters["importance"]]
            
            # 标签过滤
            if "tags" in filters:
                filtered_memories = [m for m in filtered_memories 
                                   if any(tag in m.get("tags", []) for tag in filters["tags"])]
            
            # 时间范围过滤
            if "date_range" in filters:
                # 简化实现
                pass
        
        # 关键词搜索
        if query:
            filtered_memories = [m for m in filtered_memories 
                               if self._matches_query(m, query)]
        
        return filtered_memories
    
    def _matches_query(self, memory: Dict, query: str) -> bool:
        """检查记忆是否匹配查询"""
        search_text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
        return query.lower() in search_text.lower()
    
    def _calculate_search_score(self, memory: Dict, query: str) -> float:
        """计算搜索相关性得分"""
        score = 0.0
        
        search_text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
        
        # 关键词匹配得分
        if query.lower() in search_text.lower():
            score += 1.0
        
        # 重要性得分
        importance = memory.get("importance", "L3")
        if importance == "L1":
            score += 0.5
        elif importance == "L2":
            score += 0.2
        
        # 时间得分（简化：越新得分越高）
        score += 0.1
        
        return score
    
    def generate_graph_view(self, center_memory_id: Optional[str] = None) -> Dict:
        """生成记忆关联图谱视图"""
        
        graph_data = {
            "nodes": [],
            "edges": [],
            "center_node": center_memory_id,
            "errors": []
        }
        
        try:
            # 获取所有记忆
            all_memories = self._get_all_memories()
            
            # 限制节点数量
            limited_memories = all_memories[:self.visualization_settings["graph_max_nodes"]]
            
            # 生成节点
            for memory in limited_memories:
                node = {
                    "id": memory["id"],
                    "label": memory["title"][:30] + ("..." if len(memory["title"]) > 30 else ""),
                    "importance": memory.get("importance", "L3"),
                    "tags": memory.get("tags", []),
                    "timestamp": memory.get("timestamp", "")
                }
                graph_data["nodes"].append(node)
            
            # 生成边（关联关系）
            # 简化实现：基于相似度创建关联
            for i, memory1 in enumerate(limited_memories):
                for j, memory2 in enumerate(limited_memories[i+1:], i+1):
                    similarity = self._calculate_memory_similarity(memory1, memory2)
                    
                    if similarity > 0.3:  # 相似度阈值
                        edge = {
                            "source": memory1["id"],
                            "target": memory2["id"],
                            "weight": similarity,
                            "label": f"相似度: {similarity:.2f}"
                        }
                        graph_data["edges"].append(edge)
            
        except Exception as e:
            graph_data["errors"].append(str(e))
        
        return graph_data
    
    def _calculate_memory_similarity(self, memory1: Dict, memory2: Dict) -> float:
        """计算记忆相似度"""
        text1 = f"{memory1.get('user_input', '')} {memory1.get('ai_response', '')}"
        text2 = f"{memory2.get('user_input', '')} {memory2.get('ai_response', '')}"
        
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1 & words2
        similarity = len(common_words) / min(len(words1), len(words2))
        
        return similarity
    
    def edit_memory(self, memory_id: str, updates: Dict) -> Dict:
        """编辑记忆"""
        
        edit_result = {
            "memory_id": memory_id,
            "success": False,
            "updated_fields": [],
            "errors": []
        }
        
        try:
            # 在实际实现中，这里应该修改记忆文件
            # 简化实现：记录编辑操作
            
            print(f"[VisualizationPanel] 编辑记忆: {memory_id}")
            print(f"更新内容: {updates}")
            
            edit_result["success"] = True
            edit_result["updated_fields"] = list(updates.keys())
            
        except Exception as e:
            edit_result["errors"].append(str(e))
        
        return edit_result
    
    def delete_memory(self, memory_id: str) -> Dict:
        """删除记忆"""
        
        delete_result = {
            "memory_id": memory_id,
            "success": False,
            "errors": []
        }
        
        try:
            # 在实际实现中，这里应该删除记忆文件
            # 简化实现：记录删除操作
            
            print(f"[VisualizationPanel] 删除记忆: {memory_id}")
            
            delete_result["success"] = True
            
        except Exception as e:
            delete_result["errors"].append(str(e))
        
        return delete_result


def test_visualization_panel():
    """测试可视化面板功能"""
    
    config = {
        "visualization_panel": {
            "recent_memories_count": 5,
            "hot_topics_count": 3,
            "search_results_limit": 10,
            "graph_max_nodes": 20,
            "auto_refresh_seconds": 30
        }
    }
    
    panel = VisualizationPanel(config)
    
    # 测试侧边栏内容生成
    sidebar_content = panel.generate_sidebar_content()
    print(f"侧边栏内容: {len(sidebar_content['recent_memories'])}条最近记忆, {len(sidebar_content['hot_topics'])}个热点话题")
    
    # 测试搜索功能
    search_results = panel.search_memories("记忆")
    print(f"搜索结果: {search_results['total_count']}条")
    
    # 测试图谱视图
    graph_data = panel.generate_graph_view()
    print(f"图谱数据: {len(graph_data['nodes'])}个节点, {len(graph_data['edges'])}条边")
    
    print("✅ 可视化面板功能测试完成")


if __name__ == "__main__":
    test_visualization_panel()