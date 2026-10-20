"""Read-only YouTube Data API v3 client. Credentials come from the environment, never files.

Set YOUTUBE_API_KEY (a key restricted to the YouTube Data API v3 is enough for public
research), or the 3 OAuth refresh variables below. OAuth refresh happens in memory.
Only the read-only endpoints listed in READ_ENDPOINTS can be called.
"""

import os
import time
from collections import Counter

import requests


class YouTubeError(RuntimeError):
    pass


class YouTubeClient:
    READ_ENDPOINTS = {"search", "videos", "channels", "playlistItems", "commentThreads"}

    def __init__(self, max_searches=60, max_calls=1500):
        self.session = requests.Session()
        self.key = os.environ.get("YOUTUBE_API_KEY")
        self.oauth = all(os.environ.get(n) for n in (
            "YOUTUBE_OAUTH_CLIENT_ID", "YOUTUBE_OAUTH_CLIENT_SECRET", "YOUTUBE_OAUTH_REFRESH_TOKEN"))
        if not self.oauth and not self.key:
            raise YouTubeError("No YouTube credentials. Set YOUTUBE_API_KEY, or YOUTUBE_OAUTH_CLIENT_ID, "
                               "YOUTUBE_OAUTH_CLIENT_SECRET and YOUTUBE_OAUTH_REFRESH_TOKEN.")
        self.expires_at = 0
        self.counts = Counter()
        self.max_searches = max_searches
        self.max_calls = max_calls

    def _refresh(self):
        try:
            r = self.session.post("https://oauth2.googleapis.com/token", data={
                "grant_type": "refresh_token",
                "client_id": os.environ["YOUTUBE_OAUTH_CLIENT_ID"],
                "client_secret": os.environ["YOUTUBE_OAUTH_CLIENT_SECRET"],
                "refresh_token": os.environ["YOUTUBE_OAUTH_REFRESH_TOKEN"],
            }, timeout=30)
        except requests.RequestException:
            raise YouTubeError("YouTube OAuth refresh transport failure") from None
        if r.status_code != 200:
            raise YouTubeError(f"YouTube OAuth refresh failed (HTTP {r.status_code})")
        data = r.json()
        self.session.headers["Authorization"] = "Bearer " + data["access_token"]
        self.expires_at = time.monotonic() + int(data.get("expires_in", 3600)) - 60

    def get(self, endpoint, **params):
        if endpoint not in self.READ_ENDPOINTS:
            raise YouTubeError("Only approved read-only endpoints are supported")
        for attempt in range(4):
            if sum(self.counts.values()) >= self.max_calls:
                raise YouTubeError("Local API request cap reached")
            if endpoint == "search" and self.counts[endpoint] >= self.max_searches:
                raise YouTubeError("Local search request cap reached")
            if self.oauth:
                if time.monotonic() >= self.expires_at:
                    self._refresh()
            else:
                params["key"] = self.key
            self.counts[endpoint] += 1
            try:
                r = self.session.get("https://youtube.googleapis.com/youtube/v3/" + endpoint,
                                     params=params, timeout=30)
            except requests.RequestException:
                if attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise YouTubeError(f"YouTube {endpoint} transport failure") from None
            if r.status_code == 200:
                return r.json()
            if r.status_code == 401 and self.oauth and attempt == 0:
                self.expires_at = 0
                continue
            if r.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            try:
                reasons = [e.get("reason", "unknown") for e in r.json().get("error", {}).get("errors", [])]
            except ValueError:
                reasons = []
            raise YouTubeError(f"YouTube {endpoint}: HTTP {r.status_code}, reasons={reasons}")
        raise YouTubeError(f"YouTube {endpoint} retries exhausted")
