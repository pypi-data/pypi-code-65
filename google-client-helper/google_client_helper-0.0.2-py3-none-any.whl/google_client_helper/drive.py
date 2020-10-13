from io import BytesIO
from time import sleep
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload, HttpError
from .service import GoogleServiceMixin

folder_type = 'application/vnd.google-apps.folder'


class GoogleDrive(GoogleServiceMixin):

    api_name = 'drive'
    api_version = 'v3'
    scopes = ['https://www.googleapis.com/auth/drive']
    credential_name = 'drive'

    def file_list(self, **kwargs):
        if 'fields' not in kwargs:
            kwargs['fields'] = ("nextPageToken, files(id, name, appProperties, webViewLink, "
                                "size, modifiedTime, mimeType, owners, thumbnailLink, md5Checksum)")
        results = self.service.files().list(**kwargs, pageSize=50).execute()
        next_page = results.get('nextPageToken')
        items = results.get('files', [])
        while next_page:
            results = self.service.files().list(**kwargs, pageSize=50, pageToken=next_page).execute()
            next_page = results.get('nextPageToken')
            items = items + results.get('files', [])
        return items

    @staticmethod
    def build_q(name=None, mime_type=None, folder=None, shared_with_me=None, trashed=False):
        search = [f'trashed = {str(trashed).lower()}']
        if name:
            search.append(f"name='{name}'")
        if mime_type:
            search.append(f"mimeType='{mime_type}'")
        if folder:
            if type(folder) == dict:
                search.append(f"'{folder['id']}' in parents")
            else:
                search.append(f"'{folder}' in parents")
        if shared_with_me:
            search.append('sharedWithMe')
        return ' and '.join(search)

    def get_folder(self, folder_path, shared_with_me=False, **kwargs):
        paths = folder_path.split('/')
        next_folder = None
        if shared_with_me:
            q_dict = {'shared_with_me': True}
        elif 'folder' in kwargs:
            q_dict = {'folder': kwargs.pop('folder')}
        else:
            q_dict = {'folder': 'root'}
        for p in paths:
            q_dict.update({'mime_type': folder_type, 'name': p})
            next_folder = self.file_list(q=self.build_q(**q_dict), **kwargs)
            if not next_folder:
                return
            q_dict = {'folder': next_folder[0]}
        if next_folder and len(next_folder) > 0:
            return next_folder[0]

    def get_file(self, name, folder):
        folder_id = self.get_folder(folder)
        file_id = self.file_list(q=self.build_q(name=name, folder=folder_id))[0]['id']
        return self.get_file_from_id(file_id)

    def get_file_from_id(self, file):
        request = self.service.files().get_media(fileId=file['id'])
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh

    def create_folder(self, title, parent):
        body = {'name': title, 'mimeType': folder_type}
        if parent:
            body['parents'] = [parent['id']]
        return self.service.files().create(body=body, fields='id').execute()

    def find_create_folder(self, folder_path, **kwargs):
        folder = self.get_folder(folder_path, **kwargs)
        if folder:
            return folder
        if folder_path.find('/') < 0:
            parent_folder = kwargs['folder']
        else:
            parent_folder = self.get_folder(folder_path[0:folder_path.rfind('/')], **kwargs)
        folder = self.create_folder(folder_path[folder_path.rfind('/') + 1:], parent_folder)
        sleep(5)
        return folder

    def create_file_body(self, body, data_stream):
        if data_stream.getbuffer().nbytes == 0:
            google_file = self.service.files().create(body=body).execute()
        else:
            if body.get('mimeType'):
                media_body = MediaIoBaseUpload(data_stream, mimetype=body['mimeType'], resumable=True)
            else:
                media_body = MediaIoBaseUpload(data_stream, resumable=True)
            try:
                google_file = self.google_execute_retry(self.service.files().create(body=body, media_body=media_body))
            except HttpError:
                self.service = self.get_service_account()
                google_file = self.service.files().create(body=body, media_body=media_body).execute()
        return google_file

    def create_file_stream(self, title, parent_ids, mime_type, data_stream, body=None):
        if body is None:
            body = {}
        body['name'] = title
        if mime_type:
            body['mimeType'] = mime_type
        else:
            body['mimeType'] = '[*/*]'
        if parent_ids:
            body['parents'] = parent_ids
        return self.create_file_body(body, data_stream)

    def create_file(self, title, parent_ids, mime_type, data, body=None):
        return self.create_file_stream(title, parent_ids, mime_type, BytesIO(data), body)

    def get_all_descendants(self, folder_id):
        files_folders = self.file_list(q=self.build_q(folder=folder_id))
        output_files = []
        for f in files_folders:
            if f['mimeType'] == folder_type:
                descendant_files = self.get_all_descendants(f['id'])
                for d in descendant_files:
                    d['tags'] = d.get('tags', []) + [f['name']]
                output_files += descendant_files
            else:
                output_files.append(f)
        return output_files
