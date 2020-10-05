"""FTPProcessor"""
import os
from ftplib import error_perm

from ftpsync.constants import Common
from ftpsync.rest_driver import DataConfigUtil
from ftpsync.ftp_util import FTPUtility


class FTPProcessor:
    """Takes care of FTP files upload and download"""

    def download_file(self, file_path, config):
        """Download FTP files to local machine"""

        success = 0
        ftp = FTPUtility.get_ftp_connection(config['host_name'], config['username'],
                                            config['password'])
        ftp.set_pasv(True)
        dir_loc = '.'
        filename = file_path
        le = file_path.rfind('/')
        if le > 0:
            dir_loc = dir_loc + "/" + file_path[:le]
            filename = file_path[le + 1:]
        ftp.cwd(dir_loc)
        local_file_path = str(config['client_id']) + "/" + str(config['config_id']) + "/" + dir_loc
        filepath = os.path.join(local_file_path, filename)
        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path)
        localfile = open(filepath, 'wb')
        ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
        ftp.close()
        localfile.close()
        success = 1
        return success

    def get_files(self, config):
        """Get FTP files"""

        ftp = FTPUtility.get_ftp_connection(config['host_name'], config['username'],
                                            config['password'])
        ftp.cwd(config['source'])
        ftp.set_pasv(True)
        list_files = self.traverse(ftp, config['source'], [])
        ftp.close()
        # check this files process status
        processed_files_list = DataConfigUtil.get_process_status_by_config_id(config['config_id'])
        unprocessed_files = [x for x in list_files if x not in processed_files_list]
        files = []
        # download
        for unprocessed_file in unprocessed_files:
            success = self.download_file(unprocessed_file, config)
            if success == 1:
                files.append(unprocessed_file)
        return files

    def traverse(self, ftp, k, list_files, depth=0):
        """
        return a recursive listing of an ftp server contents (starting
        from the current directory)

        listing is returned as a recursive dictionary, where each key
        contains a contents of the subdirectory or None if it corresponds
        to a file.

        @param ftp: ftplib.FTP object
        """
        if depth > 10:
            return ['depth > 10']
        level = {}
        for entry in (path for path in ftp.nlst() if path not in ('.', '..')):
            try:
                ftp.cwd(entry)
                s = entry
                if (len(k) != 0):
                    s = k + '/' + entry

                level[entry] = self.traverse(ftp, s, list_files, depth + 1)
                ftp.cwd('..')
            except error_perm:
                level[entry] = None
                s = entry
                if (len(k) != 0):
                    s = k + '/' + entry
                    list_files.append(s)
        return list_files

    @staticmethod
    def put_files(config, file_path):
        """Upload local files to FTP server"""

        success = {}
        dest_path = ''
        local_file_name = ''
        try:
            local_file_name = file_path.replace("/", "|")
            ftp = FTPUtility.get_ftp_connection(config['host_name'], config['username'],
                                                config['password'])
            ftp.cwd(config['dest'])
            dir_path = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            FTPProcessor.mk_ftp_dir(ftp, dir_path)
            dest_path = os.path.join(config['dest'], file_path)
            local_file = open(local_file_name, "rb")
            ftp.storbinary('STOR ' + file_name, local_file)
            ftp.quit()
            local_file.close()
            success['status'] = Common.process_status_2.value
            success['msg'] = "Success"
            success['source_path'] = file_path
            success['dest_path'] = dest_path
        except Exception as ex:
            success['status'] = Common.process_status_1.value
            success['msg'] = str(ex)
            success['source_path'] = file_path
            success['dest_path'] = dest_path
        finally:
            FTPUtility.delete_file(local_file_name)
        return success

    @staticmethod
    def mk_ftp_dir(ftp, dir_path):
        d_tmp = dir_path.split("/")
        for dir_loc in d_tmp:
            if FTPProcessor.ftp_directory_exists(ftp, dir_loc) is False:
                ftp.mkd(dir_loc)
            ftp.cwd(dir_loc)

    @staticmethod
    def ftp_directory_exists(ftp, dir_path):
        filelist = []
        ftp.retrlines('LIST', filelist.append)
        for file in filelist:
            if file.split()[-1] == dir_path and file.upper().startswith('D'):
                return True
        return False
