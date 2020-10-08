from guessit import guessit
import sys


class Video:
    def __init__(self, file):
        guess = guessit(file, "-s")
        self.year = ""
        if (guess["type"]) == "episode":
            self.main = str(guess["title"]).replace(" ", "+")
            self.season = "{:02d}".format(int(guess["season"]))
            self.episode = "{:02d}".format(int(guess["episode"]))
            self.source = guess.get("source", "")
            self.codec = guess.get("video_codec", "")
            self.audio = guess.get("audio_codec", "")
            self.resolution = guess.get("screen_size", "")
            self.busqueda = "%s+S%sE%s" % (self.main, self.season, self.episode)
        else:
            self.busqueda = str(guess["title"]).replace(" ", "+")
            try:
                self.year = guess["year"]
            except KeyError:
                sys.exit(
                    "Tu video no tiene información suficiente para una "
                    "búsqueda automática"
                )
            self.source = guess.get("source", "")
            self.codec = guess.get("video_codec", "")
            self.audio = guess.get("audio_codec", "")
            self.resolution = guess.get("screen_size", "")

    def get_keywords(self):
        sources = {
            "Blu-ray": [
                "bluray",
                "blu-ray",
                "bdrip",
                "bd-rip",
                "brrip",
                "br-rip",
                "blu ray",
                "bdrip",
            ],
            "DVD": ["dvdrip", ".dvd.", "dvd-r", "ntsc", " dvd ", " pal "],
            "Web": [
                "web-dl",
                "web-rip",
                "webdl",
                " web ",
                ".web.",
                ".web",
                "web.",
                "webrip",
            ],
            "HDTV": ["hdtv", "screen-tv", "hc-rip"],
            "": [],
        }

        codecs = {
            "H.264": ["264", "avc"],
            "H.265": ["265", "hevc"],
            "Divx": [" divx ", ".divx.", "-divx"],
            "Xvid": ["xvid"],
            "DVDivX": ["DVDivx"],
            "VP7": ["vp7"],
            "VP9": ["vp9"],
            "": [],
        }

        audio_codecs = {
            "Dolby Digital": ["dolby", ".dd", "-dd", "dd-", "d.d", " dd ", "ac3"],
            "Dolby Digital Plus": ["dolby", ".dd", "-dd", "dd-", "d.d", " dd ", "ac3"],
            "FLAC": ["flac", "lossless"],
            "AAC": [" aac ", ".aac", "aac.", "-aac", "aac-"],
            "DTS": ["dts"],
            "EAC3": ["EAC3"],
            "LPCM": ["LPCM"],
            "MP3": ["mp3"],
            "MP2": ["MP2"],
            "Opus": ["Opus"],
            "PCM": ["PCM"],
            "Vorbis": ["Vorbis"],
            "": [],
        }

        resolutions = {
            "1080p": ["1080", "720", "576", "4k", "2k", "full hd"],
            "720p": ["1080", "720", "576", "4k", "2k", "full hd"],
            "576p": ["1080", "720", "576", "4k", "2k", "full hd"],
            "480p": ["480", "360"],
            "2160p": ["4k, 2160p"],
            "": [],
        }

        return {
            "year": "({})".format([self.year]),
            "resol": resolutions[self.resolution],
            "source": sources[self.source],
            "audio": audio_codecs[self.audio],
            "codec": codecs[self.codec],
        }
