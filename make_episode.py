"""Turn a written script into an MP3 episode and add it to the podcast feed.

Usage:
    py make_episode.py scripts/2026-11-12-my-topic.md "Episode title" "One-line description"

The script file is plain text / light markdown. Headings and markdown symbols
are stripped before speaking. Output goes to docs/episodes/, and docs/feed.xml
is regenerated from docs/episodes.json.
"""
import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

import edge_tts
from mutagen.mp3 import MP3

ROOT = Path(__file__).parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
DOCS = ROOT / "docs"
EPISODES_DIR = DOCS / "episodes"
INDEX = DOCS / "episodes.json"


def clean_for_speech(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text, flags=re.M)          # headings
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)     # links -> text
    text = re.sub(r"https?://\S+", "", text)                 # bare urls
    text = re.sub(r"[*_`>]+", "", text)                      # emphasis, quotes
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.M)      # bullets
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


async def synthesize(text: str, out: Path) -> None:
    tts = edge_tts.Communicate(text, CONFIG["voice"], rate=CONFIG.get("rate", "+0%"))
    await tts.save(str(out))


def build_feed(episodes: list) -> str:
    base = CONFIG["base_url"].rstrip("/")
    items = []
    for ep in sorted(episodes, key=lambda e: e["date"], reverse=True):
        items.append(f"""    <item>
      <title>{escape(ep['title'])}</title>
      <description>{escape(ep['description'])}</description>
      <guid isPermaLink="false">{escape(ep['file'])}</guid>
      <pubDate>{ep['pubdate']}</pubDate>
      <enclosure url="{base}/episodes/{ep['file']}" length="{ep['bytes']}" type="audio/mpeg"/>
      <itunes:duration>{ep['seconds']}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(CONFIG['podcast_title'])}</title>
    <link>{base}/</link>
    <description>{escape(CONFIG['podcast_description'])}</description>
    <language>{CONFIG.get('language', 'en')}</language>
    <itunes:author>{escape(CONFIG['author'])}</itunes:author>
    <itunes:image href="{base}/cover.png"/>
    <itunes:category text="Education"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    script_path = Path(sys.argv[1])
    title = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else title

    EPISODES_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    filename = f"{now:%Y-%m-%d}-{slugify(title)}.mp3"
    out = EPISODES_DIR / filename

    text = clean_for_speech(script_path.read_text(encoding="utf-8"))
    print(f"Synthesizing {len(text.split())} words with {CONFIG['voice']}...")
    asyncio.run(synthesize(text, out))

    seconds = int(MP3(out).info.length)
    episodes = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else []
    episodes = [e for e in episodes if e["file"] != filename]
    episodes.append({
        "title": title,
        "description": description,
        "file": filename,
        "date": now.isoformat(),
        "pubdate": format_datetime(now),
        "bytes": out.stat().st_size,
        "seconds": seconds,
    })
    INDEX.write_text(json.dumps(episodes, indent=2), encoding="utf-8")
    (DOCS / "feed.xml").write_text(build_feed(episodes), encoding="utf-8")
    print(f"Done: {out}  ({seconds // 60}m{seconds % 60:02d}s)")


if __name__ == "__main__":
    main()
