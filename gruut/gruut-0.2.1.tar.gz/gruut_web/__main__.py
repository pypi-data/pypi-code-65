#!/usr/bin/env python3
"""Web server entry point"""
import hashlib
import heapq
import io
import logging
import subprocess
import tempfile
import time
import typing
import urllib.parse
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

import gruut
import gruut_ipa
import quart_cors
from quart import Quart, Response, render_template, request, send_from_directory

_DIR = Path(__file__).parent

_LOGGER = logging.getLogger("gruut_web")
logging.basicConfig(level=logging.DEBUG)

_LANGUAGES = {}

# -----------------------------------------------------------------------------

app = Quart("gruut_web")
app.secret_key = str(uuid4())

app.config["TEMPLATES_AUTO_RELOAD"] = True

app = quart_cors.cors(app)

# -----------------------------------------------------------------------------


@dataclass
class LookupResult:
    """Result from a word lookup"""

    phonemes: typing.List[gruut_ipa.Phoneme]

    def __post_init__(self):
        self._phonemes_text = ""
        self._espeak = ""

    @property
    def phonemes_text(self) -> str:
        """Get whitespace separated phoneme string"""
        if self._phonemes_text:
            return self._phonemes_text

        self._phonemes_text = " ".join(p.text for p in self.phonemes)
        return self._phonemes_text

    @property
    def espeak(self) -> str:
        """Get eSpeak phonemes for pronunciation"""
        if self._espeak:
            return self._espeak

        self._espeak = gruut_ipa.ipa_to_espeak(self.phonemes_text)
        return self._espeak


# -----------------------------------------------------------------------------


@app.route("/")
async def index():
    """Main page"""
    language_name = request.args.get("language")
    word = request.args.get("word", "").lower()

    gruut_lang = None
    results = []
    espeak_str = ""

    if language_name:
        # Load language
        gruut_lang = _LANGUAGES.get(language_name)
        if not gruut_lang:
            gruut_lang = gruut.Language.load(language_name)
            if gruut_lang:
                _LANGUAGES[language_name] = gruut_lang

    if gruut_lang and word:
        text_prons = gruut_lang.phonemizer.phonemize([word])

        # Get eSpeak phonemes
        espeak_cmd = ["espeak-ng", "-v", language_name, "-q", "-x", "--sep= ", word]
        _LOGGER.debug(espeak_cmd)
        espeak_str = subprocess.check_output(
            espeak_cmd, universal_newlines=True
        ).strip()

        for word_pron in text_prons[0]:
            word_phonemes = [gruut_ipa.Phoneme(p) for p in word_pron]
            results.append(LookupResult(phonemes=word_phonemes))

    return await render_template(
        "index.html",
        lang=language_name,
        word=word,
        results=results,
        espeak_str=espeak_str,
        time=time.time(),
        enumerate=enumerate,
        quote=urllib.parse.quote,
    )


# -----------------------------------------------------------------------------


@app.route("/api/speak-phone")
async def app_api_speak_phone():
    """WAV for IPA phone."""
    phone = request.args.get("phone")
    assert phone, "No phone"

    phoneme = gruut_ipa.Phoneme(phone)
    _LOGGER.debug("%s -> %s", phone, phoneme.to_string())

    wav_dir = _DIR / "wav"
    wav_path: typing.Optional[Path] = None
    if phoneme.vowel:
        height_str = phoneme.vowel.height.value
        placement_str = phoneme.vowel.placement.value
        rounded_str = "rounded" if phoneme.vowel.rounded else "unrounded"
        wav_path = wav_dir / f"{height_str}_{placement_str}_{rounded_str}_vowel.wav"
    elif phoneme.consonant:
        voiced_str = "voiced" if phoneme.consonant.voiced else "voiceless"
        place_str = phoneme.consonant.place.value.replace("-", "")
        type_str = phoneme.consonant.type.value.replace("-", "_")
        wav_path = wav_dir / f"{voiced_str}_{place_str}_{type_str}.wav"
        if not wav_path.is_file():
            # Try without voicing
            wav_path = wav_dir / f"{place_str}_{type_str}.wav"
    elif phoneme.schwa:
        if phoneme.schwa.r_coloured:
            # Close enough to "r" (er in corn[er])
            wav_path = wav_dir / f"alveolar_approximant.wav"
        else:
            # ə
            wav_path = wav_dir / f"mid-central_vowel.wav"

    assert wav_path, f"No WAV for {phone}"
    assert wav_path.is_file(), f"Missing {wav_path} for {phone}"
    wav_bytes = wav_path.read_bytes()

    return Response(wav_bytes, mimetype="audio/wav")


# -----------------------------------------------------------------------------


@app.route("/api/speak-phones")
async def app_api_speak_phones():
    """WAV for phonetic pronunciation."""
    language = request.args.get("lang", "en")
    phones = request.args.get("phones")
    assert phones, "No phones"

    espeak_str = gruut_ipa.espeak.ipa_to_espeak(phones)

    espeak_cmd = [
        "espeak-ng",
        "-v",
        language,
        "-s",
        "30",
        "--stdout",
        f"[[{espeak_str}]]",
    ]
    _LOGGER.debug(espeak_cmd)
    wav_bytes = subprocess.check_output(espeak_cmd)
    _LOGGER.debug("Got %s byte(s) of WAV data", len(wav_bytes))

    return Response(wav_bytes, mimetype="audio/wav")


# -----------------------------------------------------------------------------


@app.route("/api/speak-word")
async def app_api_speak_word():
    """WAV for word."""
    language = request.args.get("lang", "en")
    word = request.args.get("word")
    speed = request.args.get("speed", 30)
    assert word, "No word"

    espeak_cmd = ["espeak-ng", "-v", language, "-s", str(speed), "--stdout", word]
    _LOGGER.debug(espeak_cmd)
    wav_bytes = subprocess.check_output(espeak_cmd)
    _LOGGER.debug("Got %s byte(s) of WAV data", len(wav_bytes))

    return Response(wav_bytes, mimetype="audio/wav")


# -----------------------------------------------------------------------------


@app.route("/css/<path:filename>", methods=["GET"])
async def css(filename) -> Response:
    """CSS static endpoint."""
    return await send_from_directory(_DIR / "css", filename)


@app.route("/img/<path:filename>", methods=["GET"])
async def img(filename) -> Response:
    """Image static endpoint."""
    return await send_from_directory(_DIR / "img", filename)


@app.errorhandler(Exception)
async def handle_error(err) -> typing.Tuple[str, int]:
    """Return error as text."""
    _LOGGER.exception(err)
    return (f"{err.__class__.__name__}: {err}", 500)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
