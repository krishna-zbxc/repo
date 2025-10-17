"""Utilities for fetching public Reddit data without authentication."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Sequence

import requests

LOGGER = logging.getLogger(__name__)


@dataclass
class RedditPost:
    """Representation of a Reddit post."""

    id: str
    title: str
    author: str
    selftext: str
    url: str
    score: int
    comment_count: int


@dataclass
class RedditComment:
    """Representation of a top-level Reddit comment."""

    id: str
    author: str
    body: str
    score: int


DEFAULT_HEADERS = {
    "User-Agent": "reddit-ai-shorts/0.1 (by u/anonymous)"
}

REDDIT_BASE_URL = "https://www.reddit.com"


class RedditAPIError(RuntimeError):
    """Raised when the Reddit API returns an unexpected response."""


def _request_json(path: str, params: dict | None = None) -> dict:
    response = requests.get(
        f"{REDDIT_BASE_URL}{path}",
        params=params,
        headers=DEFAULT_HEADERS,
        timeout=30,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as error:  # pragma: no cover - thin wrapper
        raise RedditAPIError(str(error)) from error
    return response.json()


def fetch_top_posts(
    subreddit: str,
    *,
    limit: int = 5,
    time_filter: str = "day",
) -> List[RedditPost]:
    """Return the top posts from a subreddit."""

    payload = _request_json(
        f"/r/{subreddit}/top.json",
        params={"limit": limit, "t": time_filter},
    )
    posts: List[RedditPost] = []
    for child in payload.get("data", {}).get("children", []):
        data = child.get("data", {})
        if data.get("stickied"):
            continue
        post = RedditPost(
            id=data.get("id", ""),
            title=data.get("title", ""),
            author=data.get("author", "unknown"),
            selftext=data.get("selftext", ""),
            url=data.get("url", ""),
            score=int(data.get("score", 0)),
            comment_count=int(data.get("num_comments", 0)),
        )
        posts.append(post)
    return posts


def fetch_top_comments(post_id: str, *, limit: int = 10) -> List[RedditComment]:
    """Return the top-level comments for a given post."""

    payload = _request_json(
        f"/comments/{post_id}.json",
        params={"limit": limit, "depth": 1, "sort": "top"},
    )
    if not isinstance(payload, Sequence) or not payload:
        LOGGER.warning("Unexpected comment payload for post %s", post_id)
        return []
    comments_raw = payload[1].get("data", {}).get("children", [])
    comments: List[RedditComment] = []
    for child in comments_raw:
        data = child.get("data", {})
        if data.get("body") in {None, "[deleted]", "[removed]"}:
            continue
        comment = RedditComment(
            id=data.get("id", ""),
            author=data.get("author", "unknown"),
            body=data.get("body", ""),
            score=int(data.get("score", 0)),
        )
        comments.append(comment)
    return comments


def fetch_posts_with_comments(
    subreddit: str,
    *,
    limit: int = 5,
    comment_limit: int = 5,
    time_filter: str = "day",
) -> Iterable[tuple[RedditPost, List[RedditComment]]]:
    """Fetch posts along with their top comments."""

    for post in fetch_top_posts(subreddit, limit=limit, time_filter=time_filter):
        yield post, fetch_top_comments(post.id, limit=comment_limit)
