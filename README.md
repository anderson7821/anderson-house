# AI Memory System - 三层智能记忆插件

基于OpenClaw三层记忆架构的智能记忆系统，让AI助手拥有长期记忆能力！

## 🧠 核心功能

### 🔍 智能筛选器
- **自动识别重要信息**：检测"记住..."、"我叫..."、"项目重点是..."等关键词
- **热点话题升级**：同一话题讨论3次以上自动提升记忆层级
- **自动打标签**：根据内容自动添加[type:decision/bug/feature]标签
- **重要性评分**：给每条记忆打分（0-10分），高分自动进L1

### 🔄 智能检索器
- **话题感知检索**：检测当前话题关键词，自动检索相关记忆
- **渐进式披露**：先显示摘要，需要时再展开全文
- **记忆预热**：新会话自动加载最相关的5条记忆
- **遗忘曲线优化**：近期记忆权重高，远期记忆摘要化

### 🗜️ 智能压缩器
- **自动摘要**：每10轮对话生成200字摘要
- **原始对话压缩**：30天后原始对话打包zip
- **重复合并**：相似内容自动合并去重
- **空间预警**：当存储超过1G时提醒整理

### 🧹 后台整理器
- **闲时整理**：IDE空闲5分钟时后台整理记忆
- **记忆迁移**：低频记忆从L2降级到L3
- **关联发现**：自动发现记忆之间的关联
- **质量评估**：定期淘汰低价值记忆

### 📊 可视化面板
- **记忆面板**：侧边栏显示最近记忆和热点
- **搜索界面**：可视化搜索和过滤
- **图谱视图**：记忆关联网络图
- **手动编辑**：直接修改/删除记忆

## 🚀 快速开始

### 安装方法

1. 下载VSIX文件：`ide-memory-system-anderson-1.0.0.vsix`
2. 在VS Code/Cursor中执行：
   ```bash
   code --install-extension ide-memory-system-anderson-1.0.0.vsix
   ```
3. 重启IDE

### 使用方法

#### 基本命令
- `Ctrl+Shift+P` → 输入"Memory System"查看可用命令
- `/memory list` - 列出最近记忆
- `/memory search <关键词>` - 搜索记忆
- `/memory panel` - 打开记忆面板

#### 自动功能
- 插件自动启动，无需手动配置
- 对话自动记录到`.memory/YYYY-MM-DD.md`
- 新会话自动注入最近1天的记录

## 📁 文件结构

```
.memory/                          # 项目级记忆存储
├── 2026-03-02.md                 # 每日记忆文件
├── welcome.md                    # 欢迎记忆
└── config.yaml                   # 配置文件

~/.ide-memory/                    # 用户级记忆存储
├── l3_memories/                  # L3长期记忆
├── user_config.yaml              # 用户配置
└── logs/                         # 系统日志
```

## ⚙️ 配置选项

在VS Code设置中搜索"Memory System"进行配置：

- `memorySystem.enabled` - 启用/禁用记忆系统
- `memorySystem.storagePaths.project` - 项目级存储路径
- `memorySystem.storagePaths.user` - 用户级存储路径

## 🎯 三层记忆架构

### L1 - 长期记忆
- 重要决策、关键信息、用户偏好
- 自动识别关键词存入
- 永久保存，不会被自动清理

### L2 - 情景记忆  
- 近期对话、项目上下文、工作状态
- 自动摘要化存储
- 定期压缩，保留精华

### L3 - 会话记忆
- 当前对话、临时信息、缓存数据
- 原始对话存储
- 自动清理，释放空间

## 🔧 技术特性

- **轻量级设计**：基于Markdown的透明存储
- **智能算法**：结合遗忘曲线和重要性评分
- **多窗口同步**：支持多IDE窗口记忆共享
- **账号切换保护**：账号切换时记忆自动保护
- **安全可靠**：路径验证和防误删机制

## 📈 性能指标

- **启动时间**：< 500ms
- **内存占用**：< 50MB
- **存储效率**：压缩率 > 80%
- **检索速度**：平均 < 100ms

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 💖 支持项目

如果这个插件对你有帮助，请考虑支持我们的开发工作！

### ☕ Buy Me a Coffee

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support%20the%20Project-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://buymeacoffee.com/andersonmemory)

### 💰 GitHub Sponsors

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Support%20Open%20Source-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/anderson-memory-tech)

### 🏢 企业定制服务

需要企业级定制功能？联系我们提供专业服务！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 联系我们

- 官网：https://anderson-memory.tech
- 邮箱：contact@anderson-memory.tech
- GitHub：https://github.com/anderson-memory-tech/ide-memory-system
- Buy Me a Coffee：https://buymeacoffee.com/andersonmemory

---

**让AI助手真正记住你！** 🚀