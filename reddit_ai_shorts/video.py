"""Utilities for rendering narration scripts into simple vertical videos."""

from __future__ import annotations

import logging
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from moviepy import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

from .generation import ScriptSection, build_outline
from .api import RedditComment, RedditPost

LOGGER = logging.getLogger(__name__)


@dataclass
class VideoTheme:
    """Basic styling information for generated frames."""

    background_color: tuple[int, int, int] = (12, 12, 22)
    heading_color: tuple[int, int, int] = (255, 215, 0)
    body_color: tuple[int, int, int] = (235, 235, 235)
    heading_font_size: int = 110
    body_font_size: int = 64
    width: int = 1080
    height: int = 1920


def _load_font(preferred: Sequence[str], size: int) -> ImageFont.ImageFont:
    for name in preferred:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    LOGGER.debug("Falling back to default font")
    return ImageFont.load_default()


def _render_section_image(section: ScriptSection, *, theme: VideoTheme) -> Image.Image:
    image = Image.new("RGB", (theme.width, theme.height), color=theme.background_color)
    draw = ImageDraw.Draw(image)

    heading_font = _load_font(["DejaVuSans-Bold.ttf", "Arial.ttf"], theme.heading_font_size)
    body_font = _load_font(["DejaVuSans.ttf", "Arial.ttf"], theme.body_font_size)

    margin_x = int(theme.width * 0.08)
    current_y = int(theme.height * 0.08)

    heading_text = section.heading.upper()
    draw.text((margin_x, current_y), heading_text, font=heading_font, fill=theme.heading_color)
    current_y += heading_font.getbbox(heading_text)[3] + int(theme.height * 0.03)

    body_wrapped = textwrap.fill(section.body, width=32)
    draw.multiline_text(
        (margin_x, current_y),
        body_wrapped,
        font=body_font,
        fill=theme.body_color,
        spacing=12,
    )
    return image


def _sections_to_clips(sections: Iterable[ScriptSection], *, theme: VideoTheme, duration: float) -> list[ImageClip]:
    clips: list[ImageClip] = []
    for section in sections:
        frame = _render_section_image(section, theme=theme)
        clip = ImageClip(np.array(frame)).set_duration(duration)
        clips.append(clip)
    return clips


def render_short_video(
    post: RedditPost,
    comments: Iterable[RedditComment],
    output_path: Path,
    *,
    theme: VideoTheme | None = None,
    seconds_per_section: float = 6.0,
    fps: int = 30,
) -> Path:
    """Create a short MP4 video that cycles through narration sections."""

    theme = theme or VideoTheme()
    sections = build_outline(post, comments)
    clips = _sections_to_clips(sections, theme=theme, duration=seconds_per_section)

    if not clips:
        raise ValueError("No sections available to render a video")

    video = concatenate_videoclips(clips, method="compose")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Rendering video to %s", output_path)
    video.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio=False,
        verbose=False,
        logger=None,
    )
    video.close()
    return output_path
