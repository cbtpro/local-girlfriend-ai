import gradio as gr
import asyncio
from girlfriend_core import GirlfriendAI
from voice_manager import VoiceManager
import yaml

# 加载配置
with open("config.yaml") as f:
    config = yaml.safe_load(f)

ai = GirlfriendAI(config)
voice = VoiceManager(config)

def chat_with_voice(message: str):
    reply = ai.chat(message)
    audio = asyncio.run(voice.text_to_speech(reply))
    return reply, audio

# 创建 Gradio 界面
interface = gr.Interface(
    fn=chat_with_voice,
    inputs=gr.Textbox(label="对她说什么", lines=3),
    outputs=[
        gr.Textbox(label="她的回复"),
        gr.Audio(label="语音回复")
    ],
    title="💕 Mac M2 本地虚拟女友 AI",
    theme="soft"
)

if __name__ == "__main__":
    interface.launch(share=False)