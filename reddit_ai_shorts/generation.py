"""Helpers for turning Reddit content into AI-friendly prompts and scripts."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Iterable, List

from .api import RedditComment, RedditPost


@dataclass
class ScriptSection:
    """A portion of the generated narration script."""

    heading: str
    body: str


def build_outline(post: RedditPost, comments: Iterable[RedditComment]) -> List[ScriptSection]:
    """Create a rough outline for a vertical short-form video."""

    comments = list(comments)
    intro = ScriptSection(
        heading="Hook",
        body=textwrap.fill(
            (
                f"Reddit story from r/{post.author if post.author != 'unknown' else 'anonymous'}: "
                f"{post.title.strip()}"
            ),
            width=80,
        ),
    )

    body_lines: List[str] = []
    if post.selftext:
        body_lines.append(post.selftext.strip())
    if comments:
        body_lines.append("Top community reactions:")
        for comment in comments[:3]:
            comment_line = f"- {comment.author}: {comment.body.strip()}"
            body_lines.append(comment_line)
    if not body_lines:
        body_lines.append("Check out the full thread for more details!")
    main_section = ScriptSection(
        heading="Story",
        body=textwrap.fill("\n".join(body_lines), width=80),
    )

    outro = ScriptSection(
        heading="Call to action",
        body="Follow for more daily Reddit stories!",
    )
    return [intro, main_section, outro]


def create_narration_script(post: RedditPost, comments: Iterable[RedditComment]) -> str:
    """Combine sections into a narration-friendly script."""

    sections = build_outline(post, comments)
    lines: List[str] = []
    for section in sections:
        lines.append(section.heading.upper())
        lines.append(section.body)
        lines.append("")
    return "\n".join(lines).strip()


def compose_llm_prompt(post: RedditPost, comments: Iterable[RedditComment]) -> str:
    """Return a prompt that can be sent to a text generation model."""

    comments = list(comments)
    prompt_parts = [
        "You are a short-form video script writer.",
        "Write a 3-part, 90-second narration for vertical video summarizing the Reddit post.",
        "Each part should be 2-3 sentences and keep the viewer engaged.",
        "Use a friendly, excited tone and finish with a call to action.",
        "Post details:",
        f"Title: {post.title}",
        f"Author: {post.author}",
        f"Score: {post.score}",
        f"Comments: {post.comment_count}",
    ]
    if post.selftext:
        prompt_parts.append("Original post body:\n" + post.selftext)
    if comments:
        prompt_parts.append("Key top comments:")
        for comment in comments[:5]:
            prompt_parts.append(f"- {comment.author}: {comment.body}")
    prompt_parts.append(
        "Return the script as markdown with headings for Hook, Story, and Call to action."
    )
    return "\n\n".join(prompt_parts)
