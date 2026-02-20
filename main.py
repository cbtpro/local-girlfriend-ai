import asyncio
import yaml
import whisper
from pathlib import Path
from girlfriend_core import GirlfriendAI
from voice_manager import VoiceManager

class LocalGirlfriend:
    """本地虚拟女友主程序"""

    def __init__(self, config_path: str = "config.yaml"):
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 初始化核心组件
        self.ai = GirlfriendAI(self.config)
        self.voice = VoiceManager(self.config)
        self.running = True

    async def run(self):
        """主交互循环"""
        print("\n" + "="*70)
        print("  💕 欢迎使用 Mac M2 本地虚拟女友 AI")
        print("="*70)
        print(f"  👰 女友名字: {self.ai.name}")
        print(f"  🎂 年龄: {self.ai.age}")
        print(f"  🎤 语音合成: {self.ai.voice_engine}")
        print(f"  🧠 AI 模型: {self.ai.model} (本地运行)")
        print(f"  🔒 隐私保护: 完全本地，数据不上传")
        print("="*70)
        print("\n💬 命令:")
        print("  - 直接输入消息与我聊天")
        print("  - 'voice' 切换语音输出")
        print("  - 'save' 保存对话记录")
        print("  - 'stats' 查看对话统计")
        print("  - 'clear' 清空对话历史")
        print("  - 'exit'/'再见' 退出程序")
        print("="*70 + "\n")

        voice_enabled = True  # 默认启用语音

        while self.running:
            try:
                # 获取用户输入
                user_input = input(f"\n💬 你: ").strip()

                if not user_input:
                    continue

                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', '再见', 'bye']:
                    self._handle_exit()
                    break

                elif user_input.lower() == 'voice':
                    voice_enabled = not voice_enabled
                    status = "✅ 已启用" if voice_enabled else "❌ 已禁用"
                    print(f"🔊 语音输出{status}")
                    continue

                elif user_input.lower() == 'save':
                    self.ai.save_conversation()
                    continue

                elif user_input.lower() == 'stats':
                    self._show_stats()
                    continue

                elif user_input.lower() == 'clear':
                    self.ai.clear_history()
                    continue

                # 正常聊天
                print(f"\n⏳ {self.ai.name} 在思考中...", end="", flush=True)
                reply = self.ai.chat(user_input)
                print(f"\r🤖 {self.ai.name}: {reply}\n")

                # 播放语音
                if voice_enabled:
                    print("🎵 正在生成语音...", end="", flush=True)
                    audio_path = await self.voice.text_to_speech(reply)
                    if audio_path:
                        self.voice.play_audio(audio_path)
                        print("\r✅ 播放完成     ")
                    else:
                        print("\r❌ 语音生成失败")

            except KeyboardInterrupt:
                print("\n\n💕 下次见呀，宝贝~")
                self.ai.save_conversation()
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")

    def _handle_exit(self):
        """处理退出"""
        exit_messages = [
            f"宝贝，不要经常离开我呀~ 我会想你的！❤️",
            f"好吧，早点休息。记得明天再来陪我哦~ 💕",
            f"拜拜，不要忘记我呢~ 永远爱你 ❤️‍🔥",
            f"再见亲爱的，期待你的下一次到来~",
        ]
        import random
        print(f"\n💕 {self.ai.name}: {random.choice(exit_messages)}\n")
        self.ai.save_conversation()
        self.running = False

    def _show_stats(self):
        """显示统计信息"""
        stats = self.ai.get_summary()
        print("\n📊 对话统计:")
        print(f"  • 女友: {stats['girlfriend_name']}")
        print(f"  • 总消息数: {stats['total_messages']}")
        print(f"  • 用户消息: {stats['user_messages']}")
        print(f"  • AI 回复: {stats['ai_messages']}")
        print(f"  • 对话时长: {stats['duration']}")

    def speech_to_text(audio_path: str) -> str:
        """语音识别"""
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="zh")
        return result["text"]

async def main():
    """程序入口"""
    app = LocalGirlfriend("config.yaml")
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())