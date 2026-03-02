@echo off
REM Open VSX 发布脚本 (Windows版本)
REM 用于将插件发布到 Open VSX Registry

setlocal enabledelayedexpansion

REM 配置信息
set EXTENSION_NAME=ide-memory-system-anderson
set VERSION=1.0.0
set PUBLISHER=anderson-memory-tech
set VSIX_FILE=%EXTENSION_NAME%-%VERSION%.vsix

REM 颜色定义（Windows CMD不支持ANSI颜色，使用文字标识）
set RED=[ERROR]
set GREEN=[SUCCESS]
set YELLOW=[WARNING]
set BLUE=[INFO]

REM 日志函数
:log_info
echo %BLUE% %*
goto :eof

:log_success
echo %GREEN% %*
goto :eof

:log_warning
echo %YELLOW% %*
goto :eof

:log_error
echo %RED% %*
goto :eof

REM 检查前置条件
:check_prerequisites
call :log_info "检查前置条件..."

REM 检查 ovsx 命令是否安装
ovsx --version >nul 2>&1
if errorlevel 1 (
    call :log_error "ovsx 命令未安装，请先安装：npm install -g ovsx"
    exit /b 1
)

REM 检查 VSIX 文件是否存在
if not exist "%VSIX_FILE%" (
    call :log_error "VSIX 文件不存在: %VSIX_FILE%"
    call :log_info "请先执行: vsce package"
    exit /b 1
)

REM 检查是否已登录
ovsx whoami >nul 2>&1
if errorlevel 1 (
    call :log_warning "未登录到 Open VSX，需要先登录"
    call :log_info "请执行: ovsx login"
    call :log_info "或者设置环境变量: OVSX_PAT=your_personal_access_token"
    exit /b 1
)

call :log_success "前置条件检查通过"
goto :eof

REM 验证插件信息
:validate_extension
call :log_info "验证插件信息..."

REM 检查 package.json 中的关键字段
if not exist "package.json" (
    call :log_error "package.json 文件不存在"
    exit /b 1
)

REM 使用 PowerShell 解析 JSON（Windows 兼容方案）
for /f "usebackq tokens=*" %%i in (`powershell -Command "(Get-Content package.json ^| ConvertFrom-Json).name"`) do set name=%%i
for /f "usebackq tokens=*" %%i in (`powershell -Command "(Get-Content package.json ^| ConvertFrom-Json).version"`) do set version=%%i
for /f "usebackq tokens=*" %%i in (`powershell -Command "(Get-Content package.json ^| ConvertFrom-Json).publisher"`) do set publisher=%%i

if not "%name%"=="%EXTENSION_NAME%" (
    call :log_error "插件名称不匹配: 期望 %EXTENSION_NAME%，实际 %name%"
    exit /b 1
)

if not "%version%"=="%VERSION%" (
    call :log_error "版本号不匹配: 期望 %VERSION%，实际 %version%"
    exit /b 1
)

if not "%publisher%"=="%PUBLISHER%" (
    call :log_error "发布者不匹配: 期望 %PUBLISHER%，实际 %publisher%"
    exit /b 1
)

call :log_success "插件信息验证通过"
goto :eof

REM 检查插件是否已存在
:check_existing_extension
call :log_info "检查插件是否已存在..."

ovsx get "%PUBLISHER%.%EXTENSION_NAME%" >nul 2>&1
if not errorlevel 1 (
    call :log_warning "插件已存在: %PUBLISHER%.%EXTENSION_NAME%"
    
    REM 获取最新版本
    for /f "usebackq tokens=*" %%i in (`ovsx get "%PUBLISHER%.%EXTENSION_NAME%" 2^>nul ^| powershell -Command "(ConvertFrom-Json).version"`) do set latest_version=%%i
    
    if "%latest_version%"=="%VERSION%" (
        call :log_error "版本 %VERSION% 已存在，请更新版本号"
        exit /b 1
    ) else (
        call :log_info "当前最新版本: %latest_version%"
        call :log_info "准备发布新版本: %VERSION%"
    )
) else (
    call :log_success "插件不存在，将创建新插件"
)

goto :eof

REM 发布插件
:publish_extension
call :log_info "发布插件到 Open VSX..."

REM 发布命令
ovsx publish "%VSIX_FILE%"
if not errorlevel 1 (
    call :log_success "插件发布成功!"
    call :log_info "访问地址: https://open-vsx.org/extension/%PUBLISHER%/%EXTENSION_NAME%"
) else (
    call :log_error "插件发布失败"
    exit /b 1
)

goto :eof

REM 验证发布结果
:verify_publish
call :log_info "验证发布结果..."

REM 等待几秒钟让服务器处理
timeout /t 5 /nobreak >nul

ovsx get "%PUBLISHER%.%EXTENSION_NAME%" >nul 2>&1
if not errorlevel 1 (
    call :log_success "发布验证通过，版本 %VERSION% 已上线"
) else (
    call :log_warning "发布验证失败，可能需要等待更长时间"
)

goto :eof

REM 显示发布信息
:show_publish_info
call :log_info "=== 发布信息汇总 ==="
echo 插件名称: %EXTENSION_NAME%
echo 版本号: %VERSION%
echo 发布者: %PUBLISHER%
echo VSIX文件: %VSIX_FILE%
echo Open VSX 地址: https://open-vsx.org/extension/%PUBLISHER%/%EXTENSION_NAME%
echo GitHub 地址: https://github.com/%PUBLISHER%/%EXTENSION_NAME%
echo.
call :log_success "发布完成！"
goto :eof

REM 主函数
:main
call :log_info "开始 Open VSX 发布流程..."
echo.

call :check_prerequisites
echo.

call :validate_extension
echo.

call :check_existing_extension
echo.

call :publish_extension
echo.

call :verify_publish
echo.

call :show_publish_info
goto :eof

REM 执行主函数
call :main

endlocal