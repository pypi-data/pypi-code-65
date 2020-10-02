import os
import shutil
import sys
import fnmatch
import time
import datetime
import re

BASE_DIR = os.getenv("ROOT_FS")


class Box:
    def __init__(self, *args, **kwargs):
        super(Box, self).__init__(*args, **kwargs)
    
    @staticmethod
    def make_dir(path):
        try:
            path = os.path.join(BASE_DIR, path)
            os.makedirs(path)
            return True
        except Exception as e:
            # print(e)
            return False
        
    @staticmethod
    def make_file(file_object, target_path):
        with open(os.path.join(BASE_DIR, target_path), 'wb') as f:
            f.write(file_object)

    @staticmethod
    def list_dirs(path):
        """True for folders, False for files"""
        path = os.path.join(BASE_DIR, path)
        if not os.path.exists(path):
            raise Exception("Path Does not exists.")

        items = os.listdir(path)
        return [
            (
                os.path.join(path, item), 
                True if os.path.isdir(os.path.join(path, item)) else False) 
            for item in items]
    
    @staticmethod
    def get_all_files(path, all_files=[]):
        path = os.path.join(BASE_DIR, path)
        def getfiles(path, all_files):
            if os.path.isfile(path):
                all_files.append(path)
                return path
            items = os.listdir(path)
            for item in items:
                getfiles(os.path.join(path, item), all_files)
            return all_files
        files = getfiles(path, all_files)
        return files
    
    @staticmethod
    def recursive_glob(treeroot, pattern):
        results = []
        for base, dirs, files in os.walk(treeroot):
            goodfiles = fnmatch.filter(files, pattern)
            # goodfiles = fnmatch.filter(map(str.lower, files), pattern.lower())
            gooddirs = fnmatch.filter(dirs, pattern)
            results.extend(os.path.join(base, f) for f in goodfiles)
            results.extend(os.path.join(base, f) for f in gooddirs)
        return results
        
    @staticmethod
    def search(item, path=False, recursive=False):
        if path:
            path = os.path.join(BASE_DIR, path)
        else:
            path = BASE_DIR
        
        results = Box.recursive_glob(path, '*{0}*'.format(item))
        return results
    
    @staticmethod
    def get_metadata(path):
        path = os.path.join(BASE_DIR, path)
        stats = os.stat(path)
        results = {
            "name": os.path.basename(path),
            "size": stats.st_size,
            "created_at": datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%a %b %d, %Y %H:%M:%S'),
            "modified_at": datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%a %b %d, %Y %H:%M:%S'),
        }
        return results
    
    @staticmethod
    def rename(path, new_name):
        path = os.path.join(BASE_DIR, path)
        base_path, name = os.path.split(path)
        os.rename(path, os.path.join(base_path, new_name))
            
    @staticmethod
    def copy(path, dest):
        path = os.path.join(BASE_DIR, path)
        dest = os.path.join(BASE_DIR, dest)
        if os.path.isfile(path):
            shutil.copy2(path, dest)
        if os.path.isdir(path):
            shutil.copytree(path, dest, dirs_exist_ok=True)
    
    @staticmethod
    def delete(path):
        path = os.path.join(BASE_DIR, path)
        if os.path.isfile(path):
            os.remove(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
    
    @staticmethod
    def move(src, dest):
        Box.copy(src, dest)
        Box.delete(src)
