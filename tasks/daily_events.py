import anthropic
import datetime
from typing import cast

from anthropic.types import MessageParam

PROMPT = """
東京で今週末（{date_range}）に開催される、デートに使いやすいイベントを3件紹介してください。
アート展、グルメイベント、マーケット、音楽ライブなど幅広いジャンルから選んでください。

---
🗓️ 今週末の東京イベント

**① イベント名**
- 場所:
- 日時:
- 概要:（2〜3文）
- デートポイント:（なぜ一緒に行くと楽しいか）

**② イベント名**
（同上）

**③ イベント名**
（同上）
---
"""


def main():
    client = anthropic.Anthropic()

    today = datetime.date.today()
    days_to_sat = (5 - today.weekday()) % 7 or 7
    sat = today + datetime.timedelta(days=days_to_sat)
    sun = sat + datetime.timedelta(days=1)
    date_range = f"{sat.strftime('%m月%d日')}（土）〜{sun.strftime('%m月%d日')}（日）"

    print(f"=== 🗓️ 今週末の東京イベント: {sat.strftime('%Y-%m-%d')} ===\n")

    messages: list[MessageParam] = [{"role": "user", "content": PROMPT.format(date_range=date_range)}]

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=messages,
        )

        for block in response.content:
            if isinstance(block, anthropic.types.TextBlock):
                print(block.text)

        if response.stop_reason != "tool_use":
            break

        messages.append(cast(MessageParam, {"role": "assistant", "content": response.content}))
        messages.append(cast(MessageParam, {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": block.id, "content": ""}
                for block in response.content
                if block.type == "tool_use"
            ],
        }))


if __name__ == "__main__":
    main()
