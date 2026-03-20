#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import re
from dataclasses import dataclass
from typing import Optional
from urllib import request
from urllib.parse import urlparse


@dataclass
class ReleaseInfo:
    checksum: str
    url: str
    size: int
    app_name: str
    version: str
    release_type: str
    filename: str


class ReleaseParser:
    FILENAME_PATTERN = re.compile(r"^(.+)-(\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?)-(.+)\.nupkg$")
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    KNOWN_CHANNELS = ("stable", "beta")

    def __init__(self, base_url: str = "https://api.wemod.com/client/channels"):
        self.base_url = base_url

    def get_release_url(self, channel: str = "stable", app_id: str = "Wand") -> str:
        return f"{self.base_url}/{channel}/RELEASES?id={app_id}"

    def fetch_all_channels(
        self, app_id: str = "Wand"
    ) -> dict[str, Optional[ReleaseInfo]]:
        results = {}
        for channel in self.KNOWN_CHANNELS:
            results[channel] = self.fetch_release_info(channel, app_id)
        return results

    def fetch_release_info(
        self, channel: str = "stable", app_id: str = "Wand"
    ) -> Optional[ReleaseInfo]:
        url = self.get_release_url(channel, app_id)
        try:
            req = request.Request(url, headers={"User-Agent": self.USER_AGENT})
            with request.urlopen(req) as response:
                data = response.read().decode("utf-8").strip()
                return self.parse_release_data(data)
        except Exception:
            return None

    def parse_release_data(self, data: str) -> Optional[ReleaseInfo]:
        data = data.lstrip("\ufeff")
        parts = data.split()
        if len(parts) != 3:
            return None

        checksum, url, size_str = parts

        try:
            size = int(size_str)
        except ValueError:
            return None

        filename = self._extract_filename(url)
        if not filename:
            return None

        parsed = self._parse_filename(filename)
        if not parsed:
            return None

        app_name, version, release_type = parsed

        return ReleaseInfo(
            checksum=checksum,
            url=url,
            size=size,
            app_name=app_name,
            version=version,
            release_type=release_type,
            filename=filename,
        )

    def _extract_filename(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        path = parsed.path
        if "/" in path:
            return path.rsplit("/", 1)[-1]
        return path if path else None

    def _parse_filename(self, filename: str) -> Optional[tuple[str, str, str]]:
        match = self.FILENAME_PATTERN.match(filename)
        if not match:
            return None
        return match.group(1), match.group(2), match.group(3)
