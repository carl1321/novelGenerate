#!/bin/bash

# 小说生成智能体框架 - 启动脚本
# 支持 Docker Compose 和本地开发两种模式

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 检查 .env 文件
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env 文件不存在，正在从 env.example 创建...${NC}"
        cp env.example .env
        echo -e "${GREEN}✅ 已创建 .env 文件，请编辑配置必要的参数（至少配置 AI API Key）${NC}"
        echo -e "${YELLOW}   按 Enter 继续，或按 Ctrl+C 退出编辑 .env 文件${NC}"
        read
    fi
}

# Docker Compose 模式启动
start_docker() {
    echo -e "${GREEN}🐳 使用 Docker Compose 启动服务...${NC}"
    
    # 检查 .env 文件
    check_env
    
    # 构建并启动服务
    echo -e "${GREEN}📦 构建 Docker 镜像...${NC}"
    docker-compose build
    
    echo -e "${GREEN}🚀 启动服务...${NC}"
    docker-compose up -d
    
    # 等待服务启动
    echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
    sleep 5
    
    # 检查服务状态
    echo -e "${GREEN}📊 服务状态：${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}✅ 服务启动完成！${NC}"
    echo -e "${GREEN}📱 前端地址: http://localhost:3001${NC}"
    echo -e "${GREEN}🔧 后端API: http://localhost:8001${NC}"
    echo -e "${GREEN}📚 API文档: http://localhost:8001/docs${NC}"
    echo ""
    echo -e "${YELLOW}查看日志: docker-compose logs -f${NC}"
    echo -e "${YELLOW}停止服务: docker-compose down${NC}"
}

# 本地开发模式启动
start_local() {
    echo -e "${GREEN}💻 使用本地开发模式启动服务...${NC}"
    
    # 检查 .env 文件
    check_env
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 未安装${NC}"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装${NC}"
        exit 1
    fi
    
    # 检查 PostgreSQL
    if ! command -v psql &> /dev/null; then
        echo -e "${YELLOW}⚠️  PostgreSQL 客户端未安装，无法检查数据库连接${NC}"
    fi
    
    # 启动后端
    echo -e "${GREEN}🔧 启动后端服务...${NC}"
    cd backend
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}创建 Python 虚拟环境...${NC}"
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -r requirements.txt
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
    BACKEND_PID=$!
    cd ..
    
    # 等待后端启动
    sleep 3
    
    # 启动前端
    echo -e "${GREEN}🎨 启动前端服务...${NC}"
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装前端依赖...${NC}"
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo -e "${GREEN}✅ 服务启动完成！${NC}"
    echo -e "${GREEN}📱 前端地址: http://localhost:3001${NC}"
    echo -e "${GREEN}🔧 后端API: http://localhost:8001${NC}"
    echo -e "${GREEN}📚 API文档: http://localhost:8001/docs${NC}"
    echo ""
    echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
    
    # 等待中断信号
    trap "echo -e '\n${YELLOW}🛑 正在停止服务...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
    wait
}

# 主函数
main() {
    echo -e "${GREEN}🚀 小说生成智能体框架 - 启动脚本${NC}"
    echo ""
    
    # 检查参数
    if [ "$1" == "docker" ] || [ "$1" == "d" ]; then
        if check_docker; then
            start_docker
        else
            echo -e "${RED}❌ Docker 或 Docker Compose 未安装${NC}"
            echo -e "${YELLOW}请安装 Docker 和 Docker Compose，或使用本地开发模式: ./start.sh local${NC}"
            exit 1
        fi
    elif [ "$1" == "local" ] || [ "$1" == "l" ]; then
        start_local
    else
        # 自动选择模式
        if check_docker; then
            echo -e "${YELLOW}检测到 Docker，使用 Docker Compose 模式${NC}"
            echo -e "${YELLOW}如需使用本地开发模式，请运行: ./start.sh local${NC}"
            echo ""
            start_docker
        else
            echo -e "${YELLOW}未检测到 Docker，使用本地开发模式${NC}"
            echo ""
            start_local
        fi
    fi
}

# 运行主函数
main "$@"

