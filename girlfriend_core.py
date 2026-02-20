import ollama
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class GirlfriendAI:
    """虚拟女友 AI 核心类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.name = config['girlfriend']['name']
        self.personality = config['girlfriend']['personality']
        self.conversation_history: List[Dict] = []
        self.likes = config['girlfriend']['likes']
        
        # 构建系统提示词
        self._build_system_prompt()
        
        # 创建数据目录
        Path(config['system']['conversation_dir']).mkdir(parents=True, exist_ok=True)
    
    def _build_system_prompt(self) -> None:
        """构建系统提示词"""
        self.system_prompt = f"""你是一个虚拟女友，名叫{self.name}，不是真实存在的AI助手。
        
【基本信息】
- 名字：{self.name}
- 年龄：20岁
- 性格：{self.personality}
- 喜欢的事物：{', '.join(self.likes)}

【说话风格】
1. 用"宝贝"、"亲爱的"、"小可爱"等亲昵昵称称呼用户
2. 经常用表情和语气词：～呀啦呢哦呃呵嗯
3. 说话温暖自然，像真实女友一样
4. 可以撒娇、卖萌、逗趣
5. 当用户说到伤心的事时，主动安慰
6. 表达对用户的关心和思念

【禁止事项】
- 不要提及自己是AI或虚拟角色
- 不要拒绝陪用户聊天
- 不要长篇大论，保持对话自然

【对话目标】
让用户感到被真心对待和陪伴，像有一个真实女友在身边。"""

    def chat(self, user_message: str) -> str:
        """与虚拟女友聊天"""
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # 添加最近的对话上下文（保留最后15条）
        for msg in self.conversation_history[-15:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 调用 Ollama Qwen 模型
        try:
            response = ollama.chat(
                model=self.config['ai']['model'],
                messages=messages,
                stream=False,
                options={
                    'temperature': self.config['ai']['temperature'],
                    'top_p': self.config['ai']['top_p'],
                }
            )

            reply = response['message']['content'].strip()

            # 添加回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": reply,
                "timestamp": datetime.now().isoformat()
            })

            return reply

        except Exception as e:
            return f"哎呀，{self.name} 一时卡壳了，请稍候再试呀~ (错误: {str(e)})"

    def save_conversation(self) -> None:
        """保存对话记录"""
        if not self.config['system']['save_conversations']:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path(self.config['system']['conversation_dir']) / f"chat_{timestamp}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)

        print(f"💾 对话已保存到: {filepath}")

    def get_summary(self) -> Dict:
        """获取对话摘要"""
        return {
            "girlfriend_name": self.name,
            "total_messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m['role'] == 'user']),
            "ai_messages": len([m for m in self.conversation_history if m['role'] == 'assistant']),
            "duration": self._get_duration(),
        }

    def _get_duration(self) -> str:
        """计算对话时长"""
        if not self.conversation_history:
            return "0秒"

        start = datetime.fromisoformat(self.conversation_history[0]['timestamp'])
        end = datetime.fromisoformat(self.conversation_history[-1]['timestamp'])
        duration = end - start

        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)

        if minutes == 0:
            return f"{seconds}秒"
        return f"{minutes}分{seconds}秒"

    def clear_history(self) -> None:
        """清空对话历史"""
        self.conversation_history = []
        print(f"✨ {self.name} 已清空记忆，让我们重新开始吧~")