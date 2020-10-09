
from .utils import getListGames
import os

import numpy as np
import cv2  # pip install opencv-python (==3.4.11.41)
import imutils  # pip install imutils
import skvideo.io
from tqdm import tqdm

import moviepy.editor

def getDuration(video_path):
    
    time_second = moviepy.editor.VideoFileClip(video_path).duration
    return time_second

class Frame():
    def __init__(self, video_path, FPS=2, transform=None, start=None, duration=None):

        self.FPS = FPS
        self.transform = transform

        # Knowing number of frames from FFMPEG metadata w/o without iterating over all frames
        videodata = skvideo.io.FFmpegReader(video_path)
        # numFrame x H x W x channels
        (numframe, _, _, _) = videodata.getShape()
        # if self.verbose:
            # print("shape video", videodata.getShape())
        self.time_second = getDuration(video_path)
        # fps_video = numframe / time_second

        # time_second = getDuration(video_path)
        # if self.verbose:
        #     print("duration video", time_second)

        good_number_of_frames = False
        while not good_number_of_frames:
            fps_video = numframe / self.time_second
            # time_second = numframe / fps_video

            self.frames = []
            videodata = skvideo.io.vreader(video_path)
            # fps_desired = 2
            drop_extra_frames = fps_video/self.FPS

            for i_frame, frame in tqdm(enumerate(videodata), total=numframe):
                # print(i_frame % drop_extra_frames)
                if start is not None:
                    if i_frame < fps_video * start:
                        continue

                if duration is not None:
                    if i_frame > fps_video * (start + duration):
                        # print("end of duration :)")
                        continue

                if (i_frame % drop_extra_frames < 1):

                    if self.transform == "resize256crop224":  # crop keep the central square of the frame
                        frame = imutils.resize(
                            frame, height=256)  # keep aspect ratio
                        # number of pixel to remove per side
                        off_side_h = int((frame.shape[0] - 224)/2)
                        off_side_w = int((frame.shape[1] - 224)/2)
                        frame = frame[off_side_h:-off_side_h,
                                        off_side_w:-off_side_w, :]  # remove them

                    elif self.transform == "crop":  # crop keep the central square of the frame
                        frame = imutils.resize(
                            frame, height=224)  # keep aspect ratio
                        # number of pixel to remove per side
                        off_side = int((frame.shape[1] - 224)/2)
                        frame = frame[:, off_side:-
                                        off_side, :]  # remove them

                    elif self.transform == "resize":  # resize change the aspect ratio
                        # lose aspect ratio
                        frame = cv2.resize(frame, (224, 224),
                                            interpolation=cv2.INTER_CUBIC)

                    # else:
                    #     raise NotImplmentedError()
                    # if self.array:
                    #     frame = img_to_array(frame)
                    self.frames.append(frame)

            print("expected number of frames", numframe,
                  "real number of available frames", i_frame+1)

            if numframe == i_frame+1:
                print("===>>> proper read! Proceeding! :)")
                good_number_of_frames = True
            else:
                print("===>>> not read properly... Read frames again! :(")
                numframe = i_frame+1
        
        self.frames = np.array(self.frames)

    def __len__(self):
        return len(self.listGame)

    def __iter__(self, index):
        return self.frames[index]
    
    # def frames(self):

# class VideoLoader():
#     def __init__(self, SoccerNetDir, split="v1"):
#         self.SoccerNetDir = SoccerNetDir
#         self.split = split
#         # if split == "v1":
#         #     self.listGame = getListGames("v1")
#         # # elif split == "challenge":
#         # #     self.listGame = getListGames()
#         # else:
#         self.listGame = getListGames(split)

#     def __len__(self):
#         return len(self.listGame)

#     def __iter__(self, index):
#         video_path = self.listGame[index]

#         # Read RELIABLE lenght for the video, in second
#         if args.verbose:
#             print("video path", video_path)
#         v = cv2.VideoCapture(video_path)
#         v.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
#         time_second = v.get(cv2.CAP_PROP_POS_MSEC)/1000
#         if args.verbose:
#             print("duration video", time_second)
#         import json
#         metadata = skvideo.io.ffprobe(video_path)
#         # print(metadata.keys())
#         # print(json.dumps(metadata["video"], indent=4))
#         # getduration
#         # print(metadata["video"]["@avg_frame_rate"])
#         # # print(metadata["video"]["@duration"])

#         # Knowing number of frames from FFMPEG metadata w/o without iterating over all frames
#         videodata = skvideo.io.FFmpegReader(video_path)
#         (numframe, _, _, _) = videodata.getShape()  # numFrame x H x W x channels
#         if args.verbose:
#             print("shape video", videodata.getShape())

#         # # extract REAL FPS
#         fps_video = metadata["video"]["@avg_frame_rate"]
#         fps_video = float(fps_video.split("/")[0])/float(fps_video.split("/")[1])
#         # fps_video = numframe/time_second
#         if args.verbose:
#             print("fps=", fps_video)
#         time_second = numframe / fps_video
#         if args.verbose:
#             print("duration video", time_second)
#         frames = []
#         videodata = skvideo.io.vreader(video_path)
#         fps_desired = 2
#         drop_extra_frames = fps_video/fps_desired
#         for i_frame, frame in tqdm(enumerate(videodata), total=numframe):
#             # print(i_frame % drop_extra_frames)
#             if (i_frame % drop_extra_frames < 1):

#                 if args.preprocess == "resize256crop224":  # crop keep the central square of the frame
#                     frame = imutils.resize(frame, height=256)  # keep aspect ratio
#                     # number of pixel to remove per side
#                     off_side_h = int((frame.shape[0] - 224)/2)
#                     off_side_w = int((frame.shape[1] - 224)/2)
#                     frame = frame[off_side_h:-off_side_h,
#                                 off_side_w:-off_side_w, :]  # remove them

#                 elif args.preprocess == "crop":  # crop keep the central square of the frame
#                     frame = imutils.resize(frame, height=224)  # keep aspect ratio
#                     # number of pixel to remove per side
#                     off_side = int((frame.shape[1] - 224)/2)
#                     frame = frame[:, off_side:-off_side, :]  # remove them

#                 elif args.preprocess == "resize":  # resize change the aspect ratio
#                     # lose aspect ratio
#                     frame = cv2.resize(frame, (224, 224),
#                                     interpolation=cv2.INTER_CUBIC)

#                 else:
#                     raise NotImplmentedError()
#                 frames.append(frame)

#         # create numpy aray (nb_frames x 224 x 224 x 3)
#         frames = np.array(frames)
#         return frames
