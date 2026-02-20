import asyncio
import edge_tts
import pyttsx3
import os
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import time

class VoiceManager:
    """语音管理器 - 支持在线和离线语音合成"""

    def __init__(self, config: Dict):
        self.config = config
        self.voice = config['voice']['tts_voice']
        self.rate = config['voice']['tts_rate']
        self.audio_dir = Path("./data/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        # 离线语音配置
        self.offline_enabled = config['voice'].get('offline_enabled', True)
        self.offline_engine = config['voice'].get('offline_engine', 'pyttsx3')
        self.offline_voice = config['voice'].get('offline_voice', None)
        self.offline_rate = config['voice'].get('offline_rate', 1.0)

        # 初始化离线引擎
        self.pyttsx3_engine = None
        if self.offline_enabled:
            self._init_pyttsx3()

    def _init_pyttsx3(self) -> None:
        """初始化 pyttsx3 离线语音引擎"""
        try:
            self.pyttsx3_engine = pyttsx3.init()
            # 设置语速（pyttsx3 的默认范围是 50-300）
            rate = max(50, min(300, int(150 * self.offline_rate)))
            self.pyttsx3_engine.setProperty('rate', rate)
            # 设置音量（0.0-1.0）
            self.pyttsx3_engine.setProperty('volume', 1.0)
            print("✅ 离线语音引擎 pyttsx3 初始化成功")
        except Exception as e:
            print(f"⚠️  pyttsx3 初始化失败: {e}")
            self.pyttsx3_engine = None

    def _check_network_connectivity(self, timeout: int = 2) -> bool:
        """检查网络连接状态

        Args:
            timeout: 超时时间（秒）

        Returns:
            True 表示网络可用，False 表示网络不可用
        """
        try:
            # 尝试连接到 Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except (socket.timeout, socket.error):
            return False

    async def text_to_speech(self, text: str) -> str:
        """文字转语音 - 支持在线和离线"""
        try:
            # 检查网络连接
            has_network = self._check_network_connectivity()

            if has_network:
                # 优先使用 Edge TTS（在线）
                print("🌐 使用在线语音引擎 (Edge TTS)...")
                result = await self._convert_with_edge_tts(text)
                if result:
                    return result
                else:
                    print("⚠️  Edge TTS 生成失败，降级到离线...")
            else:
                print("📡 网络不可用，使用离线语音引擎...")

            # 使用离线引擎
            return self._convert_with_pyttsx3(text)

        except Exception as e:
            print(f"❌ 语音合成错误: {e}")
            # 最后尝试离线
            if self.offline_enabled and self.pyttsx3_engine:
                return self._convert_with_pyttsx3(text)
            return None

    async def _convert_with_edge_tts(self, text: str) -> str:
        """使用 Edge TTS 进行语音合成"""
        try:
            # Edge TTS 对于超长文本会有问题，自动分割
            if len(text) > 200:
                sentences = self._split_text(text)
                audio_files = []
                for i, sent in enumerate(sentences):
                    filepath = await self._convert_single_edge_tts(sent, i)
                    if filepath:
                        audio_files.append(filepath)
                return audio_files if audio_files else None
            else:
                return await self._convert_single_edge_tts(text, 0)

        except Exception as e:
            print(f"❌ Edge TTS 转换失败: {e}")
            return None

    async def _convert_single_edge_tts(self, text: str, index: int = 0) -> str:
        """单次 Edge TTS 语音转换"""
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
            print(f"❌ Edge TTS 单次转换失败: {e}")
            return None

    def _convert_with_pyttsx3(self, text: str) -> str:
        """使用 pyttsx3 进行离线语音合成"""
        if not self.pyttsx3_engine:
            print("❌ 离线语音引擎未初始化")
            return None

        try:
            output_path = self.audio_dir / "response_offline.mp3"

            print(f"🎵 正在使用离线引擎生成语音...")

            # pyttsx3 保存音频文件
            # 注意：pyttsx3 在 macOS 上可能有问题，使用系统命令作为备选方案
            self.pyttsx3_engine.save_to_file(text, str(output_path))
            self.pyttsx3_engine.runAndWait()

            # 检查文件是否生成
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"✅ 离线语音生成成功: {output_path}")
                return str(output_path)
            else:
                print("⚠️  pyttsx3 未能生成音频，尝试使用系统 say 命令...")
                return self._convert_with_say_command(text)

        except Exception as e:
            print(f"❌ 离线语音转换失败: {e}")
            # 降级到系统 say 命令
            return self._convert_with_say_command(text)

    def _convert_with_say_command(self, text: str) -> str:
        """在 macOS 上使用 say 命令生成语音（备选方案）"""
        try:
            output_path = self.audio_dir / "response_offline_say.m4a"

            print("🎵 使用 macOS say 命令生成语音...")

            # 使用 macOS 自带的 say 命令
            cmd = f'say -o "{output_path}" -v "Ting-Ting" "{text}"'
            os.system(cmd)

            # 检查文件是否生成
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"✅ 系统语音生成成功: {output_path}")
                return str(output_path)
            else:
                print("❌ 系统 say 命令也失败了")
                return None

        except Exception as e:
            print(f"❌ say 命令生成失败: {e}")
            return None

    def play_audio(self, audio_path: str) -> None:
        """播放音频"""
        try:
            if isinstance(audio_path, list):
                for path in audio_path:
                    if os.path.exists(path):
                        os.system(f'afplay "{path}" 2>/dev/null')
                    else:
                        print(f"⚠️  音频文件不存在: {path}")
            else:
                if os.path.exists(audio_path):
                    os.system(f'afplay "{audio_path}" 2>/dev/null')
                else:
                    print(f"⚠️  音频文件不存在: {audio_path}")
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