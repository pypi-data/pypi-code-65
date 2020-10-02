import sys
import os
import tempfile
from gtts import gTTS
from . import util

def say(sentence):
    import pyttsx
    engine = pyttsx.init()
    engine.say(sentence)
    engine.runAndWait()


def win_tts(sentence):
    import win32com.client as wincl
    speak = wincl.Dispatch("SAPI.SpVoice")
    speak.Speak(sentence)


def g_tts(sentence, save_path, lang='en', engine='mpg123'):
    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    try:
        filename = util.slugify(sentence) + ".mp3"
        mp3file = os.path.join(os.path.join(save_path, filename))
        if not os.path.exists(mp3file):
            tts = gTTS(text=sentence, lang=lang)
            tts.save(mp3file)
        if os.path.exists(mp3file):
            os.system('%s "%s"' % (engine, mp3file))
    except Exception as e:
        print(e)


def gtts_all_txt(dirpath):
    for d in os.listdir(dirpath):
        if d.endswith(".txt"):
            file = os.path.join(dirpath, d).replace("\\", "/")
            save_dir = file.replace(".txt", "")
            if os.path.exists(save_dir):
                continue
            os.makedirs(save_dir)
            with open(file, "r", encoding="utf-8") as f:
                lines = f.read()
                for line in lines:
                    if line or not line.startswith("#") or not line.startswith("-"):
                        g_tts(line, save_dir)


# python -m plugins.tts "apple"
if __name__ == "__main__":
    # win_tts(sys.argv[1])
    # , sys.argv[2]
    tmpdir = os.path.join('/tmp/tts')
    g_tts(sys.argv[1], tmpdir)
