from collections import defaultdict
from datetime import datetime
import glob
import hashlib
import os
import shutil

from PIL import ExifTags, Image
from yaspin import yaspin

ALLOWED_EXTENSIONS = (
    'png',
    'jpeg',
    'jpg',
    'mov',
    'mp4',
    'm4v',
)


def _created_datetime_from_file(f):
    if _file_ext(f) in ('jpg', 'jpeg'):
        with Image.open(f) as img:
            exif = img._getexif()
            # some JPGS will be missing EXIF header data and thus a datetime of
            # the file creation can't be extracted.
            if exif is not None:
                tags = {
                    ExifTags.TAGS[k]: v
                    for k, v in exif.items()
                    if k in ExifTags.TAGS
                }
                # some JPG files might be missing the particular datetime EXIF tag
                # we need and so the file creation date can't be extracted.
                if 'DateTimeOriginal' in tags:
                    # JPEG EXIF datetimes are formatted like 2020:10:04 10:18:05
                    return datetime.strptime(tags['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    # if nothing else worked we default to st_birthtime, which is OSX-specific.
    # when portability matters, read https://stackoverflow.com/a/39501288/765705
    return datetime.fromtimestamp(os.stat(f).st_birthtime)


def _make_file_index(files):
    file_index = defaultdict(dict)
    for f in files:
        h = hashlib.new('md5')
        with open(f, 'rb') as media:
            h.update(media.read())
        file_index[f]['created'] = _created_datetime_from_file(f)
        file_index[f]['md5'] = h.hexdigest()
    return file_index


def _make_month_index(file_index):
    month_index = defaultdict(list)
    for f, i in file_index.items():
        month_index[i['created'].strftime('%Y_%m')].append(
            {'file': f, 'created': i['created'], 'md5': i['md5']}
        )
    return month_index


def _make_duplicate_index(file_index):
    """
    Makes an index of files that have an exact content duplicate.
    Reurns a dict with the md5 as key and duplicate files list as values.
    """
    duplicate_index = defaultdict(list)
    for f, i in file_index.items():
        duplicate_index[i['md5']].append({'file': f, 'created': i['created']})

    # only return those with proper duplicates.
    return {k: v for k, v in duplicate_index.items() if len(v) > 1}


def _ensure_dir(name):
    if not os.path.isdir(name):
        # enforces removal of non-dir files.
        shutil.rmtree(name, ignore_errors=True)
        os.mkdir(name)


def _dst_fname(f):
    fname = f['created'].strftime('%Y_%m_%d_%H_%M_%S_')
    fname += f['md5'][
        :8
    ]  # first 8 bytes of MD5 (is enough?) to exclude conflicts on the same second.
    ext = _file_ext(f['file'])
    return fname + '.' + ext


def _has_md5(f, md5):
    h = hashlib.new('md5')
    with open(f, 'rb') as media:
        h.update(media.read())
    return h.hexdigest() == md5


def _file_ext(f):
    return f.split('.')[-1].lower()


def _sort(month_index, duplicate_index):
    for dirname in month_index:
        _ensure_dir(dirname)
        for f in month_index[dirname]:
            dst = os.path.join(dirname, _dst_fname(f))
            if os.path.exists(dst) and _has_md5(dst, f['md5']):
                continue
            shutil.move(f['file'], dst)


def run(args):
    sp = yaspin()
    sp.color = 'blue'
    sp.start()
    sp.text = "searching for media files..."
    files = glob.glob('**/*.*', recursive=True)
    eligible_files = [f for f in files if _file_ext(f) in ALLOWED_EXTENSIONS]
    sp.write(f"> found {len(eligible_files)} media files.")
    sp.text = "creating media file indexes..."
    file_index = _make_file_index(eligible_files)
    month_index = _make_month_index(file_index)
    duplicate_index = _make_duplicate_index(file_index)
    duplicate_count = sum(len(v) for v in duplicate_index.values())
    sp.write(f"> found {duplicate_count} duplicated media files.")
    sp.text = "sorting media files..."
    _sort(month_index, duplicate_index)
    # sp.red.fail("✘")
    sp.text = 'success!'
    sp.green.ok("✔")
