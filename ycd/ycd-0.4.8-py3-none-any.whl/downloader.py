import os
import random
import signal
import time
from ycd.youtube.channel import get_videos
from .arguments import Arguments
from json.decoder import JSONDecodeError
from pathlib import Path
from pytchat import util, Extractor, HTMLArchiver, VideoInfo
from pytchat.exceptions import InvalidVideoIdException, NoContents, PatternUnmatchError
from pytchat.util.extract_video_id import extract_video_id
from typing import List, Dict
from .youtube import channel
from .progressbar import ProgressBar


class Downloader:

    def __init__(self, dir_videos: set):
        self._dir_videos = dir_videos

    def video(self, video) -> None:

        video_id = extract_video_id(video.get('id'))
        try:

            if not os.path.exists(Arguments().output):
                raise FileNotFoundError
            separated_path = str(Path(Arguments().output)) + os.path.sep
            path = util.checkpath(separated_path + video_id + '.html')
            # check if the video_id is already exists the output folder
            if video_id in self._dir_videos:
                print(
                    f"Video [{video_id}] is already exists in {os.path.dirname(path)}. Skip process.")
                return False
            time.sleep(random.random()*2+2)            
            print(f"\n"
                  f"[title]    {video.get('title')}\n"
                  f"[id]       {video_id}    [published] {video.get('time_published')}\n"
                  f"[channel]  {video.get('author')}"
                  )
            print(f"[path]     {path}")
            try:
                duration = video["duration"]
            except KeyError:
                return False
            pbar = ProgressBar(total=(duration * 1000), status="Extracting")

            ex = Extractor(video_id,
                           callback=pbar._disp)
            signal.signal(signal.SIGINT, (lambda a, b: self.cancel(ex, pbar)))
            data = ex.extract()
            if data == []:
                return False
            pbar.reset("#", "=", total=len(data), status="Rendering  ")
            processor = HTMLArchiver(path, callback=pbar._disp)
            processor.process(
                [{'video_id': None,
                  'timeout': 1,
                  'chatdata': (action["replayChatItemAction"]["actions"][0] for action in data)}]
            )
            processor.finalize()
            pbar.close()
            print("\nCompleted")

            print()
            if pbar.is_cancelled():
                print("\nThe extraction process has been discontinued.\n")
                return False
            return True

        except InvalidVideoIdException:
            print("Invalid Video ID or URL:", video_id)
        except NoContents as e:
            print('---' + str(e) + '---')
        except FileNotFoundError:
            print("The specified directory does not exist.:{}".format(
                Arguments().output))
            exit(0)
        except JSONDecodeError as e:
            print(e.msg)
            print("Cannot parse video information.:{}".format(video_id))
            if Arguments().save_error_data:
                util.save(e.doc, "ERR_JSON_DECODE", ".dat")
        except PatternUnmatchError as e:
            print(e.msg)
            print("Cannot parse video information.:{}".format(video_id))
            if Arguments().save_error_data:
                util.save(e.doc, "ERR_PATTERN_UNMATCH", ".dat")

    def videos(self, video_ids: List[int]) -> None:
        for i, video_id in enumerate(video_ids):
            print(f"\n{'-'*10} video:{i+1} of {len(video_ids)} {'-'*10}")
            if '[' in video_id or ']' in video_id:
                video_id = video_id.replace('[', '').replace(']', '')
            try:
                video = self.get_info(video_id)
                if video.get('error'):
                    continue
                self.video(video)
            except InvalidVideoIdException:
                print(f"Invalid video id: {video_id}")

    def channels(self, channels: List[str]) -> None:
        for i, ch in enumerate(channels):
            counter = 0
            for video in get_videos(channel.get_channel_id(ch)):
                if counter > Arguments().first - 1:
                    break
                print(
                    f"\n{'-'*10} channel: {i+1} of {len(channels)} / video: {counter+1} of {Arguments().first} {'-'*10}")
                ret = self.video(video)
                if ret:
                    counter += 1

    def cancel(self, ex, pbar) -> None:
        ex.cancel()
        pbar.cancel()

    def get_info(self, video_id: str) -> Dict:
        video = dict()
        for i in range(3):
            try:
                info = VideoInfo(video_id)
                break
            except PatternUnmatchError:
                time.sleep(2)
                continue
        else:
            print(f"PatternUnmatchError:{video_id}")
            return {'error': True}

        video['id'] = video_id
        video['author'] = info.get_channel_id()
        video['time_published'] = "Unknown"
        video['title'] = info.get_title()
        video['duration'] = info.get_duration()
        return video
