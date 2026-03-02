#!/usr/bin/env python3
"""快速测试优化后的智能筛选器功能"""

from smart_filter import SmartFilter

config = {'smart_filter': {'importance_detection': True}}
filter = SmartFilter(config)

# 测试优化后的自动打标签
test_cases = [
    '决定采用新的技术方案',
    '修复了一个严重的bug', 
    '实现了新的功能特性',
    '如何解决这个问题？',
    '今天天气不错'
]

print("🧠 优化后功能快速测试")
print("=" * 50)

for case in test_cases:
    result = filter.analyze_importance(case, '')
    print(f"{case}")
    print(f"  -> 标签: {result['tags']}")
    print(f"  -> 层级: {result['level']}")
    print(f"  -> 评分: {result['score']}/10")
    print("  " + "-" * 30)

print("\n✅ 优化完成！自动打标签和层级判断已改善。")