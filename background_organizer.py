"""
后台整理模块 - 阶段四升级：睡眠中工作
实现从"实时处理"到"闲时优化"的升级
"""

import os
import re
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib


class BackgroundOrganizer:
    """后台整理器 - 实现闲时优化和记忆迁移"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.organizer_settings = self._load_organizer_settings()
        self.is_running = False
        self.background_thread = None
        self.last_activity_time = datetime.now()
        
    def _load_organizer_settings(self) -> Dict:
        """加载整理器配置"""
        return {
            "idle_threshold_minutes": 5,      # 空闲5分钟后开始整理
            "migration_threshold_days": 7,    # 7天未访问的记忆降级
            "quality_evaluation_days": 30,    # 30天评估记忆质量
            "low_quality_threshold": 0.3,     # 质量评分低于0.3淘汰
            "association_discovery_enabled": True,  # 启用关联发现
            "max_background_time_minutes": 10  # 最大后台运行时间10分钟
        }
    
    def start_background_organization(self):
        """启动后台整理线程"""
        if self.is_running:
            print("[BackgroundOrganizer] 后台整理已在运行中")
            return
        
        self.is_running = True
        self.background_thread = threading.Thread(target=self._background_worker)
        self.background_thread.daemon = True
        self.background_thread.start()
        
        print("[BackgroundOrganizer] 后台整理线程已启动")
    
    def stop_background_organization(self):
        """停止后台整理"""
        self.is_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        
        print("[BackgroundOrganizer] 后台整理线程已停止")
    
    def _background_worker(self):
        """后台工作线程"""
        print("[BackgroundOrganizer] 后台工作线程启动")
        
        start_time = datetime.now()
        
        while self.is_running:
            try:
                # 检查是否空闲
                if self._is_idle():
                    print("[BackgroundOrganizer] 检测到空闲状态，开始后台整理...")
                    
                    # 执行后台整理任务
                    self._perform_background_tasks()
                    
                    # 检查是否超过最大运行时间
                    if (datetime.now() - start_time).total_seconds() > self.organizer_settings["max_background_time_minutes"] * 60:
                        print("[BackgroundOrganizer] 达到最大运行时间，停止整理")
                        break
                
                # 休眠30秒后再次检查
                time.sleep(30)
                
            except Exception as e:
                print(f"[BackgroundOrganizer] 后台工作线程异常: {e}")
                time.sleep(60)  # 异常后休眠1分钟
        
        self.is_running = False
        print("[BackgroundOrganizer] 后台工作线程结束")
    
    def _is_idle(self) -> bool:
        """检查是否处于空闲状态"""
        idle_threshold = self.organizer_settings["idle_threshold_minutes"]
        idle_time = (datetime.now() - self.last_activity_time).total_seconds() / 60
        
        return idle_time >= idle_threshold
    
    def update_activity_time(self):
        """更新活动时间（用户操作时调用）"""
        self.last_activity_time = datetime.now()
    
    def _perform_background_tasks(self):
        """执行后台整理任务"""
        organization_report = {
            "started_at": datetime.now().isoformat(),
            "tasks_completed": 0,
            "memory_migrations": 0,
            "associations_discovered": 0,
            "low_quality_memories": 0,
            "errors": []
        }
        
        try:
            # 任务1: 记忆迁移（低频记忆降级）
            migration_result = self._migrate_low_frequency_memories()
            organization_report["memory_migrations"] = migration_result["migrated_count"]
            organization_report["tasks_completed"] += 1
            
            # 任务2: 关联发现
            if self.organizer_settings["association_discovery_enabled"]:
                association_result = self._discover_memory_associations()
                organization_report["associations_discovered"] = association_result["associations_count"]
                organization_report["tasks_completed"] += 1
            
            # 任务3: 质量评估
            quality_result = self._evaluate_memory_quality()
            organization_report["low_quality_memories"] = quality_result["low_quality_count"]
            organization_report["tasks_completed"] += 1
            
            organization_report["completed_at"] = datetime.now().isoformat()
            
            # 输出整理报告
            self._print_organization_report(organization_report)
            
        except Exception as e:
            organization_report["errors"].append(str(e))
            print(f"[BackgroundOrganizer] 后台整理任务异常: {e}")
        
        return organization_report
    
    def _migrate_low_frequency_memories(self) -> Dict:
        """迁移低频记忆（L2降级到L3）"""
        
        migration_report = {
            "migrated_count": 0,
            "migrated_memories": []
        }
        
        try:
            # 获取所有记忆
            all_memories = self._get_all_memories()
            
            # 分析记忆访问频率
            low_frequency_memories = []
            cutoff_date = datetime.now() - timedelta(days=self.organizer_settings["migration_threshold_days"])
            
            for memory in all_memories:
                # 检查记忆层级和最后访问时间
                if memory.get("importance") == "L2":  # 情景记忆
                    last_accessed = self._get_memory_last_accessed(memory)
                    
                    if last_accessed and last_accessed < cutoff_date:
                        low_frequency_memories.append(memory)
            
            # 执行迁移
            for memory in low_frequency_memories:
                if self._migrate_memory_to_l3(memory):
                    migration_report["migrated_count"] += 1
                    migration_report["migrated_memories"].append(memory.get("title", ""))
            
            if migration_report["migrated_count"] > 0:
                print(f"[BackgroundOrganizer] 已迁移{migration_report['migrated_count']}条低频记忆到L3")
            
        except Exception as e:
            print(f"[BackgroundOrganizer] 记忆迁移失败: {e}")
        
        return migration_report
    
    def _get_all_memories(self) -> List[Dict]:
        """获取所有记忆（简化实现）"""
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
                        "timestamp": lines[0].split(" - ")[0] if " - " in lines[0] else "",
                        "title": lines[0].split(" - ")[1] if " - " in lines[0] else lines[0],
                        "user_input": lines[2].replace("**用户**: ", "") if lines[2].startswith("**用户**: ") else "",
                        "ai_response": lines[3].replace("**AI**: ", "") if len(lines) > 3 and lines[3].startswith("**AI**: ") else "",
                        "file_path": file_path,
                        "importance": self._extract_importance(lines[0])  # 从标题提取重要性
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
            return "L3"  # 默认
    
    def _get_memory_last_accessed(self, memory: Dict) -> Optional[datetime]:
        """获取记忆最后访问时间（简化实现）"""
        # 在实际实现中，这里应该记录和读取访问时间
        # 简化实现：使用文件修改时间
        file_path = memory.get("file_path")
        if file_path and file_path.exists():
            return datetime.fromtimestamp(file_path.stat().st_mtime)
        return None
    
    def _migrate_memory_to_l3(self, memory: Dict) -> bool:
        """将记忆迁移到L3层级"""
        try:
            # 在实际实现中，这里应该修改记忆文件的层级标记
            # 简化实现：记录迁移日志
            print(f"[BackgroundOrganizer] 迁移记忆到L3: {memory.get('title', '')}")
            return True
        except Exception as e:
            print(f"[BackgroundOrganizer] 迁移失败: {e}")
            return False
    
    def _discover_memory_associations(self) -> Dict:
        """发现记忆之间的关联"""
        
        association_report = {
            "associations_count": 0,
            "discovered_associations": []
        }
        
        try:
            # 获取所有记忆
            all_memories = self._get_all_memories()
            
            # 分析记忆之间的关联
            associations = self._find_memory_associations(all_memories)
            
            for assoc in associations:
                association_report["associations_count"] += 1
                association_report["discovered_associations"].append({
                    "memory1": assoc[0].get("title", ""),
                    "memory2": assoc[1].get("title", ""),
                    "similarity": assoc[2]
                })
            
            if association_report["associations_count"] > 0:
                print(f"[BackgroundOrganizer] 发现{association_report['associations_count']}个记忆关联")
            
        except Exception as e:
            print(f"[BackgroundOrganizer] 关联发现失败: {e}")
        
        return association_report
    
    def _find_memory_associations(self, memories: List[Dict]) -> List[Tuple[Dict, Dict, float]]:
        """查找记忆之间的关联"""
        associations = []
        
        # 简单的关键词关联分析
        for i, memory1 in enumerate(memories):
            for j, memory2 in enumerate(memories[i+1:], i+1):
                similarity = self._calculate_memory_similarity(memory1, memory2)
                
                if similarity > 0.6:  # 相似度阈值
                    associations.append((memory1, memory2, similarity))
        
        # 按相似度排序
        associations.sort(key=lambda x: x[2], reverse=True)
        
        return associations[:10]  # 返回前10个最强关联
    
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
    
    def _evaluate_memory_quality(self) -> Dict:
        """评估记忆质量"""
        
        quality_report = {
            "low_quality_count": 0,
            "evaluated_memories": 0,
            "low_quality_list": []
        }
        
        try:
            # 获取旧记忆
            cutoff_date = datetime.now() - timedelta(days=self.organizer_settings["quality_evaluation_days"])
            old_memories = []
            
            all_memories = self._get_all_memories()
            for memory in all_memories:
                last_accessed = self._get_memory_last_accessed(memory)
                if last_accessed and last_accessed < cutoff_date:
                    old_memories.append(memory)
            
            quality_report["evaluated_memories"] = len(old_memories)
            
            # 评估每个记忆的质量
            for memory in old_memories:
                quality_score = self._calculate_memory_quality(memory)
                
                if quality_score < self.organizer_settings["low_quality_threshold"]:
                    quality_report["low_quality_count"] += 1
                    quality_report["low_quality_list"].append({
                        "title": memory.get("title", ""),
                        "quality_score": quality_score
                    })
            
            if quality_report["low_quality_count"] > 0:
                print(f"[BackgroundOrganizer] 发现{quality_report['low_quality_count']}条低质量记忆")
            
        except Exception as e:
            print(f"[BackgroundOrganizer] 质量评估失败: {e}")
        
        return quality_report
    
    def _calculate_memory_quality(self, memory: Dict) -> float:
        """计算记忆质量评分（0-1）"""
        score = 0.5  # 基础分
        
        # 基于内容长度的评分
        content_length = len(memory.get("user_input", "")) + len(memory.get("ai_response", ""))
        if content_length > 200:
            score += 0.2
        elif content_length < 50:
            score -= 0.2
        
        # 基于重要性的评分
        importance = memory.get("importance", "L3")
        if importance == "L1":
            score += 0.3
        elif importance == "L2":
            score += 0.1
        
        # 基于关键词的评分
        important_keywords = ["记住", "重要", "关键", "决定", "选择", "功能", "实现"]
        text = f"{memory.get('user_input', '')} {memory.get('ai_response', '')}"
        
        for keyword in important_keywords:
            if keyword in text:
                score += 0.1
                break
        
        return min(1.0, max(0.0, score))  # 确保在0-1之间
    
    def _print_organization_report(self, report: Dict):
        """输出整理报告"""
        print("\n[BackgroundOrganizer] 后台整理报告")
        print("=" * 50)
        print(f"完成时间: {report.get('completed_at', 'N/A')}")
        print(f"完成任务: {report.get('tasks_completed', 0)}/3")
        print(f"记忆迁移: {report.get('memory_migrations', 0)}条")
        print(f"关联发现: {report.get('associations_discovered', 0)}个")
        print(f"低质量记忆: {report.get('low_quality_memories', 0)}条")
        
        if report.get("errors"):
            print(f"错误数量: {len(report['errors'])}")
        
        print("=" * 50)


def test_background_organizer():
    """测试后台整理器功能"""
    
    config = {
        "background_organizer": {
            "idle_threshold_minutes": 1,  # 测试用1分钟
            "migration_threshold_days": 1,
            "quality_evaluation_days": 1,
            "low_quality_threshold": 0.3,
            "association_discovery_enabled": True,
            "max_background_time_minutes": 2
        }
    }
    
    organizer = BackgroundOrganizer(config)
    
    # 测试记忆迁移
    migration_result = organizer._migrate_low_frequency_memories()
    print(f"记忆迁移测试: {migration_result['migrated_count']}条")
    
    # 测试关联发现
    association_result = organizer._discover_memory_associations()
    print(f"关联发现测试: {association_result['associations_count']}个")
    
    # 测试质量评估
    quality_result = organizer._evaluate_memory_quality()
    print(f"质量评估测试: {quality_result['low_quality_count']}条低质量")
    
    print("✅ 后台整理器功能测试完成")


if __name__ == "__main__":
    test_background_organizer()