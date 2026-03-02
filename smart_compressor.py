"""
智能压缩模块 - 阶段三升级：告别150G存储噩梦
实现从"存原始对话"到"存精华摘要"的升级
"""

import os
import re
import json
import zipfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil


class SmartCompressor:
    """智能压缩器 - 实现记忆压缩和存储优化"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.compression_settings = self._load_compression_settings()
        
    def _load_compression_settings(self) -> Dict:
        """加载压缩配置"""
        return {
            "auto_summary_rounds": 10,  # 每10轮对话生成摘要
            "summary_max_length": 200,  # 摘要最大长度200字
            "compress_after_days": 30,  # 30天后压缩原始对话
            "space_warning_threshold": 1024,  # 1GB空间预警
            "similarity_threshold": 0.8,     # 相似度阈值80%
            "keep_original": False           # 压缩后是否保留原始文件
        }
    
    def generate_conversation_summary(self, conversation_rounds: List[Dict]) -> Dict:
        """生成对话摘要（每10轮自动生成）"""
        
        if len(conversation_rounds) < 3:
            return {
                "summary": "对话轮次不足，无需摘要",
                "rounds_count": len(conversation_rounds),
                "generated_at": datetime.now().isoformat()
            }
        
        # 提取关键信息点
        key_points = []
        decisions = []
        problems = []
        features = []
        
        for round_data in conversation_rounds:
            user_input = round_data.get("user_input", "")
            ai_response = round_data.get("ai_response", "")
            
            # 识别重要内容
            if self._is_important_content(user_input):
                key_points.append({
                    "timestamp": round_data.get("timestamp", ""),
                    "user_input": self._summarize_text(user_input),
                    "ai_response": self._summarize_text(ai_response),
                    "importance": self._analyze_importance(user_input)
                })
            
            # 分类内容
            if "决定" in user_input or "选择" in user_input:
                decisions.append(self._extract_decision(user_input, ai_response))
            elif "错误" in user_input or "问题" in user_input:
                problems.append(self._extract_problem(user_input, ai_response))
            elif "功能" in user_input or "实现" in user_input:
                features.append(self._extract_feature(user_input, ai_response))
        
        # 生成摘要文本
        summary_parts = []
        
        if decisions:
            summary_parts.append(f"**决策事项** ({len(decisions)}项): " + ", ".join([d["title"] for d in decisions[:3]]))
        
        if problems:
            summary_parts.append(f"**问题解决** ({len(problems)}项): " + ", ".join([p["title"] for p in problems[:3]]))
        
        if features:
            summary_parts.append(f"**功能实现** ({len(features)}项): " + ", ".join([f["title"] for f in features[:3]]))
        
        if key_points:
            summary_parts.append(f"**关键讨论** ({len(key_points)}项)")
        
        summary_text = "；".join(summary_parts)
        
        # 限制摘要长度
        if len(summary_text) > self.compression_settings["summary_max_length"]:
            summary_text = summary_text[:self.compression_settings["summary_max_length"]] + "..."
        
        return {
            "summary_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8],
            "generated_at": datetime.now().isoformat(),
            "total_rounds": len(conversation_rounds),
            "summary": summary_text,
            "key_points_count": len(key_points),
            "decisions_count": len(decisions),
            "problems_count": len(problems),
            "features_count": len(features),
            "key_points": key_points[:5],  # 最多5个关键点
            "decisions": decisions[:3],    # 最多3个决策
            "problems": problems[:3],      # 最多3个问题
            "features": features[:3]        # 最多3个功能
        }
    
    def _is_important_content(self, text: str) -> bool:
        """判断是否为重要内容"""
        important_keywords = ["记住", "重要", "关键", "必须", "决定", "选择", "错误", "问题", "功能", "实现"]
        return any(keyword in text for keyword in important_keywords)
    
    def _analyze_importance(self, text: str) -> str:
        """分析内容重要性"""
        if "记住" in text or "重要" in text or "关键" in text:
            return "high"
        elif "决定" in text or "选择" in text:
            return "medium"
        else:
            return "low"
    
    def _summarize_text(self, text: str, max_length: int = 50) -> str:
        """文本摘要"""
        if len(text) <= max_length:
            return text
        
        # 简单的摘要逻辑：取前max_length个字符
        return text[:max_length] + "..."
    
    def _extract_decision(self, user_input: str, ai_response: str) -> Dict:
        """提取决策信息"""
        return {
            "title": "决策: " + user_input[:30] + "...",
            "user_input": self._summarize_text(user_input),
            "ai_response": self._summarize_text(ai_response),
            "type": "decision"
        }
    
    def _extract_problem(self, user_input: str, ai_response: str) -> Dict:
        """提取问题信息"""
        return {
            "title": "问题: " + user_input[:30] + "...",
            "user_input": self._summarize_text(user_input),
            "ai_response": self._summarize_text(ai_response),
            "type": "problem"
        }
    
    def _extract_feature(self, user_input: str, ai_response: str) -> Dict:
        """提取功能信息"""
        return {
            "title": "功能: " + user_input[:30] + "...",
            "user_input": self._summarize_text(user_input),
            "ai_response": self._summarize_text(ai_response),
            "type": "feature"
        }
    
    def compress_old_conversations(self, older_than_days: int = 30) -> Dict:
        """压缩旧对话（30天后自动压缩）"""
        
        compression_report = {
            "started_at": datetime.now().isoformat(),
            "processed_files": 0,
            "compressed_files": 0,
            "saved_space": 0,
            "errors": []
        }
        
        try:
            # 获取旧记忆文件
            old_files = self._get_old_memory_files(older_than_days)
            
            for file_path in old_files:
                compression_report["processed_files"] += 1
                
                # 检查文件大小
                file_size = file_path.stat().st_size
                
                # 压缩文件
                zip_path = file_path.with_suffix('.zip')
                
                if self._compress_file(file_path, zip_path):
                    compression_report["compressed_files"] += 1
                    
                    # 计算节省空间
                    zip_size = zip_path.stat().st_size
                    space_saved = file_size - zip_size
                    compression_report["saved_space"] += max(0, space_saved)
                    
                    # 根据配置决定是否删除原始文件
                    if not self.compression_settings["keep_original"]:
                        file_path.unlink()
                        print(f"✅ 已压缩并删除: {file_path.name}")
                    else:
                        print(f"✅ 已压缩: {file_path.name}")
                else:
                    compression_report["errors"].append(f"压缩失败: {file_path.name}")
            
            compression_report["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            compression_report["errors"].append(f"压缩过程异常: {e}")
        
        return compression_report
    
    def _get_old_memory_files(self, older_than_days: int) -> List[Path]:
        """获取旧记忆文件"""
        old_files = []
        memory_dir = Path(".memory")
        
        if not memory_dir.exists():
            return old_files
        
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        for file_path in memory_dir.glob("*.md"):
            try:
                # 从文件名解析日期
                file_date_str = file_path.stem
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    old_files.append(file_path)
            except ValueError:
                # 文件名格式不匹配，跳过
                continue
        
        return old_files
    
    def _compress_file(self, source_path: Path, target_path: Path) -> bool:
        """压缩单个文件"""
        try:
            with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(source_path, source_path.name)
            return True
        except Exception as e:
            print(f"❌ 压缩失败 {source_path.name}: {e}")
            return False
    
    def merge_similar_memories(self, similarity_threshold: float = 0.8) -> Dict:
        """合并相似记忆内容"""
        
        merge_report = {
            "started_at": datetime.now().isoformat(),
            "processed_files": 0,
            "merged_groups": 0,
            "saved_entries": 0,
            "errors": []
        }
        
        try:
            # 获取所有记忆文件
            memory_files = self._get_all_memory_files()
            
            # 按日期分组处理
            files_by_date = {}
            for file_path in memory_files:
                date_str = file_path.stem
                if date_str not in files_by_date:
                    files_by_date[date_str] = []
                files_by_date[date_str].append(file_path)
            
            # 处理每个日期的记忆
            for date_str, file_paths in files_by_date.items():
                merge_report["processed_files"] += len(file_paths)
                
                # 读取并分析记忆内容
                memories = []
                for file_path in file_paths:
                    memories.extend(self._parse_memory_file(file_path))
                
                # 查找相似记忆
                similar_groups = self._find_similar_memories(memories, similarity_threshold)
                
                if similar_groups:
                    merge_report["merged_groups"] += len(similar_groups)
                    
                    # 合并相似记忆
                    for group in similar_groups:
                        if len(group) > 1:
                            merged_memory = self._merge_memory_group(group)
                            merge_report["saved_entries"] += (len(group) - 1)
                            
                            # 保存合并后的记忆
                            self._save_merged_memory(merged_memory, date_str)
            
            merge_report["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            merge_report["errors"].append(f"合并过程异常: {e}")
        
        return merge_report
    
    def _get_all_memory_files(self) -> List[Path]:
        """获取所有记忆文件"""
        memory_dir = Path(".memory")
        if memory_dir.exists():
            return list(memory_dir.glob("*.md"))
        return []
    
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
                        "file_path": file_path
                    }
                    memories.append(memory)
        except Exception as e:
            print(f"解析记忆文件失败: {e}")
        
        return memories
    
    def _find_similar_memories(self, memories: List[Dict], threshold: float) -> List[List[Dict]]:
        """查找相似记忆"""
        similar_groups = []
        processed = set()
        
        for i, memory1 in enumerate(memories):
            if i in processed:
                continue
            
            similar_group = [memory1]
            processed.add(i)
            
            for j, memory2 in enumerate(memories[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = self._calculate_similarity(memory1, memory2)
                if similarity >= threshold:
                    similar_group.append(memory2)
                    processed.add(j)
            
            if len(similar_group) > 1:
                similar_groups.append(similar_group)
        
        return similar_groups
    
    def _calculate_similarity(self, memory1: Dict, memory2: Dict) -> float:
        """计算记忆相似度"""
        # 简单的文本相似度计算（可扩展为更复杂的算法）
        text1 = f"{memory1.get('user_input', '')} {memory1.get('ai_response', '')}"
        text2 = f"{memory2.get('user_input', '')} {memory2.get('ai_response', '')}"
        
        # 基于共同关键词的相似度
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1 & words2
        similarity = len(common_words) / min(len(words1), len(words2))
        
        return similarity
    
    def _merge_memory_group(self, memories: List[Dict]) -> Dict:
        """合并记忆组"""
        # 选择最重要的记忆作为基础
        base_memory = max(memories, key=lambda m: len(m.get('user_input', '')) + len(m.get('ai_response', '')))
        
        # 合并标题
        titles = [m.get('title', '') for m in memories]
        merged_title = " | ".join(set(titles))
        
        # 合并内容
        user_inputs = [m.get('user_input', '') for m in memories]
        ai_responses = [m.get('ai_response', '') for m in memories]
        
        merged_user_input = " | ".join(set(user_inputs))
        merged_ai_response = " | ".join(set(ai_responses))
        
        return {
            "timestamp": base_memory.get("timestamp", ""),
            "title": merged_title,
            "user_input": merged_user_input,
            "ai_response": merged_ai_response,
            "merged_from": len(memories),
            "original_titles": titles
        }
    
    def _save_merged_memory(self, memory: Dict, date_str: str):
        """保存合并后的记忆"""
        # 在实际实现中，这里应该保存到新的记忆文件
        print(f"📝 合并记忆: {memory['title']} (合并自{memory['merged_from']}条)")
    
    def check_storage_space(self) -> Dict:
        """检查存储空间"""
        
        space_report = {
            "checked_at": datetime.now().isoformat(),
            "total_size_mb": 0,
            "file_count": 0,
            "warning_level": "normal",  # normal/warning/critical
            "recommendations": []
        }
        
        try:
            memory_dir = Path(".memory")
            
            if not memory_dir.exists():
                space_report["message"] = "记忆目录不存在"
                return space_report
            
            # 计算总大小
            total_size = 0
            file_count = 0
            
            for file_path in memory_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            total_size_mb = total_size / (1024 * 1024)
            space_report["total_size_mb"] = round(total_size_mb, 2)
            space_report["file_count"] = file_count
            
            # 判断预警级别
            threshold = self.compression_settings["space_warning_threshold"]
            
            if total_size_mb > threshold * 2:
                space_report["warning_level"] = "critical"
                space_report["recommendations"].append("立即执行压缩清理")
            elif total_size_mb > threshold:
                space_report["warning_level"] = "warning"
                space_report["recommendations"].append("建议执行压缩清理")
            else:
                space_report["warning_level"] = "normal"
                space_report["recommendations"].append("存储空间正常")
            
            # 添加详细建议
            if total_size_mb > 500:
                space_report["recommendations"].append("考虑启用自动压缩功能")
            if file_count > 1000:
                space_report["recommendations"].append("考虑合并相似记忆")
            
        except Exception as e:
            space_report["error"] = str(e)
        
        return space_report


def test_smart_compressor():
    """测试智能压缩器功能"""
    
    config = {
        "smart_compressor": {
            "auto_summary_rounds": 10,
            "summary_max_length": 200,
            "compress_after_days": 30,
            "space_warning_threshold": 1024,
            "similarity_threshold": 0.8,
            "keep_original": False
        }
    }
    
    compressor = SmartCompressor(config)
    
    # 测试摘要生成
    test_conversations = [
        {"user_input": "记住：三层记忆系统架构", "ai_response": "好的，已记录三层记忆架构", "timestamp": "10:00"},
        {"user_input": "决定采用智能压缩方案", "ai_response": "建议使用摘要+压缩策略", "timestamp": "10:15"},
        {"user_input": "错误：存储空间不足", "ai_response": "立即执行压缩清理", "timestamp": "10:30"}
    ]
    
    summary = compressor.generate_conversation_summary(test_conversations)
    print(f"摘要生成测试: {summary['summary']}")
    
    # 测试空间检查
    space_report = compressor.check_storage_space()
    print(f"空间检查: {space_report['total_size_mb']}MB, 级别: {space_report['warning_level']}")


if __name__ == "__main__":
    test_smart_compressor()