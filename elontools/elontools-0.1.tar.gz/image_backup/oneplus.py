import os
import time
from pyexiv2 import Image
import imghdr
import json
import shutil
import subprocess

# 对于指定的文件路径，生成带序列号的路径:
def handle_duplicate_path(path):
    i = 0
    dir_name = os.path.dirname(path)
    es_name = '.'+os.path.basename(path).split('.')[-1]
    file_name = os.path.basename(path).replace(es_name, '')

    new_in_path = path
    while os.path.exists(new_in_path):
        i = i+1
        new_in_path = os.path.join(dir_name, file_name+'_{0}{1}'.format(i, es_name))
    # print(new_in_path)
    return new_in_path

    code = ""
    for i in range(4):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        code += ch
    print(code)


def pull_from_android():
    download_path = os.path.expanduser('~/downloads/照片备份-OnePlus5【{}】'.format(time.strftime('%Y-%m-%d', time.localtime())))

    if os.path.exists(download_path):
        shutil.rmtree(download_path)


    audio_record = os.path.join(download_path, '录音')
    if not os.path.exists(audio_record):
        os.makedirs(audio_record)

    os.chdir(audio_record)
    os.system('adb pull /sdcard/Record')

    audio_record = os.path.join(download_path, '图片和视频')
    if not os.path.exists(audio_record):
        os.makedirs(audio_record)
    os.chdir(audio_record)
    os.system('adb pull /sdcard/Pictures/Screenshots')  # 屏幕截图
    os.system('adb pull /sdcard/DCIM/Camera')  # 相机照片和视频
    os.system('adb pull /sdcard/tencent/MicroMsg/WeiXin')  # 微信图片

    return download_path


def zip_dir_with_pwd(dir_path, pwd):
    # ori_path = os.getcwd()
    os.chdir(dir_path)
    zip_name = os.path.basename(dir_path)+'.zip'
    os.system('zip -r -m ../{0} . -P {1} -s 1000m'.format(zip_name, pwd))
    os.chdir(os.path.abspath('../'))
    shutil.rmtree(dir_path)
    


def modify_file_name_by_exif(path):
    import shutil
    for r, ds, fs in os.walk(path):
        for f in fs:
            file_path = os.path.join(r, f)
            if '.' not in f: 
                continue
            es_name = '.'+file_path.split('.')[-1]

            if f.lower().endswith(('.mov', '.mp4')):
                ret = json.loads(os.popen('exiftool -j {}'.format(file_path)).read())
                print(ret[0]['MediaCreateDate'])
                time_str = ret[0]['MediaCreateDate']

                time_stamp = time.mktime(time.strptime(time_str, '%Y:%m:%d %H:%M:%S'))
                new_path = os.path.join(r, str(int(time_stamp))+es_name)
                new_path = handle_duplicate_path(new_path)
                shutil.copy2(file_path, new_path)
                os.remove(file_path)

            if f.lower().endswith(('.png', '.jpeg', '.jpg')):
                if imghdr.what(file_path) == 'png' or imghdr.what(file_path) == 'jpeg':
                    with Image(file_path) as img:
                        res = img.read_exif()
                        if 'Exif.Photo.DateTimeOriginal' not in res:
                            print(file_path)
                        else:
                            time_str = res['Exif.Photo.DateTimeOriginal']
                            print(time_str)
                            time_stamp = time.mktime(time.strptime(time_str, '%Y:%m:%d %H:%M:%S'))
                            new_path = os.path.join(r, str(int(time_stamp))+es_name)
                            new_path = handle_duplicate_path(new_path)
                            shutil.copy2(file_path, new_path)
                            os.remove(file_path)



def run():
    # if 'command not found' in os.popen("exiftoo").read():
    #     print('未安装exiftool: https://exiftool.org/')
    #     exit(0)

    with open(os.devnull, 'wb') as devnull:
            try:
                subprocess.check_call('exiftool', shell=True, stdout=devnull, stderr=subprocess.STDOUT)
            except Exception as e:
                print('未安装exiftool: https://exiftool.org/')
                exit(0)
        
    config_file = os.path.expanduser('~/.elon.json')
    if not os.path.exists(config_file):
        pwd = input('输入压缩用密码:')
        with open(config_file,'w') as f:
            json.dump({
                'pwd':pwd,
                },f)

    path = pull_from_android()
    modify_file_name_by_exif(path)
    file_list = [os.path.join(path, f)
                 for f in os.listdir(path)
                 if os.path.isdir(os.path.join(path, f))
                 ]
    

    with open(config_file,'r') as f:
        config = json.load(f)
        for item in file_list:
            zip_dir_with_pwd(item, config['pwd'])
        os.system('open {} -a finder'.format(path))  # 打开文件夹
    print('完成! 分卷解压缩使用Mac端的ezip: https://ezip.awehunt.com/')


if __name__ == '__main__':
    run()
    


