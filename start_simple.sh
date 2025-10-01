#!/bin/bash

# 小说生成系统启动脚本（简化版）

echo "🚀 启动小说生成系统..."

# 设置环境变量
export PYTHONPATH="/Users/carl/workspace/tools/novelGenerate/backend:$PYTHONPATH"
PYTHON_CMD="/opt/miniconda3/bin/python"

# 检查Python环境
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python命令未找到: $PYTHON_CMD"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

# 检查npm环境
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装npm"
    exit 1
fi

# 停止现有进程
echo "🛑 停止现有进程..."
pkill -f "api_server.py" || true
pkill -f "vite" || true
sleep 2

# 启动后端API服务器
echo "🔧 启动后端API服务器..."
cd /Users/carl/workspace/tools/novelGenerate/backend
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 5

# 检查后端是否启动成功
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ 后端启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ 后端启动成功"

# 启动前端开发服务器
echo "🎨 启动前端开发服务器..."
cd /Users/carl/workspace/tools/novelGenerate/frontend
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 3

echo "✅ 系统启动完成！"
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
