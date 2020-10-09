
from pathlib import Path
import json
import os
try:
    import skvideo.io
except:
    pass
# import moviepy.editor

def getListGames(split="v1"):

    #  if single split, convert into a list
    if not isinstance(split, list):
        split = [split]
    
    # if an element is "v1", convert to  train/valid/test
    if "all" in split:
        split = ["train", "valid", "test", "challenge"]
    if "v1" in split:
        split.pop(split.index("v1"))
        split.append("train")
        split.append("valid")
        split.append("test")

    listgames = []
    # loop over splits
    for spl in split: 
        if spl == "train":
            jsonGamesFile = Path(__file__).parent / "data/SoccerNetGamesTrain.json"
        elif spl == "valid":
            jsonGamesFile = Path(__file__).parent / "data/SoccerNetGamesValid.json"
        elif spl == "test":
            jsonGamesFile = Path(__file__).parent / "data/SoccerNetGamesTest.json"
        elif spl == "challenge":
            jsonGamesFile = Path(__file__).parent / "data/SoccerNetGamesChallenge.json"

        with open(jsonGamesFile, "r") as json_file:
            dictionary = json.load(json_file)

        for championship in dictionary:
            for season in dictionary[championship]:
                for game in dictionary[championship][season]:

                    listgames.append(os.path.join(championship, season, game))
                    
    return listgames


def getDuration(video_path):
    # metadata = skvideo.io.ffprobe(video_path)
    # print(video_path)
    # print("meta video", metadata["video"]["tag"])
    # print("meta audio", metadata["audio"]["tag"])
    # time_second = 0
    # try:
    #     # prioritize "video" "tag" "DURATION" metadata if readily available
    #     for entry in metadata["audio"]["tag"]:
    #         print("audio entry", list(entry.items()))
    #         if list(entry.items())[0][1] == "DURATION":
                
    #             duration = list(entry.items())[1][1].split(":")
    #             # print(duration)
    #             time_second = int(duration[0])*3600 + \
    #                 int(duration[1])*60 + float(duration[2])
    # except:
    #     pass

    # # read "@duration" metadata if availabel
    # try:
    #     time_second = float(metadata["video"]["@duration"])
    # except:
    #     pass

    # try:
    #     # prioritize "video" "tag" "DURATION" metadata if readily available
    #     for entry in metadata["video"]["tag"]:
    #         # print("video entry", list(entry.items()))
    #         if list(entry.items())[0][1] == "DURATION":
                
    #             duration = list(entry.items())[1][1].split(":")
    #             # print(duration)
    #             time_second = int(duration[0])*3600 + \
    #                 int(duration[1])*60 + float(duration[2])
    # except:
    #     pass
    # # print("duration video", time_second, video_path)
    # if abs(time_second - moviepy.editor.VideoFileClip(video_path).duration)>0.034:
    #     print(video_path)
    #     print("time_second", time_second)        
    #     print("moviepy", moviepy.editor.VideoFileClip(video_path).duration)    
        # assert False 
    time_second = moviepy.editor.VideoFileClip(video_path).duration
    return time_second

if __name__ == "__main__":
    print(len(getListGames(["v1", "challenge"])))
