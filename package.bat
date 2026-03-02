@echo off
echo ========================================
echo IDE Memory System - VSIX 打包脚本
echo ========================================

REM 检查是否安装了 vsce
where vsce >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未安装 vsce，请先运行: npm install -g @vscode/vsce
    pause
    exit /b 1
)

REM 创建临时打包目录
if exist "package_temp" rmdir /s /q "package_temp"
mkdir "package_temp"

REM 复制必要文件到打包目录
copy "package.json" "package_temp\"
copy "extension.js" "package_temp\"
copy "memory_plugin.py" "package_temp\"
copy "storage_manager.py" "package_temp\"
copy "config.yaml" "package_temp\"
copy "README.md" "package_temp\"

REM 复制 hooks 目录
xcopy "hooks" "package_temp\hooks" /E /I /Y

REM 进入打包目录并执行打包
cd "package_temp"

REM 使用 vsce 打包
echo 正在打包 VSIX 文件...
vsce package --no-dependencies

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 打包成功！
    echo ========================================
    echo.
    echo 生成的 VSIX 文件:
    dir *.vsix
    echo.
    echo 安装方法:
    echo 1. 在 VS Code 中按 Ctrl+Shift+P
    echo 2. 输入 "Extensions: Install from VSIX"
    echo 3. 选择生成的 .vsix 文件
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 打包失败！
    echo ========================================
)

REM 返回原目录
cd ..

REM 清理临时目录
rmdir /s /q "package_temp"

pause