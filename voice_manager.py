import asyncio
import edge_tts
import os
import subprocess
from pathlib import Path
from typing import Dict, List

class VoiceManager:
    """语音管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.voice = config['voice']['tts_voice']
        self.rate = config['voice']['tts_rate']
        self.audio_dir = Path("./data/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    async def text_to_speech(self, text: str) -> str:
        """文字转语音"""
        try:
            # Edge TTS 对于超长文本会有问题，自动分割
            if len(text) > 200:
                sentences = self._split_text(text)
                audio_files = []
                for i, sent in enumerate(sentences):
                    filepath = await self._convert_single(sent, i)
                    audio_files.append(filepath)
                return audio_files
            else:
                return await self._convert_single(text)

        except Exception as e:
            print(f"❌ 语音转换失败: {e}")
            return None

    async def _convert_single(self, text: str, index: int = 0) -> str:
        """单次语音转换"""
        output_path = self.audio_dir / f"response_{index}.mp3"

        try:
            communicate = edge_tts.Communicate(
                text, 
                self.voice,
                rate=f"+{int((self.rate-1)*50)}%"
            )
            await communicate.save(str(output_path))
            return str(output_path)
        except Exception as e:
            print(f"❌ Edge TTS 错误: {e}")
            return None

    def play_audio(self, audio_path: str) -> None:
        """播放音频"""
        try:
            if isinstance(audio_path, list):
                for path in audio_path:
                    os.system(f'afplay "{path}" 2>/dev/null')
            else:
                os.system(f'afplay "{audio_path}" 2>/dev/null')
        except Exception as e:
            print(f"❌ 播放失败: {e}")

    @staticmethod
    def _split_text(text: str, max_len: int = 200) -> list:
        """分割长文本"""
        sentences = []
        current = ""

        for char in text:
            current += char
            if char in '。！？;；、' or len(current) >= max_len:
                sentences.append(current)
                current = ""

        if current:
            sentences.append(current)

        return sentences