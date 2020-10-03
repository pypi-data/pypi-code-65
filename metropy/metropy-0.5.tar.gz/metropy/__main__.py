import threading

try:
    from pkg_resources import resource_filename
except:
    # Fallback (will fail loading, but at least does not raise exception)
    def resource_filename(*args, **kwargs):
        return None

import time
import wave
from typing import Optional

import pyaudio
import argparse
import curses
import sys


audio: Optional[pyaudio.PyAudio] = None


def init_audio():
    global audio
    audio = pyaudio.PyAudio()


def destroy_audio():
    global audio
    if audio:
        audio.terminate()


def load_wav(path):
    return wave.open(path, "rb")


def resolve_filename(pkg: str, res: str) -> str:
    """ Reads the content of the file 'res' from the resources of the package """
    return resource_filename(pkg, res)


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)


class StoppableThread(threading.Thread):
    s_tag = 0
    def __init__(self, metronome, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metronome = metronome
        self.bpm = self.metronome.bpm
        self.beats = self.metronome.beats
        self.bar_sound = self.metronome.bar_sound
        self.beat_sound = self.metronome.beat_sound
        self._stop_event = threading.Event()
        self._tag = StoppableThread._next_tag()

    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def run(self) -> None:
        DELTA_S = 60 / self.bpm

        current_beat = 0

        while not self.is_stopped():
            with self.metronome.lock:
                if not self.metronome.playing:
                    break

                # Use bar_sound or beat_sound depending on the current beat count
                sound = self.bar_sound if current_beat == 0 else self.beat_sound

                # Rewind to the begin
                sound.rewind()

                # Open stream
                stream = audio.open(
                    format=audio.get_format_from_width(sound.getsampwidth()),
                    channels=sound.getnchannels(),
                    rate=sound.getframerate(),
                    output=True
                )

                last_t = time.time_ns()

                # Play
                while True:
                    data = sound.readframes(1024)

                    if len(data) <= 0:
                        break

                    if self.is_stopped():
                        break

                    stream.write(data)

                # t_end = time.time_ns()

            # Stop
            stream.stop_stream()
            stream.close()

            # Schedule next playing
            current_beat = (current_beat + 1) % self.beats

            time.sleep(DELTA_S - (time.time_ns() - last_t) * 1e-9)

    @staticmethod
    def _next_tag():
        StoppableThread.s_tag = StoppableThread.s_tag + 1
        return StoppableThread.s_tag


class Metronome:
    def __init__(self, bar_sound, beat_sound, bpm=60, beats=4):
        self.bar_sound = bar_sound
        self.beat_sound = beat_sound
        self.playing = False
        self.bpm = bpm
        self.beats = beats
        self.lock = threading.Lock()

        self._current_thread: Optional[StoppableThread] = None

    def toggle(self):
        self.playing = not self.playing
        self._invalidate()

    def start(self):
        self.playing = True
        self._invalidate()

    def stop(self, clean=True):
        self.playing = False
        self._invalidate(clean=clean)

    def increase_bpm(self, amount=1):
        self.bpm = self.bpm + amount
        self._invalidate()

    def set_beats(self, beats):
        self.beats = beats
        self._invalidate()

    def _invalidate(self, clean=False):
        if not self._current_thread and not self.playing:
            pass

        elif self._current_thread and self.playing:
            self._current_thread.stop()
            if clean:
                self._current_thread.join()
            self._start()

        elif not self._current_thread and self.playing:
            self._start()

        elif self._current_thread and not self.playing:
            self._current_thread.stop()
            if clean:
                self._current_thread.join()
            self._current_thread = None

    def _start(self):
        self._current_thread = StoppableThread(metronome=self)
        self._current_thread.start()

class UI:
    # Main
    MAIN_WIN_INFO_COL_WIDTH = 10

    # Help
    HELP_WIN_SPACE_FROM_CENTER = 2
    HELP_WIN_PADDING_X = 4
    HELP_WIN_PADDING_Y = 1

    HELP_WIN_INFOS = [
        ("SPACE", "start/stop the metronome"),
        ("UP", "decrease bpm by 5"),
        ("DOWN", "increase bpm by 5"),
        ("LEFT", "decrease bpm by 1"),
        ("RIGHT", "increase bpm by 1"),
        ("1/2/3/4/5/6/7/8/9", "change the beats per bar"),
        ("d", "show/hide bpm detector"),
        ("h", "show/hide help"),
        ("q", "quit"),
    ]

    HELP_WIN_HEIGHT = len(HELP_WIN_INFOS) + 2 * HELP_WIN_PADDING_Y + 2
    HELP_WIN_WIDTH = max(len(i[0]) + len(i[1]) for i in HELP_WIN_INFOS) + \
                    2 * HELP_WIN_SPACE_FROM_CENTER + 2 * HELP_WIN_PADDING_X + 2
    HELP_WIN_WIDTH_HALF = HELP_WIN_WIDTH // 2

    # Detector
    DETECTOR_WIN_INFOS = [
        ("SPACE", "detect a beat"),
        ("ENTER", "complete detection"),
    ]
    DETECTOR_WIN_SPACE_FROM_CENTER = 2
    DETECTOR_WIN_PADDING_Y = 0
    DETECTOR_WIN_PADDING_X = 20

    DETECTOR_WIN_HEIGHT = 10
    DETECTOR_WIN_WIDTH = max(len(i[0]) + len([1]) for i in DETECTOR_WIN_INFOS) + \
                    2 * DETECTOR_WIN_SPACE_FROM_CENTER + 2 * DETECTOR_WIN_PADDING_X + 2
    DETECTOR_WIN_WIDTH_HALF = DETECTOR_WIN_WIDTH // 2

    # Colors
    GREEN_ON_BLACK = 1
    RED_ON_BLACK = 2
    CYAN_ON_BLACK = 3
    BLACK_ON_WHITE = 4
    WHITE_ON_GREEN = 5
    WHITE_ON_RED = 6
    WHITE_ON_CYAN = 7

    def __init__(self, metronome):
        self._metronome = metronome

        self._wmain = None
        self._wmain_width = None
        self._wmain_height = None

        self._whelp = None
        self._wdetector = None

        self._current_window = None

        self._detection_start_time = None
        self._detection_end_time = None
        self._detection_beats = 0
        self._detection_last_beat_time = None

    def start(self):
        curses.wrapper(self._start)

    def _start(self, main_win):
        self._wmain = main_win
        self._wmain_height, self._wmain_width = self._wmain.getmaxyx()
        self._current_window = self._wmain
        self._init()
        self._main_loop()
        self._metronome.stop()

    def _init(self):
        # Clear and refresh the screen for a blank canvas
        self._wmain.clear()
        self._wmain.refresh()

        # Hide the blinking cursor
        curses.curs_set(0)

        # Start colors in curses
        curses.start_color()
        curses.init_pair(UI.GREEN_ON_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(UI.RED_ON_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(UI.CYAN_ON_BLACK, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(UI.BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(UI.WHITE_ON_GREEN, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(UI.WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(UI.WHITE_ON_CYAN, curses.COLOR_WHITE, curses.COLOR_CYAN)

    def _main_loop(self):
        while True:
            # Wait for next input
            self._update_current_window()
            if not self._handle_key(self._current_window.getch()):  # automatically call refresh() too
                break

    def _handle_key(self, key) -> bool:
        # eprint("Input:", key)

        # Common
        if key == ord("q"):
            return False
        elif key == ord("h"):
            self._toggle_sub_window("help", self._create_help_win)
        elif key == ord("d"):
            self._toggle_sub_window("detector",
                                    creator=self._create_detector_win,
                                    cleanup=self._cleanup_detector)

        if self._is_atop(self._wdetector):
            def newbeat():
                self._detection_last_beat_time = time.time_ns()
                self._detection_beats += 1

            if key == ord(" "):
                if not self._is_detecting() or self._is_detection_completed():
                    self._cleanup_detector()
                    self._detecting = True
                    self._detection_start_time = time.time_ns()
                newbeat()

            if key == ord("\n") and self._is_detecting():
                newbeat()
                self._detection_end_time = time.time_ns()
                self._detecting = False
        else:
            # Main/Help
            if key == ord(" "):
                self._metronome.toggle()
            elif key == curses.KEY_RIGHT:
                self._metronome.increase_bpm(1)
            elif key == curses.KEY_LEFT:
                self._metronome.increase_bpm(-1)
            elif key == curses.KEY_UP:
                self._metronome.increase_bpm(5)
            elif key == curses.KEY_DOWN:
                self._metronome.increase_bpm(-5)
            elif ord("1") <= key <= ord("9"):
                self._metronome.set_beats(int(chr(key)))

        return True

    def _is_atop(self, window) -> bool:
        return self._current_window == window

    def _is_detecting(self) -> bool:
        return self._detection_start_time is not None and self._detection_beats > 0

    def _is_detection_completed(self) -> bool:
        return self._is_detecting() and self._detection_end_time is not None

    def _cleanup_detector(self):
        self._detection_start_time = None
        self._detection_end_time = None
        self._detection_beats = 0
        self._detection_last_beat_time = None

    def _update_current_window(self, update_main_anyway=True):
        if update_main_anyway or self._is_atop(self._wmain):
            self._update_wmain()

        if self._is_atop(self._whelp):
            self._update_whelp()
        elif self._is_atop(self._wdetector):
            self._update_wdetector()

    def _update_wmain(self):
        self._wmain.clear()
        y_cursor = 0

        # Status bar
        status = "Playing" if self._metronome.playing else "Stopped"
        status_color = UI.WHITE_ON_GREEN if self._metronome.playing else UI.WHITE_ON_RED
        half1 = self._wmain_width // 2 - len(status) // 2
        half2 = self._wmain_width - half1 - len(status)
        self._addstr(self._wmain, y_cursor, 0, " " * half1 + status + " " * half2, status_color, bold=True)
        y_cursor += 2
        # Metronome info

        # - bpm
        bpm_string = f"{'BPM'.ljust(UI.MAIN_WIN_INFO_COL_WIDTH)}"
        self._addstr(self._wmain, y_cursor, 0, bpm_string, bold=True)
        self._addstr(self._wmain, y_cursor, len(bpm_string), f"{self._metronome.bpm}")
        y_cursor += 1

        # - beats
        beat_string = f"{'Beats'.ljust(UI.MAIN_WIN_INFO_COL_WIDTH)}"
        self._addstr(self._wmain, y_cursor, 0, beat_string, bold=True)
        self._addstr(self._wmain, y_cursor, len(beat_string), f"{self._metronome.beats}/4")
        y_cursor += 1

        # Bottom bar
        status_bar = f"Press d for {'hide' if self._is_atop(self._wdetector) else 'show'} detector"
        self._addstr(self._wmain, self._wmain_height - 2, 0,
                          status_bar + " " * (self._wmain_width - len(status_bar) - 1),
                          UI.BLACK_ON_WHITE)

        status_bar = f"Press h for {'hide' if self._is_atop(self._whelp) else 'show'} help"
        self._addstr(self._wmain, self._wmain_height - 1, 0,
                          status_bar + " " * (self._wmain_width - len(status_bar) - 1),
                          UI.BLACK_ON_WHITE)

        self._wmain.refresh()

    def _update_whelp(self):
        if not self._whelp:
            return

        self._whelp.clear()
        self._whelp.box(0, 0)

        y_cursor = 1 + UI.HELP_WIN_PADDING_Y

        # Content
        for (info_key, info_str) in UI.HELP_WIN_INFOS:
            self._addstr(self._whelp, y_cursor, UI.HELP_WIN_WIDTH_HALF - len(info_key) - UI.HELP_WIN_SPACE_FROM_CENTER - 1,
                         info_key, UI.CYAN_ON_BLACK)
            self._addstr(self._whelp, y_cursor, UI.HELP_WIN_WIDTH_HALF + UI.HELP_WIN_SPACE_FROM_CENTER - 1,
                         info_str, UI.CYAN_ON_BLACK)
            y_cursor += 1

    def _update_wdetector(self):
        if not self._wdetector:
            return

        self._wdetector.clear()
        self._wdetector.box(0, 0)

        # Borders
        y_cursor = 1 + UI.DETECTOR_WIN_PADDING_Y

        # Status bar
        if not self._is_detecting():
            status = "Not detecting"
            status_color = UI.WHITE_ON_RED
        else:
            if self._is_detection_completed():
                status = "Detection completed"
                status_color = UI.WHITE_ON_GREEN
            else:
                status = f"Detecting... ({self._detection_beats})"
                status_color = UI.WHITE_ON_CYAN

        detector_width = UI.DETECTOR_WIN_WIDTH - 2
        half1 = detector_width // 2 - len(status) // 2
        half2 = detector_width - half1 - len(status)
        self._addstr(self._wdetector, 1, 1, " " * half1 + status + " " * half2, status_color, bold=True)
        y_cursor += 2

        # Content
        if not self._is_detecting():
            for (info_key, info_str) in UI.DETECTOR_WIN_INFOS:
                self._addstr(self._wdetector, y_cursor,
                             UI.DETECTOR_WIN_WIDTH_HALF - len(info_key) - UI.DETECTOR_WIN_SPACE_FROM_CENTER - 1,
                             info_key, UI.CYAN_ON_BLACK)
                self._addstr(self._wdetector, y_cursor, UI.DETECTOR_WIN_WIDTH_HALF + UI.DETECTOR_WIN_SPACE_FROM_CENTER - 1,
                             info_str, UI.CYAN_ON_BLACK)
                y_cursor += 1
        else:
            # estimated BPM
            if self._detection_beats >= 2:
                estimated_bpm = int(60 * (self._detection_beats - 1) / \
                                ((self._detection_last_beat_time - self._detection_start_time) * 1e-9))
                estimated_bpm_string = "Estimated BPM     "
                self._addstr(self._wdetector, y_cursor, 2, estimated_bpm_string, bold=True)
                self._addstr(self._wdetector, y_cursor, 2 + len(estimated_bpm_string), f"{estimated_bpm}")

    def _create_help_win(self):
        helpwin = curses.newwin(UI.HELP_WIN_HEIGHT, UI.HELP_WIN_WIDTH,
                                (self._wmain_height // 2) - UI.HELP_WIN_HEIGHT // 2,
                                (self._wmain_width // 2) - UI.HELP_WIN_WIDTH // 2)
        helpwin.keypad(True)

        return helpwin


    def _create_detector_win(self):
        detectorwin = curses.newwin(UI.DETECTOR_WIN_HEIGHT, UI.DETECTOR_WIN_WIDTH,
                                    (self._wmain_height // 2) - UI.DETECTOR_WIN_HEIGHT // 2,
                                    (self._wmain_width // 2) - UI.DETECTOR_WIN_WIDTH // 2)
        detectorwin.keypad(True)

        return detectorwin

    def _toggle_sub_window(self, name, creator, cleanup=None):
        window_name = f"_w{name}"
        if self._is_atop(getattr(self, window_name)):
            self._destroy_window(getattr(self, window_name))
            self._current_window = self._wmain
            if cleanup:
                cleanup()
        else:
            self._current_window = creator()
            setattr(self, window_name, self._current_window)

    @classmethod
    def _destroy_window(cls, win):
        if not win:
            return
        win.clear()
        win.refresh()
        del win

    @classmethod
    def _addstr(cls, win, y, x, s, color_pair=None, bold=False):
        if color_pair:
            win.attron(curses.color_pair(color_pair))
        if bold:
            win.attron(curses.A_BOLD)
        win.addstr(y, x, s)
        if color_pair:
            win.attroff(curses.color_pair(color_pair))
        if bold:
            win.attroff(curses.A_BOLD)




def main():

    parser = argparse.ArgumentParser(
        description="Metronome with Terminal UI in ncurses."
    )

    # --bar <BAR_SOUND>
    parser.add_argument("--bar",
                        dest="bar", metavar="BAR_SOUND",
                        help="Path of the bar sound (.wav)")

    # --beat <BEAT_SOUND>
    parser.add_argument("--beat",
                        dest="beat", metavar="BEAT_SOUND",
                        help="Path of the beat sound (.wav)")

    # bpm // optioanl
    parser.add_argument("bpm",
                        nargs='?', default="60",
                        help="BPM (default is 60)")
    # beats // optioanl
    parser.add_argument("beats",
                        nargs='?', default="4",
                        help="Beats per bar (default is 4)")
    # Read args
    parsed = vars(parser.parse_args(sys.argv[1:]))

    def to_int_or_quit(obj):
        if obj is not None:
            try:
                return int(obj)
            except:
                eprint("Invalid parameter")
                exit(-1)

    bar = parsed.get("bar")
    beat = parsed.get("beat")
    bpm = to_int_or_quit(parsed.get("bpm", 60))
    beats = to_int_or_quit(parsed.get("beats", 4))

    bar_path = bar or resolve_filename("metropy.sounds", "bar.wav")
    beat_path = beat or resolve_filename("metropy.sounds", "beat.wav")

    bar_sound = None
    beat_sound = None

    print(f"Loading bar sound at '{bar_path}'")

    try:
        bar_sound = load_wav(bar_path)
    except:
        eprint("Failed to load bar sound, using default one")
        try:
            bar_sound = load_wav(resolve_filename("metropy.sounds", "bar.wav"))
        except:
            eprint("Failed to load bar sound, aborting")
            exit(1)

    print(f"Loading beat sound at '{beat_path}'")

    try:
        beat_sound = load_wav(beat_path)
    except:
        eprint("Failed to load beat sound, using default one")
        try:
            beat_sound = load_wav(resolve_filename("metropy.sounds", "beat.wav"))
        except:
            eprint("Failed to load beat sound, aborting")
            exit(1)

    metronome = Metronome(
        bar_sound=bar_sound,
        beat_sound=beat_sound,
        bpm=bpm,
        beats=beats
    )

    init_audio()
    UI(metronome).start()
    destroy_audio()

if __name__ == "__main__":
    main()