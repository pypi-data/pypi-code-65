import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import logging
import pkg_resources
from pydub import AudioSegment
from pydub.playback import play
import tempfile
from typing import List

s3_client = boto3.client('s3')

BUCKET='dingpy'
PRE_LOADED_ALARMS = [
    'beep',
    'bell_tibetan',
    'birds',
    'clock_chimes',
    'computer_magic',
    'japanese_temple_bell',
    'music_box',
    'school_bell',
    'service_bell',
    'tinkle'
]

class MyAlarm(object):
    def __init__(self):
        self._sound = None


    def __str__(self):
        return f'DingPy MyAlarm Object (sound=\'{self._sound}\')'


    def _ding_from_library(self, sound) -> None:
        '''
        Read from local package directory to retrieve pre-loaded alarms.
        '''
        if sound in PRE_LOADED_ALARMS:
            self._sound = sound
            _local_tmp_path = pkg_resources.resource_filename(__name__, f'data/{sound}.mp3')
            alarm = AudioSegment.from_file(_local_tmp_path, format="mp3")
            play(alarm)
        else:
            logging.error(f'❌ Sound {sound} doesn\'t exist. Try using one of {PRE_LOADED_ALARMS}.')


    def _ding_from_local(self, path) -> None:
        '''
        Read from local directory and play the mp3 file.
        '''
        try:
            alarm = AudioSegment.from_file(path, format="mp3")
            play(alarm)
        except:
            logging.error(f'❌ Error loading audio file from directory {path}. Please use the absolute path.')


    def _ding_from_s3(self, sound) -> None:
        '''
        Download a mp3 file from s3 to a local temporary directory and plays the alarm.
        '''
        self._sound = sound
        # create a local temporary directory to save the downloaded audio file
        _local_tmp_path = f'{tempfile.mkdtemp()}/dingpy_{self._sound}.mp3'

        try:
            s3_client.download_file(
                Bucket=BUCKET,
                Key=f'{self._sound}.mp3',
                Filename=_local_tmp_path)
            alarm = AudioSegment.from_file(_local_tmp_path, format="mp3")
            play(alarm)
        except ClientError as e:
            logging.error(f'❌ Error downloading audio file {self._sound} from s3 bucket: {e}')


    @staticmethod
    def _list_alarms() -> None:
        '''
        Print a list of all available alarm sounds.
        '''
        alarm_files = _get_s3_keys(bucket=BUCKET)
        alarms = sorted([alarm[:-4] if alarm.endswith('mp3') else alarm for alarm in alarm_files])

        print('All available alarm sounds include: 🛎')
        for _ in alarms:
            print(f'- \'{_}\'')


    @staticmethod
    def _upload_alarm(file_path: str, sound_name : str) -> None:
        '''
        Allow user to upload a customized mp3 alarm to a public s3 bucket.

        Args:
            file_path: local path that contains the mp3 file.
            sound_name: name you want for your alarm, without the '.mp3' extension.
        '''
        # check if file is of mp3 type
        if not file_path.endswith('.mp3'):
            logging.error(f'😢 Sorry we only support mp3 format currently.')

        key = f'{sound_name}.mp3'
        if _check_exists_in_s3(bucket=BUCKET, key=key):
            logging.error(f'🚫 Sound \'{sound_name}\' already exists, please choose a different name.')
        else:
            try:
                response = s3_client.upload_file(file_path, Bucket=BUCKET, Key=key)
                logging.info(f'🎉 Upload succeeded! You can now create your own Alarm 🛎 with \n `dingpy.ding(\'{sound_name}\')`')
            except ClientError as e:
                logging.error(f'❌ Error uploading audio file \'{sound_name}\' to s3 bucket: {e}')


    @staticmethod
    def _delete_alarm(sound_name : str):
        '''
        Allow user to delete custom uploaded alarm sounds.

        Args:
            sound_name: name of the alarm to delete, without the '.mp3' extension.
        '''
        key = f'{sound_name}.mp3'
        if sound_name in PRE_LOADED_ALARMS:
            logging.error(f'🚫 \'{sound_name}\' is a pre-loaded alarm sound that can\'t be deleted.')

        if _check_exists_in_s3(bucket=BUCKET, key=key):
            s3_client.delete_object(Bucket=BUCKET, Key=key)
            logging.info(f'✅ Successfully deleted alarm \'{sound_name}\' from s3 bucket.')
        else:
            logging.error(f'❌ Alarm file {sound_name}.mp3 doesn\'t exist in s3 bucket')


def _check_exists_in_s3(bucket: str, key: str) -> bool:
    '''
    Check if a key exists in the given bucket.
    '''
    try:
        s3_client.head_object(Bucket=BUCKET, Key=key)
    except ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


def _get_s3_keys(bucket: str) -> List[str]:
    '''
    Get a list of keys in an S3 bucket.
    '''
    keys = []
    resp = s3_client.list_objects_v2(Bucket=bucket)
    for obj in resp['Contents']:
        keys.append(obj['Key'])
    return keys


Alarm = MyAlarm()


def ding(sound: str='japanese_temple_bell', s3: bool=False, path: str=None) -> None:
    if path:
        Alarm._ding_from_local(path=path)
    elif sound and not s3:
        Alarm._ding_from_library(sound=sound)
    elif sound and s3:
        Alarm._ding_from_s3(sound=sound)


def list_alarms(all: bool=False) -> None:
    # return list of 10 pre-loaded alarms
    if not all:
        print('All available alarm sounds include: 🛎')
        for _ in PRE_LOADED_ALARMS:
            print(f'- \'{_}\'')
    # if checking for all available alarms, ls s3 bucket
    else:
        Alarm._list_alarms()


def upload_alarm(file_path: str, sound_name : str) -> None:
    Alarm._upload_alarm(file_path, sound_name)


def delete_alarm(sound_name: str) -> None:
    Alarm._delete_alarm(sound_name)

