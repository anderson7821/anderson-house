# 🧠 IDE三层记忆系统 - 完整安装指南

## 📦 快速安装（推荐）

### 方法1：使用VSIX文件安装（最简单）

1. **下载VSIX文件**
   ```bash
   # 运行打包脚本生成VSIX文件
   cd .plugins/memory_system/
   package.bat
   ```

2. **在VS Code中安装**
   - 打开VS Code
   - 按 `Ctrl+Shift+P` (Windows) 或 `Cmd+Shift+P` (Mac)
   - 输入 "Extensions: Install from VSIX"
   - 选择生成的 `.vsix` 文件
   - 重启VS Code

3. **验证安装**
   - 按 `Ctrl+Shift+P`
   - 输入 "记忆系统" 查看可用命令
   - 应该看到三个命令：
     - `显示记忆面板`
     - `查看最近记忆`  
     - `显示统计信息`

### 方法2：手动安装（开发模式）

1. **复制插件文件**
   ```bash
   # 将插件复制到VS Code扩展目录
   cp -r .plugins/memory_system/ ~/.vscode/extensions/ide-memory-system/
   ```

2. **重启VS Code**
   ```bash
   # 完全关闭后重新打开VS Code
   code --disable-extensions
   code
   ```

## 🔧 环境要求

### 必需环境
- ✅ **VS Code 1.60+** 或 **Cursor 1.0+**
- ✅ **Python 3.8+**（必须添加到PATH）
- ✅ **Bash环境**（Windows需要Git Bash或WSL）

### 验证环境
```bash
# 检查Python
python --version
# 应该显示: Python 3.x.x

# 检查Bash
bash --version
# 应该显示Bash版本信息
```

## ⚙️ 配置说明

### 默认配置（开箱即用）
插件安装后使用默认配置即可工作：

```yaml
# 存储路径（自动创建）
项目记忆: .memory/           # 项目级存储
用户配置: ~/.ide-memory/     # 用户级存储

# 功能配置
自动记忆注入: 启用
记忆保留天数: 7天
每日最大记忆: 100条
```

### 自定义配置
如需自定义，创建 `~/.ide-memory/config.yaml`：

```yaml
storage_paths:
  project: ".my-memory/"           # 自定义项目路径
  user: "~/.my-ide-memory/"        # 自定义用户路径

auto_injection: true
retention_days: 14                  # 延长到14天
max_memories_per_day: 200          # 增加每日限制
```

## 🚀 使用指南

### 基础使用（零配置）
1. **安装后即可使用** - 插件自动记录对话
2. **新会话自动注入** - 打开新文件时自动加载最近记忆
3. **透明存储** - 记忆保存在 `.memory/` 目录，可随时查看

### 命令使用

#### 1. 显示记忆面板
```bash
# 方法1: 命令面板
Ctrl+Shift+P → "显示记忆面板"

# 方法2: 快捷键（可自定义）
Ctrl+Shift+M
```

#### 2. 查看最近记忆
```bash
# 查看最近1天记忆
Ctrl+Shift+P → "查看最近记忆"

# 在终端中直接使用
/memory list
/memory list 3    # 查看最近3天
```

#### 3. 显示统计信息
```bash
Ctrl+Shift+P → "显示统计信息"

# 终端命令
/memory stats
```

### 高级功能

#### 主动记忆召回
AI可以主动查询相关记忆：
```python
# 在AI代码中调用
memories = plugin.on_memory_recall("报告生成错误", context)
```

#### 记忆搜索
支持关键词搜索记忆：
```bash
# 搜索包含"错误"的记忆
插件会自动搜索并返回相关记忆
```

## 📁 文件结构说明

### 安装后目录结构
```
~/.vscode/extensions/ide-memory-system/
├── extension.js              # 主扩展文件
├── package.json              # 扩展配置
├── memory_plugin.py          # Python记忆插件
├── storage_manager.py        # 存储管理器
├── config.yaml              # 默认配置
├── hooks/                    # Shell钩子
│   ├── session_start.sh     # 会话开始
│   ├── user_input.sh        # 用户输入
│   └── session_end.sh       # 会话结束
└── README.md                # 使用说明
```

### 记忆存储结构
```
项目根目录/
└── .memory/                  # 项目记忆目录（自动创建）
    ├── 2026-03-02.md        # 今日记忆文件
    ├── 2026-03-01.md        # 昨日记忆文件
    ├── WELCOME.md           # 欢迎文件
    └── config.yaml          # 项目配置（可选）

用户主目录/
└── .ide-memory/             # 用户记忆目录（自动创建）
    ├── config.yaml          # 用户配置
    └── sessions/             # 会话日志（未来功能）
```

## 🎯 功能验证

### 安装后验证步骤

1. **检查扩展是否加载**
   ```bash
   # 在VS Code终端中
   code --list-extensions | grep memory
   # 应该显示: memory-system-team.ide-memory-system
   ```

2. **检查记忆目录是否创建**
   ```bash
   # 在项目根目录
   ls -la .memory/
   # 应该看到今日的记忆文件
   ```

3. **测试基本功能**
   ```bash
   # 在VS Code命令面板中测试
   Ctrl+Shift+P → "查看最近记忆"
   # 应该显示记忆列表或"没有记忆记录"
   ```

4. **验证记忆记录**
   - 在编辑器中输入一些代码或注释
   - 等待几秒钟
   - 检查 `.memory/今日日期.md` 文件
   - 应该看到记录的内容

## 🐛 故障排除

### 常见问题

#### Q: 扩展安装后不工作？
A: 检查Python环境：
```bash
python --version
# 确保Python 3.8+可用
```

#### Q: 记忆文件没有生成？
A: 检查目录权限：
```bash
# 在项目根目录
ls -la
# 确保有写入权限
```

#### Q: Shell钩子执行失败？
A: Windows用户需要安装Git Bash：
```bash
# 安装Git for Windows
# 或使用WSL环境
```

#### Q: 命令不显示？
A: 重启VS Code：
```bash
# 完全关闭后重新打开
code --disable-extensions
code
```

### 日志调试

启用详细日志：
```json
// 在VS Code设置中
{
    "memorySystem.debug": true,
    "memorySystem.logLevel": "DEBUG"
}
```

查看扩展日志：
```bash
# 在VS Code中
Ctrl+Shift+P → "Developer: Open Extension Logs"
```

## 🔄 更新与卸载

### 更新插件
```bash
# 方法1: 重新安装VSIX文件
# 方法2: 通过扩展市场更新（未来）
```

### 卸载插件
```bash
# 方法1: VS Code扩展面板卸载
# 方法2: 手动删除目录
rm -rf ~/.vscode/extensions/ide-memory-system/
```

### 数据备份
卸载前备份记忆数据：
```bash
# 备份项目记忆
cp -r .memory/ ~/backup/memory-backup/

# 备份用户配置
cp -r ~/.ide-memory/ ~/backup/user-config/
```

## 💡 使用技巧

### 最佳实践
1. **定期查看记忆** - 使用 `/memory list` 回顾项目进展
2. **利用记忆注入** - 新会话时AI会自动了解项目背景
3. **手动添加重要信息** - 直接编辑 `.memory/` 文件添加关键信息

### 性能优化
- 记忆文件自动按日期分割
- 旧文件自动归档（保留7天）
- 支持记忆压缩（未来版本）

### 团队协作
- 项目记忆可版本控制（建议添加到 `.gitignore`）
- 用户配置个人化，不共享敏感信息

## 📞 支持与反馈

### 获取帮助
- 📖 查看详细文档：`README.md`
- 🐛 报告问题：GitHub Issues
- 💬 社区讨论：官方论坛

### 联系开发团队
- 📧 邮箱：memory-system@example.com
- 🌐 网站：https://memory-system.example.com
- 🐙 GitHub：https://github.com/your-repo/ide-memory-system

---

**🎉 恭喜！您已成功安装IDE三层记忆系统插件！**

现在开始享受智能记忆带来的高效开发体验吧！