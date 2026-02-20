#!/bin/bash

# 检查 Ollama 是否运行
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 启动 Ollama 服务..."
    ollama serve &
    sleep 3
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
pip install -q ollama edge-tts openai-whisper gradio pydantic pyyaml

# 运行程序
echo "💕 启动虚拟女友 AI..."
python main.py