import gradio as gr
import asyncio
import yaml
from girlfriend_core import GirlfriendAI
from voice_manager import VoiceManager

# =========================
# 初始化
# =========================
with open("config.yaml") as f:
    config = yaml.safe_load(f)

ai = GirlfriendAI(config)
voice = VoiceManager(config)


# =========================
# 聊天逻辑
# =========================
async def respond(message, history, use_voice):

    if history is None:
        history = []

    if not message:
        return history, "", gr.update(visible=False)

    # 加入用户消息（Gradio 6 默认就是 messages 格式）
    history.append({"role": "user", "content": message})

    # 防止模型阻塞
    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(None, ai.chat, message)

    history.append({"role": "assistant", "content": reply})

    if use_voice:
        audio_path = await voice.text_to_speech(reply)
        return history, "", gr.update(value=audio_path, visible=True)
    else:
        return history, "", gr.update(value=None, visible=False)


# =========================
# UI
# =========================
with gr.Blocks() as demo:

    gr.Markdown("# 💕 本地虚拟女友 AI")

    chatbot = gr.Chatbot(height=500)  # 不再写 type

    with gr.Row():
        msg = gr.Textbox(
            placeholder="对她说点什么吧...",
            scale=4,
            show_label=False
        )
        send_btn = gr.Button("发送", scale=1)

    use_voice = gr.Checkbox(label="启用语音回复", value=True)

    audio_output = gr.Audio(
        label="语音回复",
        type="filepath",
        visible=True
    )

    state = gr.State([])

    send_btn.click(
        respond,
        inputs=[msg, state, use_voice],
        outputs=[chatbot, msg, audio_output],
    )

    msg.submit(
        respond,
        inputs=[msg, state, use_voice],
        outputs=[chatbot, msg, audio_output],
    )

    use_voice.change(
        lambda x: gr.update(visible=x),
        inputs=use_voice,
        outputs=audio_output
    )


if __name__ == "__main__":
    demo.launch(
        share=False,
        theme=gr.themes.Soft()  # ← theme 移到这里
    )