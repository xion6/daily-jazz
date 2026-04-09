import datetime
import os

import anthropic

ERA_PROMPTS = [
    "1940〜1960年代のジャズ（ビバップ、ハードバップ、クールジャズなど黄金期）から選んでください。",
    "1970〜1990年代のジャズ（フュージョン、スムースジャズ、ECMレーベル系など）から選んでください。",
    "2000年以降のコンテンポラリージャズから選んでください。",
]

PROMPT = """
あなたはジャズの案内人です。
今日おすすめのジャズを1曲、以下のフォーマットで紹介してください。

---
🎷 今日の1曲

**曲名**:
**アーティスト**:
**アルバム**: （あれば）
**年**:

**一言**: （その曲の魅力を2〜3文で）

**こんな時に**: （どんな場面・気分に合うか）

**豆知識**: （知ると聴き方が変わるエピソードを1つ）
---

{era_instruction}
"""


def main():
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY を環境変数から自動取得

    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"=== 🎵 Daily Jazz: {today} ===\n")

    era_index = datetime.date.today().toordinal() % 3
    era_instruction = ERA_PROMPTS[era_index]
    prompt = PROMPT.format(era_instruction=era_instruction)

    past_songs = os.environ.get("PAST_SONGS", "").strip()
    if past_songs:
        prompt += f"\n以下の曲はすでに紹介済みです。これらは選ばないでください:\n{past_songs}\n"

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    block = message.content[0]
    if isinstance(block, anthropic.types.TextBlock):
        print(block.text)


if __name__ == "__main__":
    main()
