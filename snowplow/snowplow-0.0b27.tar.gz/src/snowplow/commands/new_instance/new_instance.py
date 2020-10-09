import os
import boto3
import time
import subprocess
import json
import string
from ...core import Utils


class NewInstance:
    DEFAULT_ZONE = 'us-east-1f'
    DEFAULT_DEVICE = '/dev/xvda'

    def __init__(self, ec2_instance_id, bucket_name, size, zone=DEFAULT_ZONE, buckets_root_dir=None, profile=None):
        self.ec2_instance_id = ec2_instance_id
        self.bucket_name = bucket_name
        self.size = size
        self.zone = zone
        self.profile = profile
        self._buckets_root_dir = buckets_root_dir or '/snowball/buckets'
        self.ec2_device = None
        self.local_device = None
        self._set_devices()
        self.volume = None
        self.volume_id = None
        self.attachment = None
        self._session = None
        self._client = None

    def execute(self):
        # /snowball/buckets/<bucket-name>/data
        Utils.ensure_dirs(self.data_dir())
        print('Created bucket data directory: {0}'.format(self.data_dir()))

        self._session = boto3.Session(profile_name=self.profile)
        self._client = self._session.client('ec2')

        self._create_volume()
        self._attach_volume()
        self._write_config()
        print('')
        print('Finished')

    def buckets_root_dir(self):
        """Get the path to where the buckets will be mounted."""
        return self._buckets_root_dir

    def bucket_dir(self):
        """Get the path to this buckets directory.
            /snowball/buckets/<bucket-name>
        """
        return os.path.join(self.buckets_root_dir(), self.bucket_name)

    def mount_dir(self):
        """Get the path to this buckets mounted directory.
            /snowball/buckets/<bucket-name>/mnt
        """
        return os.path.join(self.bucket_dir(), 'mnt')

    def data_dir(self):
        """Get the path to this buckets data directory.
            /snowball/buckets/<bucket-name>/mnt/data
        """
        return os.path.join(self.mount_dir(), 'data')

    def logs_dir(self):
        """Get the path to where the logs will be stored.
            /snowball/buckets/<bucket-name>/mnt/logs
        """
        return os.path.join(self.mount_dir(), 'logs')

    def _config_filename(self):
        return os.path.join(self.bucket_dir(), 'config.json')

    def _mount_script_filename(self):
        return os.path.join(self.bucket_dir(), 'mount.sh')

    def _umount_script_filename(self):
        return os.path.join(self.bucket_dir(), 'umount.sh')

    def _mkfs_script_filename(self):
        return os.path.join(self.bucket_dir(), 'mkfs.sh')

    def _s3sync_script_filename(self):
        return os.path.join(self.bucket_dir(), 's3sync.sh')

    def _synupload_script_filename(self):
        return os.path.join(self.bucket_dir(), 'syn-upload.sh')

    def _syncompare_script_filename(self):
        return os.path.join(self.bucket_dir(), 'syn-compare.sh')

    def _write_config(self):
        # /snowball/buckets/<bucket-name>/config.json
        config_path = self._config_filename()
        jconfig = {
            'Path': self.bucket_dir(),
            'Ec2InstanceId': self.ec2_instance_id,
            'BucketName': self.bucket_name,
            'Size': self.size,
            'Zone': self.zone,
            'VolumeId': self.volume_id,
            'Ec2Device': self.ec2_device,
            'LocalDevice': self.local_device
        }
        with open(config_path, mode='w') as f:
            f.write(json.dumps(jconfig))
        print('Configuration written to: {0}'.format(config_path))

        # /snowball/buckets/<bucket-name>/mount.sh
        self._write_script_file(self._mount_script_filename(),
                                'mount {0} {1}'.format(self.local_device, self.mount_dir()))

        # /snowball/buckets/<bucket-name>/umount.sh
        self._write_script_file(self._umount_script_filename(),
                                'umount {0}'.format(self.local_device))

        # /snowball/buckets/<bucket-name>/mkfs.sh
        self._write_script_file(self._mkfs_script_filename(),
                                'mkfs -t ext4 {0}'.format(self.local_device))

        # /snowball/buckets/<bucket-name>/s3sync.sh
        self._write_script_file(self._s3sync_script_filename(),
                                'aws s3 sync s3://{0} {1}'.format(self.bucket_name, self.data_dir()))

        # /snowball/buckets/<bucket-name>/syn-upload.sh
        self._write_script_file(self._synupload_script_filename(),
                                'synapse-uploader ENTITY_ID {0} --cache-dir {1} --log-dir {2}'.format(self.data_dir(),
                                                                                                      self.mount_dir(),
                                                                                                      self.logs_dir()))

        # /snowball/buckets/<bucket-name>/syn-compare.sh
        self._write_script_file(self._syncompare_script_filename(),
                                'synapse-downloader ENTITY_ID {0} --compare --log-dir {1}'.format(self.data_dir(),
                                                                                                  self.logs_dir()))

        self._format_and_mount_bucket()

    def _write_script_file(self, file_path, *lines):
        with open(file_path, mode='w') as f:
            f.writelines(lines)
        print('Created script: {0}'.format(file_path))
        os.chmod(file_path, 0o775)

    def _format_and_mount_bucket(self):
        mkfs_sh_path = self._mkfs_script_filename()
        mount_sh_path = self._mount_script_filename()

        has_error = False
        try:
            for script_path in [mkfs_sh_path, mount_sh_path]:
                print('Running: {0}'.format(script_path))
                script_result = subprocess.run(script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if script_result.returncode != 0:
                    print('Failure: {0}'.format(script_path))
                    has_error = True
                    print(script_result.stdout)
                    print(script_result.stderr)
                    break
                else:
                    print('Success: {0}'.format(script_path))
        except Exception as ex:
            print('Error running scripts: {0}'.format(ex))
            has_error = True

        if has_error:
            Utils.eprint('Error formatting and mounting bucket.')
        else:
            print('Bucket formatted and mounted successfully: {0}'.format(self.data_dir()))

    def _get_local_devices(self):
        device_names = []
        j = json.loads(subprocess.run(['lsblk', '-J'], stdout=subprocess.PIPE).stdout)

        for device in j.get('blockdevices', []):
            device_names.append(device['name'])

        device_names.sort()
        return device_names

    def _set_devices(self):
        """Get the next EBS device path for the local system.

        Returns:
            String
        """
        local_devices = self._get_local_devices()
        last_device = local_devices[-1]

        last_device_number = int(last_device[4])
        next_number = last_device_number + 1
        if next_number > 25:
            raise ValueError('Next device number exceeds 25')

        next_device = '/dev/xvd{0}'.format(string.ascii_lowercase[next_number])

        self.ec2_device = next_device
        self.local_device = '/dev/{0}{1}{2}'.format(last_device[:4], next_number, last_device[5:])

    def _create_volume(self):
        print('Creating EBS volume in zone: {0}, size: {1} GiBs, Encrypted, on device: {2}...'.format(self.zone,
                                                                                                      self.size,
                                                                                                      self.ec2_device))
        self.volume = self._client.create_volume(
            AvailabilityZone=self.zone,
            Encrypted=True,
            Size=self.size,
            TagSpecifications=[{
                'ResourceType': 'volume',
                'Tags': [
                    {'Key': 'Name',
                     'Value': '{0} on {1} -> {2}'.format(self.bucket_name, self.ec2_device, self.local_device)},
                    {'Key': 'BUCKET_NAME', 'Value': self.bucket_name}
                ]
            }])
        self.volume_id = self.volume.get('VolumeId')
        self._wait_for_volume_available()

    def _attach_volume(self):
        print('Attaching volume: {0} to EC2 instance: {1} on device: {2}'.format(self.volume_id,
                                                                                 self.ec2_instance_id,
                                                                                 self.ec2_device))
        self._client.attach_volume(
            Device=self.ec2_device,
            InstanceId=self.ec2_instance_id,
            VolumeId=self.volume_id
        )
        self._wait_for_volume_attached()

    def _wait_for_volume_available(self):
        # This will try for 5 minutes.
        max_tries = 100
        sleep_time = 3
        tries = 0
        while True:
            tries += 1
            volume = self._get_volume_status_info()
            # creating | available | in-use | deleting | deleted | error
            volume_state = volume.get('State')
            print('  Volume State: {0}'.format(volume_state))

            if volume_state in ['error', 'deleting', 'deleted']:
                raise Exception('Failed to create volume: {0}, state is: {1}'.format(self.volume_id, volume_state))
            elif volume_state == 'available':
                self.volume = volume
                return
            elif tries >= max_tries:
                raise Exception('Timed out waiting for create volume: {0}'.format(self.volume_id))
            else:
                time.sleep(sleep_time)

    def _wait_for_volume_attached(self):
        # This will try for 5 minutes.
        max_tries = 100
        sleep_time = 3
        tries = 0
        while True:
            tries += 1
            volume = self._get_volume_status_info()
            attachment = next((a for a in volume.get('Attachments') if a.get('VolumeId') == self.volume_id), None)
            if attachment:
                # attaching | attached | detaching | detached | busy
                attach_state = attachment.get('State')
                print('  Attatchment State: {0}'.format(attach_state))
            else:
                attach_state = None

            if attach_state in ['attaching', 'busy']:
                time.sleep(sleep_time)
            elif attach_state == 'attached':
                self.attachment = attachment
                return
            elif tries >= max_tries:
                raise Exception('Timed out waiting for volume: {0} to attach to {1}.'.format(self.volume_id))
            else:
                time.sleep(sleep_time)

    def _get_volume_status_info(self):
        response = self._client.describe_volumes(
            VolumeIds=[self.volume_id]
        )
        volume = next((v for v in response.get('Volumes') if v.get('VolumeId') == self.volume_id), None)
        return volume
