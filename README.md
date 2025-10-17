# Reddit AI Shorts Toolkit

This repository contains a small toolkit for turning Reddit threads into scripts, prompts, and ready-to-share vertical videos that you can use when producing AI narrated shorts. The CLI fetches the hottest stories, packages them into narration-ready markdown, renders a simple MP4 with animated slides, and optionally builds prompts for a large language model so you can polish the copy before recording.

## Features

- Fetches the top posts from any public subreddit without needing API credentials.
- Captures the highest-voted comments to add community reactions to the script.
- Generates narration drafts in Markdown format for quick editing.
- Renders a looping MP4 that cycles through the narration sections for instant previews.
- Optionally exports LLM prompts so you can ask your favourite model to improve the script.

## Requirements

- Python 3.10+
- Reddit allows unauthenticated requests with a descriptive `User-Agent`. Heavy usage should move to the official API.
- Dependencies listed in `requirements.txt` (`requests`, `moviepy`, `Pillow`, `imageio-ffmpeg`).
- FFmpeg available on your system. MoviePy will use the binary to encode the final MP4; on Debian/Ubuntu run `sudo apt install ffmpeg`.

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

1. Pick a descriptive [User-Agent string](https://github.com/reddit-archive/reddit/wiki/API#rules) for Reddit, for example `reddit-ai-shorts/1.0 (by u/yourname)`.
2. Run the CLI with your target subreddit and desired limits:

   ```bash
   python -m reddit_ai_shorts askreddit --limit 3 --comment-limit 5 --user-agent "reddit-ai-shorts/1.0 (by u/yourname)"
   ```

3. Open the generated assets in the `shorts_output/` folder:
   - `*.md` &mdash; narration-ready Markdown scripts split into sections
   - `*.mp4` &mdash; looping vertical slideshow rendering of the narration
   - `*_prompt.txt` &mdash; optional LLM prompts when `--prompts` is used
   - `*.json` &mdash; metadata tying everything back to the original thread

The command saves Markdown scripts, JSON metadata, MP4 videos, and (if requested) LLM prompts in the `shorts_output/` directory. File names are automatically slugified from the post titles. Pass `--no-video` if you only need the text outputs or `--output PATH` to write everything somewhere else.

### Example workflow

1. Run the CLI to gather a batch of trending posts.
2. Review the generated Markdown and tweak the script to match your tone.
3. Feed the prompt files into your preferred language model for a polished narration.
4. Review the auto-generated MP4 for pacing and adjust the script or regenerate as needed.

### Generating polished scripts with an LLM

The CLI produces prompt files that you can paste into models such as ChatGPT or local LLMs. They include context about the post and its comments. Ask the model to keep the script under 90 seconds and to end with a call to action.

### Command reference

- `--limit` / `--comment-limit` &mdash; control how many posts and top-level comments are collected.
- `--time-filter` &mdash; choose the Reddit ranking window (`hour`, `day`, `week`, etc.).
- `--prompts` &mdash; save LLM prompt drafts next to the narration.
- `--video` / `--no-video` &mdash; toggle the automatic MP4 renderer.
- `--user-agent` &mdash; override the HTTP User-Agent header (recommended to avoid rate limits).
- `--output` &mdash; pick a different folder for the generated assets.

### Tips for video production

- Keep visuals dynamic: show comment highlights, related imagery, or subtle motion graphics.
- Use a consistent intro and outro to build brand recognition.
- Automate the editing flow with templates in your NLE or video automation tools.

## Contributing

Feel free to extend the toolkit by adding text-to-speech integration, B-roll selection, or timeline generation.
