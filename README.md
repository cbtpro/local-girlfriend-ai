# Mac M2 本地女友 AI 完整部署方案

## 项目初始化

```shell
# 创建项目目录
mkdir local-girlfriend-ai
cd local-girlfriend-ai

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

## 安装所有依赖

```shell
# 安装依赖
pip install ollama edge-tts openai-whisper gradio pydantic

# Mac 可选：安装 ffmpeg (语音处理)
brew install ffmpeg
```

## 下载模型

```shell
# 在后台启动 Ollama（必须保持运行）
ollama serve &

# 下载 Qwen 模型（M2 最佳选择）
ollama pull qwen:7b-chat
```

## 项目结构

创建以下文件结构：

```text
local-girlfriend-ai/
├── venv/
├── config.yaml              # 配置文件
├── girlfriend_core.py       # 核心 AI 逻辑
├── voice_manager.py         # 语音管理
├── web_ui.py               # Web 界面（可选）
├── main.py                 # 主入口
└── data/
    └── conversations/      # 对话记录保存
└── README.md 介绍文档
```

