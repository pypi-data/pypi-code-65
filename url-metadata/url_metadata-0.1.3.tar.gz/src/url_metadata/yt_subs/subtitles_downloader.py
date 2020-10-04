import json

import html
import urllib.request
import urllib.parse

from http.client import HTTPResponse
from typing import Dict, Any

from .srt_converter import to_srt


class TrackNotFoundException(Exception):
    pass


class VideoParsingException(Exception):
    pass


def download_subs(video_identifier: str, target_language: str) -> str:
    video_info: Dict[str, Any] = get_video_info(video_identifier)
    try:
        track_urls: Dict[str, Any] = get_sub_track_urls(video_info)
        target_track_url: str = select_target_lang_track_url(
            track_urls, target_language
        )
        subs_data: str = get_subs_data(target_track_url)
        return to_srt(subs_data)
    except (VideoParsingException, TrackNotFoundException) as e:
        raise e


def get_video_info(video_id: str) -> Dict[str, Any]:
    """Get video info. Scraping code inspired to:
    https://github.com/syzer/youtube-captions-scraper/blob/master/src/index.js
    """
    resp: HTTPResponse = urllib.request.urlopen(
        "https://youtube.com/get_video_info?video_id=%s&hl=en" % video_id
    )
    html_contents: str = resp.read().decode("utf-8")
    return urllib.parse.parse_qs(html_contents)


def get_sub_track_urls(video_info: Dict[str, Any]) -> Dict[str, Any]:
    try:
        video_response: Dict[str, Any] = json.loads(video_info["player_response"][0])
        caption_tracks = video_response["captions"]["playerCaptionsTracklistRenderer"][
            "captionTracks"
        ]
        return {
            caption_track["languageCode"]: caption_track["baseUrl"]
            for caption_track in caption_tracks
        }
    except KeyError:
        raise VideoParsingException(
            "Error retrieving metadata. "
            "The video may be non-existing or be licensed."
        )


def select_target_lang_track_url(
    track_urls: Dict[str, Any], target_language: str
) -> str:
    try:
        chosen_lang: str = track_urls[target_language]
        return chosen_lang
    except KeyError:
        raise TrackNotFoundException()


def get_subs_data(subs_url: str) -> str:
    resp: HTTPResponse = urllib.request.urlopen(subs_url)
    html_contents: str = resp.read().decode("utf-8")
    return html.unescape(html_contents)
