import datetime
import os
import random
import sys

import anthropic
import httpx

ERA_SEARCH_TERMS = {
    "1940〜1960年代": [
        "bebop jazz",
        "cool jazz",
        "hard bop",
        "jazz standard",
        "swing jazz",
        "jazz piano trio",
        "jazz trumpet",
    ],
    "1970〜1990年代": [
        "jazz fusion",
        "jazz funk",
        "post bop jazz",
        "jazz piano",
        "contemporary jazz",
        "smooth jazz",
        "jazz saxophone",
    ],
    "2000年以降": [
        "modern jazz",
        "contemporary jazz",
        "nu jazz",
        "jazz piano",
        "indie jazz",
        "jazz quartet",
        "jazz ballad",
    ],
}

ERA_LABELS = list(ERA_SEARCH_TERMS.keys())

SYSTEM_PROMPT = "あなたはジャズの案内人です。"

DESCRIPTION_PROMPT = """\
以下の実在する曲について、指定のフォーマットで紹介文を書いてください。
曲名・アーティスト・アルバム・年・Apple MusicのURLはそのまま使い、変更しないでください。

---
🎷 今日の1曲（{era_label}）

**曲名**: {title}
**アーティスト**: {artist}
**アルバム**: {album}
**年**: {year}
**Apple Music**: {apple_music_url}

**一言**: （その曲の魅力を2〜3文で）

**こんな時に**: （どんな場面・気分に合うか）

**豆知識**: （知ると聴き方が変わるエピソードを1つ）
---
"""


def fetch_random_jazz_track(era_label: str, past_titles: set[str]) -> dict | None:
    terms = ERA_SEARCH_TERMS[era_label]
    # 検索termをシャッフルして全termを順に試す
    shuffled_terms = random.sample(terms, len(terms))

    for term in shuffled_terms:
        offset = random.choice(range(0, 200, 25))
        response = httpx.get(
            "https://itunes.apple.com/search",
            params={
                "term": term,
                "entity": "song",
                "genreId": "11",  # Jazz
                "limit": 50,
                "offset": offset,
            },
            timeout=10,
        )
        response.raise_for_status()

        raw = response.json().get("results", [])
        print(f"[debug] term={term!r} offset={offset} raw={len(raw)}", file=sys.stderr, flush=True)

        tracks = [t for t in raw if t.get("primaryGenreName") == "Jazz"]
        tracks = [t for t in tracks if t.get("trackName") not in past_titles]
        print(f"[debug] after filters={len(tracks)}", file=sys.stderr, flush=True)

        if tracks:
            return random.choice(tracks)

    return None


def main():
    client = anthropic.Anthropic()

    today = datetime.date.today()
    print(f"=== 🎵 Daily Jazz: {today.strftime('%Y-%m-%d')} ===\n")

    # 日付をシードにすることで同日の再実行は同じ年代を選びつつ、単純な循環を避ける
    rng = random.Random(today.toordinal())
    era_index = rng.randint(0, 2)
    era_label = ERA_LABELS[era_index]

    past_songs = os.environ.get("PAST_SONGS", "").strip()
    past_titles = {line.strip() for line in past_songs.splitlines() if line.strip()}

    track = fetch_random_jazz_track(era_label, past_titles)

    if track is None:
        print("Apple Musicから曲を取得できませんでした。", file=sys.stderr)
        sys.exit(1)

    title = track["trackName"]
    artist = track["artistName"]
    album = track["collectionName"]
    year = track["releaseDate"][:4]
    apple_music_url = track["trackViewUrl"]

    prompt = DESCRIPTION_PROMPT.format(
        era_label=era_label,
        title=title,
        artist=artist,
        album=album,
        year=year,
        apple_music_url=apple_music_url,
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    if not message.content:
        print("Claude からの応答が空でした。")
        return

    block = message.content[0]
    if isinstance(block, anthropic.types.TextBlock):
        print(block.text)


if __name__ == "__main__":
    main()
