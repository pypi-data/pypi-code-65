# import the necessary packages
import cv2
from devai import Path
from tqdm import tqdm
import fire


def convert_one(video_file):
    vidcap = cv2.VideoCapture(str(video_file))

    output_path = video_file.parent/video_file.stem
    output_path.mkdir(exist_ok=True)

    success, image = vidcap.read()  # success is True when frame is extracted correctly
    count = 0

    while success:
        frame_num = f"frame_{count}"
        cv2.imwrite(str(output_path/frame_num)+".jpg",
                    image)     # save frame as JPEG file

        success, image = vidcap.read()  # changing success, image for the next iteration
        count += 1


def videos_to_frames_converter(input_path, include=["avi", "mp4", "mov", "wmv", "mkv", "flv", "mpg"]):
    input_path = Path(input_path)
    assert input_path.exists(), f"Not a valid path, {str(input_path)}"

    if input_path.is_file():
        print(f"starting frames conversion of {str(input_path)}")
        convert_one(input_path)
        print(f"finished frames conversion of {str(input_path)}")
    else:
        for video_file in tqdm(input_path.ls(include=include)):
            convert_one(Path(video_file))


if __name__ == "__main__":
    fire.Fire(videos_to_frames_converter)
