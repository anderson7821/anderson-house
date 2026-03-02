#!/bin/bash

# Open VSX 发布脚本
# 用于将插件发布到 Open VSX Registry

set -e

# 配置信息
EXTENSION_NAME="ide-memory-system-anderson"
VERSION="1.0.0"
PUBLISHER="anderson-memory-tech"
VSIX_FILE="${EXTENSION_NAME}-${VERSION}.vsix"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查前置条件
check_prerequisites() {
    log_info "检查前置条件..."
    
    # 检查 ovsx 命令是否安装
    if ! command -v ovsx &> /dev/null; then
        log_error "ovsx 命令未安装，请先安装：npm install -g ovsx"
        exit 1
    fi
    
    # 检查 VSIX 文件是否存在
    if [ ! -f "$VSIX_FILE" ]; then
        log_error "VSIX 文件不存在: $VSIX_FILE"
        log_info "请先执行: vsce package"
        exit 1
    fi
    
    # 检查是否已登录
    if ! ovsx whoami &> /dev/null; then
        log_warning "未登录到 Open VSX，需要先登录"
        log_info "请执行: ovsx login"
        log_info "或者设置环境变量: OVSX_PAT=your_personal_access_token"
        exit 1
    fi
    
    log_success "前置条件检查通过"
}

# 验证插件信息
validate_extension() {
    log_info "验证插件信息..."
    
    # 检查 package.json 中的关键字段
    if [ ! -f "package.json" ]; then
        log_error "package.json 文件不存在"
        exit 1
    fi
    
    # 验证必要字段
    local name=$(jq -r '.name' package.json)
    local version=$(jq -r '.version' package.json)
    local publisher=$(jq -r '.publisher' package.json)
    
    if [ "$name" != "$EXTENSION_NAME" ]; then
        log_error "插件名称不匹配: 期望 $EXTENSION_NAME，实际 $name"
        exit 1
    fi
    
    if [ "$version" != "$VERSION" ]; then
        log_error "版本号不匹配: 期望 $VERSION，实际 $version"
        exit 1
    fi
    
    if [ "$publisher" != "$PUBLISHER" ]; then
        log_error "发布者不匹配: 期望 $PUBLISHER，实际 $publisher"
        exit 1
    fi
    
    log_success "插件信息验证通过"
}

# 检查插件是否已存在
check_existing_extension() {
    log_info "检查插件是否已存在..."
    
    if ovsx get "$PUBLISHER.$EXTENSION_NAME" &> /dev/null; then
        log_warning "插件已存在: $PUBLISHER.$EXTENSION_NAME"
        
        # 获取最新版本
        local latest_version=$(ovsx get "$PUBLISHER.$EXTENSION_NAME" | jq -r '.version')
        
        if [ "$latest_version" == "$VERSION" ]; then
            log_error "版本 $VERSION 已存在，请更新版本号"
            exit 1
        else
            log_info "当前最新版本: $latest_version"
            log_info "准备发布新版本: $VERSION"
        fi
    else
        log_success "插件不存在，将创建新插件"
    fi
}

# 发布插件
publish_extension() {
    log_info "发布插件到 Open VSX..."
    
    # 发布命令
    if ovsx publish "$VSIX_FILE"; then
        log_success "插件发布成功!"
        log_info "访问地址: https://open-vsx.org/extension/$PUBLISHER/$EXTENSION_NAME"
    else
        log_error "插件发布失败"
        exit 1
    fi
}

# 验证发布结果
verify_publish() {
    log_info "验证发布结果..."
    
    # 等待几秒钟让服务器处理
    sleep 5
    
    if ovsx get "$PUBLISHER.$EXTENSION_NAME" | jq -e ".version == \"$VERSION\"" &> /dev/null; then
        log_success "发布验证通过，版本 $VERSION 已上线"
    else
        log_warning "发布验证失败，可能需要等待更长时间"
    fi
}

# 显示发布信息
show_publish_info() {
    log_info "=== 发布信息汇总 ==="
    echo "插件名称: $EXTENSION_NAME"
    echo "版本号: $VERSION"
    echo "发布者: $PUBLISHER"
    echo "VSIX文件: $VSIX_FILE"
    echo "Open VSX 地址: https://open-vsx.org/extension/$PUBLISHER/$EXTENSION_NAME"
    echo "GitHub 地址: https://github.com/$PUBLISHER/$EXTENSION_NAME"
    echo ""
    log_success "发布完成！"
}

# 主函数
main() {
    log_info "开始 Open VSX 发布流程..."
    echo ""
    
    check_prerequisites
    echo ""
    
    validate_extension
    echo ""
    
    check_existing_extension
    echo ""
    
    publish_extension
    echo ""
    
    verify_publish
    echo ""
    
    show_publish_info
}

# 执行主函数
main "$@"