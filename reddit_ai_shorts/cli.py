"""Command-line interface for generating Reddit short scripts."""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
import sys
from typing import Iterable

from . import __version__
from .api import fetch_posts_with_comments
from .generation import compose_llm_prompt, create_narration_script
from .video import render_short_video

LOGGER = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _slugify(text: str) -> str:
    keep = [c if c.isalnum() else "-" for c in text.lower()]
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:80] or "post"


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate AI-ready scripts from Reddit posts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("subreddit", help="Target subreddit to process")
    parser.add_argument("--limit", type=int, default=3, help="Number of posts to fetch")
    parser.add_argument(
        "--comment-limit",
        type=int,
        default=5,
        help="Number of top comments to include",
    )
    parser.add_argument(
        "--time-filter",
        choices=["hour", "day", "week", "month", "year", "all"],
        default="day",
        help="Reddit timeframe for selecting top posts",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("shorts_output"),
        help="Directory to save generated scripts",
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        default=None,
        help=(
            "Custom User-Agent header to send to reddit.com. "
            "Set this to something like 'script-name/1.0 (by u/yourname)'."
        ),
    )
    parser.add_argument(
        "--prompts",
        action="store_true",
        help="Also save prompts suitable for sending to an LLM",
    )
    parser.add_argument(
        "--video",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Render a simple vertical MP4 video for each script",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"reddit-ai-shorts {__version__}",
    )
    return parser.parse_args(argv)


def _write_text(path: pathlib.Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    LOGGER.info("Wrote %s", path)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    _configure_logging(args.verbose)

    args.output.mkdir(parents=True, exist_ok=True)

    for post, comments in fetch_posts_with_comments(
        args.subreddit,
        limit=args.limit,
        comment_limit=args.comment_limit,
        time_filter=args.time_filter,
        user_agent=args.user_agent,
    ):
        video_path: pathlib.Path | None = None
        if not post.id:
            LOGGER.debug("Skipping post with missing identifier")
            continue
        slug = _slugify(post.title or post.id)
        narration = create_narration_script(post, comments)
        narration_path = args.output / f"{slug}.md"
        _write_text(narration_path, narration)

        if args.prompts:
            prompt = compose_llm_prompt(post, comments)
            prompt_path = args.output / f"{slug}_prompt.txt"
            _write_text(prompt_path, prompt)

        if args.video:
            video_path = args.output / f"{slug}.mp4"
            render_short_video(post, comments, video_path)

        metadata_path = args.output / f"{slug}.json"
        metadata = {
            "id": post.id,
            "title": post.title,
            "author": post.author,
            "score": post.score,
            "comment_count": post.comment_count,
            "thread_url": post.url,
            "script_path": narration_path.name,
            "video_path": video_path.name if video_path else None,
        }
        _write_text(metadata_path, json.dumps(metadata, indent=2))

    LOGGER.info(
        "Finished generating scripts. Use the markdown files as narration or feed the prompts into your preferred text model."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
