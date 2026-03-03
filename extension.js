const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let memoryPlugin = null;

function activate(context) {
    console.log('IDE Memory System extension is now active!');
    
    // 初始化记忆系统
    initializeMemorySystem();
    
    // 注册命令
    let disposableShowPanel = vscode.commands.registerCommand('memory-system.showMemoryPanel', () => {
        showMemoryPanel();
    });
    
    let disposableListMemories = vscode.commands.registerCommand('memory-system.listRecentMemories', () => {
        listRecentMemories();
    });
    
    let disposableShowStats = vscode.commands.registerCommand('memory-system.showStats', () => {
        showMemoryStats();
    });
    
    // 注册事件监听
    context.subscriptions.push(
        disposableShowPanel,
        disposableListMemories,
        disposableShowStats
    );
    
    // 会话开始时的记忆注入
    injectRecentMemoriesOnStartup();
    
    // 监听编辑器变化（用户输入）
    vscode.workspace.onDidChangeTextDocument((event) => {
        handleUserInput(event);
    });
    
    // 监听窗口关闭（会话结束）
    vscode.window.onDidCloseTerminal(() => {
        handleSessionEnd();
    });
}

function deactivate() {
    console.log('IDE Memory System extension is now deactivated!');
    if (memoryPlugin) {
        memoryPlugin.on_session_end();
    }
}

function initializeMemorySystem() {
    try {
        // 使用正确的扩展ID获取扩展路径
        const extension = vscode.extensions.getExtension('anderson-memory-tech.ide-memory-system-anderson');
        if (!extension) {
            throw new Error('Extension not found. Please install the extension properly.');
        }
        
        const extensionPath = extension.extensionPath;
        const pluginPath = path.join(extensionPath, 'memory_plugin.py');
        const configPath = path.join(extensionPath, 'config.yaml');
        
        console.log('Extension path:', extensionPath);
        
        // 检查Python环境
        checkPythonEnvironment();
        
        // 执行会话开始钩子
        executeSessionStartHook(extensionPath);
        
        console.log('Memory System initialized successfully');
        
    } catch (error) {
        console.error('Failed to initialize Memory System:', error);
        vscode.window.showErrorMessage('Memory System initialization failed: ' + error.message);
    }
}

function checkPythonEnvironment() {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ['--version']);
        
        pythonProcess.stdout.on('data', (data) => {
            console.log('Python version:', data.toString());
            resolve(true);
        });
        
        pythonProcess.stderr.on('data', (data) => {
            console.error('Python check error:', data.toString());
            reject(new Error('Python not found or not in PATH'));
        });
        
        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error('Python check failed with code: ' + code));
            }
        });
    });
}

function executeSessionStartHook(extensionPath) {
    const hookPath = path.join(extensionPath, 'hooks', 'session_start.sh');
    
    if (fs.existsSync(hookPath)) {
        const hookProcess = spawn('bash', [hookPath], {
            cwd: vscode.workspace.rootPath
        });
        
        hookProcess.stdout.on('data', (data) => {
            const output = data.toString();
            if (output.includes('MEMORY_CONTEXT_START')) {
                const context = extractMemoryContext(output);
                console.log('Memory context injected on session start');
            }
        });
        
        hookProcess.stderr.on('data', (data) => {
            console.error('Session start hook error:', data.toString());
        });
    }
}

function extractMemoryContext(output) {
    const startMarker = 'MEMORY_CONTEXT_START';
    const endMarker = 'MEMORY_CONTEXT_END';
    
    const startIndex = output.indexOf(startMarker) + startMarker.length;
    const endIndex = output.indexOf(endMarker);
    
    if (startIndex > -1 && endIndex > -1) {
        return output.substring(startIndex, endIndex).trim();
    }
    
    return '';
}

function injectRecentMemoriesOnStartup() {
    // 在启动时注入最近记忆到活动编辑器
    setTimeout(() => {
        if (vscode.window.activeTextEditor) {
            const memories = getRecentMemories(1);
            if (memories.length > 0) {
                showMemoryInPanel(memories);
            }
        }
    }, 2000); // 延迟2秒确保编辑器加载完成
}

function handleUserInput(event) {
    // 只有当内容变化且不是由扩展引起时才记录
    if (event.contentChanges.length > 0 && !event.reason) {
        const userInput = event.contentChanges[0].text;
        
        // 过滤掉无意义的输入（如单个字符）
        if (userInput.trim().length > 3) {
            saveUserInput(userInput);
        }
    }
}

function saveUserInput(userInput) {
    const extension = vscode.extensions.getExtension('anderson-memory-tech.ide-memory-system-anderson');
    if (!extension) return;
    
    const extensionPath = extension.extensionPath;
    const hookPath = path.join(extensionPath, 'hooks', 'user_input.sh');
    
    if (fs.existsSync(hookPath)) {
        // 模拟AI响应（实际使用时需要集成AI）
        const aiResponse = "AI response placeholder";
        const metadata = JSON.stringify({
            type: 'code_edit',
            topic: 'development',
            file: vscode.window.activeTextEditor?.document.fileName || ''
        });
        
        const hookProcess = spawn('bash', [hookPath, userInput, aiResponse, metadata], {
            cwd: vscode.workspace.rootPath
        });
        
        hookProcess.stdout.on('data', (data) => {
            console.log('User input saved:', data.toString());
        });
        
        hookProcess.stderr.on('data', (data) => {
            console.error('User input hook error:', data.toString());
        });
    }
}

function handleSessionEnd() {
    const extension = vscode.extensions.getExtension('anderson-memory-tech.ide-memory-system-anderson');
    if (!extension) return;
    
    const extensionPath = extension.extensionPath;
    const hookPath = path.join(extensionPath, 'hooks', 'session_end.sh');
    
    if (fs.existsSync(hookPath)) {
        const hookProcess = spawn('bash', [hookPath], {
            cwd: vscode.workspace.rootPath
        });
        
        hookProcess.stdout.on('data', (data) => {
            console.log('Session end processed:', data.toString());
        });
        
        hookProcess.stderr.on('data', (data) => {
            console.error('Session end hook error:', data.toString());
        });
    }
}

function showMemoryPanel() {
    // 创建并显示记忆面板
    const panel = vscode.window.createWebviewPanel(
        'memoryPanel',
        'Memory System',
        vscode.ViewColumn.Beside,
        {
            enableScripts: true
        }
    );
    
    const memories = getRecentMemories(3);
    panel.webview.html = getMemoryPanelHtml(memories);
}

function listRecentMemories() {
    const memories = getRecentMemories(1);
    
    if (memories.length === 0) {
        vscode.window.showInformationMessage('No recent memories found.');
        return;
    }
    
    const memoryList = memories.map(memory => 
        `- ${memory.timestamp}: ${memory.title}`
    ).join('\n');
    
    vscode.window.showInformationMessage(`Recent Memories:\n${memoryList}`);
}

function showMemoryStats() {
    const stats = getMemoryStats();
    
    const statsMessage = `Memory System Stats:
📊 Total Memories: ${stats.totalMemories}
📅 Recent 7 Days: ${stats.recent7Days}
📁 Memory Files: ${stats.memoryFiles}`;
    
    vscode.window.showInformationMessage(statsMessage);
}

function getRecentMemories(days) {
    // 简化实现 - 实际应该调用Python插件
    try {
        const workspacePath = vscode.workspace.rootPath;
        const memoryPath = path.join(workspacePath, '.memory');
        
        if (!fs.existsSync(memoryPath)) {
            return [];
        }
        
        // 这里应该调用Python插件获取真实数据
        // 暂时返回模拟数据
        return [
            {
                timestamp: '10:30',
                title: '如何修复报告生成错误？',
                type: 'question',
                topic: 'bugfix'
            }
        ];
        
    } catch (error) {
        console.error('Error getting recent memories:', error);
        return [];
    }
}

function getMemoryStats() {
    // 简化实现
    return {
        totalMemories: 15,
        recent7Days: 8,
        memoryFiles: 3
    };
}

function getMemoryPanelHtml(memories) {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    font-family: var(--vscode-font-family); 
                    padding: 20px; 
                    background: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                }
                .memory-item { 
                    border-left: 3px solid var(--vscode-button-background);
                    padding: 10px; 
                    margin: 10px 0; 
                    background: var(--vscode-input-background);
                }
                .timestamp { 
                    color: var(--vscode-descriptionForeground); 
                    font-size: 0.9em; 
                }
            </style>
        </head>
        <body>
            <h2>🧠 Recent Memories</h2>
            ${memories.map(memory => `
                <div class="memory-item">
                    <div class="timestamp">${memory.timestamp}</div>
                    <strong>${memory.title}</strong>
                    <div>[${memory.type}] [${memory.topic}]</div>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function showMemoryInPanel(memories) {
    // 在侧边栏显示记忆信息
    const memoryContent = memories.map(memory => 
        `**${memory.timestamp}** - ${memory.title}`
    ).join('\n');
    
    vscode.window.showInformationMessage(`Recent Memories:\n${memoryContent}`);
}

module.exports = {
    activate,
    deactivate
};