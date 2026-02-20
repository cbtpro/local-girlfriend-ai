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

## 快速启动（一键运行）

```shell
chmod +x start.sh
./start.sh
```

## 使用说明

### 首次运行

```shell
# 1. 启动 Ollama（保持后台运行）
ollama serve &

# 2. 运行虚拟女友
python main.py
```

### 自定义女友

修改 config.yaml：

```yml
girlfriend:
  name: "雨晴"              # 改名字
  personality: "高冷气质、学霸、有点傲娇"  # 改性格
  likes: ["数学", "弹钢琴", "看书"]  # 改爱好
```

### 启用语音输入（用话筒说话）

```shell
pip install sounddevice scipy
```

## 有哪些声音可选

输入下面命令可以列举声音，选择你喜欢的声音

```shell
edge-tts --list-voices
```

## 有哪些模型可以用？

基本上，支持 Ollama 所有的的模型都可以使用，通过ollama进行安装后，config 中进行配置。

## 技能如何调整

请在config.yml中进行微调

## 性格如何微调

修改 system_prompt：

```text
gf = VirtualGirlfriend(name="小冰")
gf.system_prompt = """你的名字是小冰，性格特点：聪慧、独立、有主见、略有傲娇
你是用户的虚拟女友，应该：
..."""
```

但性格和技能是要和模型搭配的，如果模型不支持，则配置无效。

## 对话太慢怎么办？

换更小的模型：

## 推荐配置

| 硬件 | 模型 | TTS | 体验 |
| ------ | ------ | ------ | ------ |
| M1 MacBook Air | qwen:1.8b-chat | pyttsx3 | ✅ 流畅 |
| M1 Pro | qwen:7b-chat | edge-tts | ⭐ 推荐 |
| M2/M3 | qwen:7b-chat | edge-tts | ⭐⭐ 最佳 |
