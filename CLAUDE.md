# Research Briefings — audio episode workflow

When the user asks for an episode/briefing/podcast on a topic, do this:

1. **Research** the topic with WebSearch / WebFetch (5–10 good, recent sources;
   prefer primary sources and reputable outlets). Note today's date and say
   when facts are recent or uncertain.
2. **Write the script** to `scripts/YYYY-MM-DD-<slug>.md`:
   - English, single narrator, 900–1,400 words (≈ 6–10 minutes).
   - Written for the ear: short sentences, no tables, no bullet lists, no URLs,
     spell out abbreviations on first use, numbers rounded and spoken naturally.
   - Structure: a hook (1–2 sentences) → what it is / why it matters → 3–4
     main sections with clear verbal transitions ("Second, ...") → open
     questions or what to watch next → a 3-sentence recap.
   - Mention sources by name in speech ("according to Reuters...").
   - Append a `<!-- sources -->` HTML comment at the end listing source URLs
     (it is not spoken; the cleaner strips links but keep it as a comment).
3. **Make the MP3 and update the feed**:
   `py make_episode.py scripts/<file>.md "<Episode title>" "<one-line description>"`
4. **Publish**: `git add -A && git commit -m "Episode: <title>" && git push`
   (only if the repo has a remote set up). The episode appears in the podcast
   app / Alexa within minutes to an hour, depending on the app's refresh.
5. Tell the user the title, duration, and 3–5 key sources.

Settings (voice, speed, feed title, base URL) are in `config.json`.
Good voices: en-US-AndrewNeural, en-US-AvaNeural, en-GB-RyanNeural,
en-US-BrianNeural, en-US-EmmaNeural (`py -m edge_tts --list-voices`).

## Topic scope
When suggesting topics, keep every proposal corporate-world related: leadership, career growth, office politics, workplace dynamics, management (pharma-corporate framing welcome). No science, health, history, travel or personal-finance topics unless the user asks.
