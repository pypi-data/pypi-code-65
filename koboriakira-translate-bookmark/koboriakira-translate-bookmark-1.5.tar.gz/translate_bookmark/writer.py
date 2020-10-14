import os
import csv
from typing import List, Dict, Any
from googletrans import Translator
from translate_bookmark.url import Url

FILENAME_ALL = 'all.csv'
FILENAME_NGSL = 'ngsl.csv'
FILENAME_NOT_NGSL = 'not_ngsl.csv'

translator = Translator()


def write_csv(result: Dict[str, Any], url: Url, use_translate: bool):
    dir_name = _create_folder(url=url.url)
    morphied_word_dict: Dict[str, int] = result['morphied_word_dict']

    with open(f'{dir_name}/{FILENAME_ALL}', mode='w') as f:
        writer = csv.writer(f)
        for word, count in morphied_word_dict.items():
            writer.writerow([word, count])

    with open(f'{dir_name}/{FILENAME_NGSL}', mode='w') as f:
        writer = csv.writer(f)
        ngsl_word_list: List[str] = result['ngsl_word_list']
        for word in ngsl_word_list:
            writer.writerow([word, morphied_word_dict[word]])

    with open(f'{dir_name}/{FILENAME_NOT_NGSL}', mode='w') as f:
        writer = csv.writer(f)
        not_ngsl_word_list = result['not_ngsl_word_list']
        for word in not_ngsl_word_list:
            if use_translate:
                ja = _translate(word=word)
                count = morphied_word_dict[word]
                writer.writerow([word, ja, count])
            else:
                count = morphied_word_dict[word]
                writer.writerow([word, count])


def _create_folder(url: str) -> str:
    splited_url = url.split('/')
    folder_name = ''
    if splited_url[len(splited_url) - 1] == '':
        folder_name = splited_url[len(splited_url) - 2]
    else:
        folder_name = splited_url[len(splited_url) - 1]
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def _translate(word: str) -> str:
    try:
        return translator.translate(word, dest="ja").text
    except Exception:
        return ''
