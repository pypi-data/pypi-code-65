"""SFTPProcessor"""
import os
from ftpsync.constants import Common
from ftpsync.rest_driver import DataConfigUtil
from ftpsync.ftp_util import FTPUtility


class SFTPProcessor:
    """Takes care of SFTP files upload and download"""

    def __init__(self):
        self.processed_files_list = []
        self.unprocessed_files_list = []

    def get_files(self, config):
        """Get SFTP files"""

        source_dir = os.path.join('/', config['source'])
        print(source_dir)
        local_dest_dir_prefix = str(config['client_id']) + "/" + str(config['config_id'])
        local_dest_dir = os.path.join(local_dest_dir_prefix, config['source'])

        # check this files process status
        self.processed_files_list = DataConfigUtil.get_process_status_by_config_id(config['config_id'])
        sftp = FTPUtility.get_sftp_connection(config['host_name'], config['username'],
                                              config['password'])
        self._sync_r(sftp, source_dir, local_dest_dir)
        sftp.close()
        return self.unprocessed_files_list

    def _sync_r(self, sftp, remote_dir, local_dir):
        """
            Recursively sync the sftp contents starting at remote dir to the local dir and return the number of files synced.
            :param sftp:        Connection to the sftp server.
            :param remote_dir:  Remote dir to start sync from.
            :param local_dir:   To sync to.
            :return             The number of files synced.
            """
        files_synced = 0
        for item in sftp.listdir(remote_dir):
            remote_dir_item = os.path.join(remote_dir, item)
            local_dir_item = os.path.join(local_dir, item)
            if sftp.isfile(remote_dir_item):
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)
                if self._should_sync_file(sftp, remote_dir_item, local_dir_item):
                    if remote_dir_item not in self.processed_files_list:
                        print('sync {} => {}'.format(remote_dir_item, local_dir_item))
                        sftp.get(remote_dir_item, local_dir_item, preserve_mtime=True)
                        self.unprocessed_files_list.append(remote_dir_item)
                    files_synced += 1
            else:
                files_synced += self._sync_r(sftp, remote_dir_item, local_dir_item)
        return files_synced

    def _should_sync_file(self, sftp, remote_file_path, local_file_path):
        """
        If the remote_file should be synced - if it was not downloaded or it is out of sync with the remote version.
        :param sftp:                Connection to the sftp server.
        :param remote_file_path:    Remote file path.
        :param local_file_path:     Local file path.
        """
        if not os.path.exists(local_file_path):
            return True
        else:
            remote_attr = sftp.lstat(remote_file_path)
            local_stat = os.stat(local_file_path)
            return remote_attr.st_size != local_stat.st_size or remote_attr.st_mtime != local_stat.st_mtime

    @staticmethod
    def put_files(config, file_path):
        """Upload local files to SFTP server"""

        success = {}
        dest_path = ''
        local_file_name = ''
        try:
            local_file_name = file_path.replace("/", "|")
            dir_path = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)

            dest_path = os.path.join(config['dest'], dir_path)
            local_file = open(local_file_name, "rb")

            sftp = FTPUtility.get_sftp_connection(config['host_name'], config['username'],
                                                config['password'])

            SFTPProcessor._mkdir_p(sftp, dest_path)

            sftp.put(local_file, preserve_mtime=True)

            sftp.close()
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
    def _mkdir_p(sftp, remote_directory):
        """Change to this directory, recursively making new folders if needed.
        Returns True if any folders were created."""
        if remote_directory == '/':
            # absolute path so change directory to root
            sftp.chdir('/')
            return
        if remote_directory == '':
            # top-level relative directory must exist
            return
        try:
            sftp.chdir(remote_directory)  # sub-directory exists
        except IOError:
            dirname, basename = os.path.split(remote_directory.rstrip('/'))
            SFTPProcessor._mkdir_p(sftp, dirname)  # make parent directories
            sftp.mkdir(basename)  # sub-directory missing, so created it
            sftp.chdir(basename)
            return True






