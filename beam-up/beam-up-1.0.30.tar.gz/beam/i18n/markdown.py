import os
import re
import sys
import logging
import traceback

from .helpers.hash import hash
from .helpers.translate import translate, FileCache
from .helpers.languages import get_source_and_target_languages
from .helpers.serialize import serialize_text, deserialize_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("")

def parse_into_blocks(content):
    """
    - We parse Markdown into individual lines
    - If we encounter special ignoretags, we ignore everything inside them
    """
    lines = content.split("\n")
    blocks = []
    ignore_text = ""
    ignore = False
    for line in lines:
        if (not ignore) and re.match(r"^\s*<\!--translate:ignore-->\s*$", line):
            ignore = True
            continue
        elif ignore and re.match(r"<\!--translate:ignore-->\s*$", line):
            blocks.append({'type': 'ignore', 'text' : ignore_text})
            ignore = False
            ignore_text = ""
            continue
        # we ignore everything inside the 'ignore' block
        if ignore:
            ignore_text += line + "\n"
            continue
        blocks.append({'type': 'text', 'text': line})
    return blocks

def translate_file(token, source_path, destination_path, source_language, target_language, clean=False):
    count = 0

    with open(source_path) as input_file:
        content = input_file.read()

    cache = FileCache(source_path+".trans")

    blocks = parse_into_blocks(content)

    for i, block in enumerate(blocks):
        if block['type'] == 'text':
            source_text = serialize_text(block['text'])
            existing_translation = cache.get(source_text, target_language, source_language=source_language)
            if existing_translation is not None:
                # we already have translated this block
                block['translation'] = existing_translation
                continue
            count += len(source_text)
            translation = deserialize_text(translate(source_text, source_language, target_language, token))
            cache.set(source_text, target_language, translation, source_language=source_language)
            block['translation'] = translation

    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    with open(destination_path, "w") as output_file:
        for block in blocks:
            if block['type'] == 'text':
                output_file.write(block['translation']+"\n")
            elif block['type'] == 'ignore':
                output_file.write(block['text']+"\n")

    if clean:
        cache.clean()

    return count

def translate_markdown(token, src_path, clean=False, match=None):
    match_path = os.path.abspth(match) if match is not None else None
    source_language, target_languages = get_source_and_target_languages(src_path)

    logger.info(f"Translating from '{source_language}' to '{', '.join(target_languages)}'...")
    language_src_path = os.path.join(src_path, source_language)
    for root, dirs, files in os.walk(language_src_path):
        for filename in files:
            if filename.endswith(".md"):
                source_path = os.path.join(root, filename)
                if match_path is not None and match_path != source_path:
                    continue
                elif match_path is not None:
                    print(f"Matched: '{source_path}'")
                for target_language in target_languages:
                    destination_path = os.path.join(src_path, target_language,
                        os.path.relpath(source_path, language_src_path))
                    count = translate_file(token, source_path, destination_path, source_language, target_language, clean=clean)
                    if count:
                        print(f"Translated {count} characters in file {source_path}")
