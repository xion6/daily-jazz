import anthropic
import datetime

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

毎回異なる曲を選んでください。モダンジャズ、ビバップ、フュージョン、ボサノバなど幅広いジャンルから選んでください。
"""


def main():
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY を環境変数から自動取得

    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"=== 🎵 Daily Jazz: {today} ===\n")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": PROMPT}],
    )

    block = message.content[0]
    if isinstance(block, anthropic.types.TextBlock):
        print(block.text)


if __name__ == "__main__":
    main()
