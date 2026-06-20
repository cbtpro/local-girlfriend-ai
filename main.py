import asyncio
import yaml
import argparse
import gradio as gr
from girlfriend_core import GirlfriendAI
from voice_manager import VoiceManager


class LocalGirlfriend:
    """本地虚拟女友核心封装"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.ai = GirlfriendAI(self.config)
        self.voice = VoiceManager(self.config)

    # =========================
    # CLI 模式
    # =========================
    async def run_cli(self):
        print("\n💕 本地虚拟女友 AI 启动成功\n")

        voice_enabled = True

        while True:
            try:
                user_input = input("\n💬 你: ").strip()

                if user_input.lower() in ['exit', 'quit', '再见']:
                    print("\n💕 下次见呀宝贝~")
                    break

                print("\n⏳ 思考中...")
                reply = self.ai.chat(user_input)
                print(f"\n🤖 {reply}")

                if voice_enabled:
                    audio_path = await self.voice.text_to_speech(reply)
                    if audio_path:
                        self.voice.play_audio(audio_path)

            except KeyboardInterrupt:
                break

    # =========================
    # Web 模式
    # =========================
    async def respond(self, message, history, use_voice):

        if history is None:
            history = []

        if not message:
            return history, "", gr.update(visible=False)

        history.append({"role": "user", "content": message})

        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(None, self.ai.chat, message)

        history.append({"role": "assistant", "content": reply})

        if use_voice:
            audio_path = await self.voice.text_to_speech(reply)
            return history, "", gr.update(value=audio_path, visible=True)
        else:
            return history, "", gr.update(value=None, visible=False)

    def run_web(self):
        with gr.Blocks() as demo:

            gr.Markdown("# 💕 本地虚拟女友 AI")

            chatbot = gr.Chatbot(height=500)

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
                self.respond,
                inputs=[msg, state, use_voice],
                outputs=[chatbot, msg, audio_output],
            )

            msg.submit(
                self.respond,
                inputs=[msg, state, use_voice],
                outputs=[chatbot, msg, audio_output],
            )

            use_voice.change(
                lambda x: gr.update(visible=x),
                inputs=use_voice,
                outputs=audio_output
            )

        demo.launch(
            share=False,
            theme=gr.themes.Soft()
        )


# =========================
# 启动入口
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="使用终端模式")
    args = parser.parse_args()

    app = LocalGirlfriend("config.yaml")

    if args.cli:
        asyncio.run(app.run_cli())
    else:
        app.run_web()


if __name__ == "__main__":
    main()