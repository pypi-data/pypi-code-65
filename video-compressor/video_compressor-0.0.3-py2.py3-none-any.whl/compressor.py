

def compressToTargetSize(video, targetSize, output):

    length = video.getDuration() / 1000
    total_bitrate = targetSize / (length+1)
    audio_bitrate = video.getAudioBitrate()
    video_bitrate = total_bitrate - audio_bitrate

    video.bitrate(video_bitrate).export(output)

