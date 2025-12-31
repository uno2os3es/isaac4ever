# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import pickle
import threading
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import (
    InstalledAppFlow,
)
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class GoogleDriveUploader:
    def __init__(
        self,
        credentials_file='credentials.json',
        token_file='token.pickle',
    ):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self.authenticate()
        self.folder_cache = {}  # Cache for folder IDs

    def authenticate(self):
        creds = None

        # Load existing tokens
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file,
                    self.SCOPES,
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def create_folder(self, folder_name, parent_id=None):
        """Create a folder in Google Drive and return its ID"""
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]

        folder = (
            self.service.files()
            .create(body=folder_metadata, fields='id')
            .execute()
        )

        return folder.get('id')

    def get_or_create_folder(self, folder_path, parent_id=None):
        """Get existing folder ID or create new one"""
        if folder_path in self.folder_cache:
            return self.folder_cache[folder_path]

        folder_name = os.path.basename(folder_path)

        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = (
            self.service.files()
            .list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
            )
            .execute()
        )

        if results['files']:
            folder_id = results['files'][0]['id']
        else:
            folder_id = self.create_folder(folder_name, parent_id)

        self.folder_cache[folder_path] = folder_id
        return folder_id

    def upload_file(self, file_path, parent_folder_id=None):
        """Upload a file to Google Drive"""
        file_name = os.path.basename(file_path)

        # Check if file already exists
        query = f"name='{file_name}'"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"

        results = (
            self.service.files()
            .list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
            )
            .execute()
        )

        # Skip if file already exists
        if results['files']:
            print(f'File already exists: {file_name}')
            return

        file_metadata = {'name': file_name}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        media = MediaFileUpload(
            file_path,
            mimetype='image/jpeg',  # Adjust if needed for other image types
            resumable=True,
        )

        try:
            file = (
                self.service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields='id',
                )
                .execute()
            )

            print(f'Uploaded: {file_name} (ID: {file.get("id")})')
            return file.get('id')
        except Exception as e:
            print(f'Error uploading {file_name}: {str(e)}')

    def recreate_directory_structure(self, base_path, drive_parent_id=None):
        """Recreate the directory structure in Google Drive"""
        structure = {}

        for root, dirs, files in os.walk(base_path):
            # Get relative path from base
            rel_path = os.path.relpath(root, base_path)
            if rel_path == '.':
                rel_path = ''

            # Create folder in Google Drive
            if rel_path:
                folder_parts = rel_path.split(os.sep)
                current_parent = drive_parent_id

                # Create each subfolder in the path
                for i, folder in enumerate(folder_parts):
                    current_path = os.path.join(*folder_parts[: i + 1])
                    if current_path not in structure:
                        structure[current_path] = self.get_or_create_folder(
                            folder, current_parent
                        )
                    current_parent = structure[current_path]

                current_folder_id = current_parent
            else:
                current_folder_id = drive_parent_id

            # Store files with their folder ID
            for file in files:
                if file.lower().endswith(
                    (
                        '.jpg',
                        '.jpeg',
                        '.png',
                        '.gif',
                        '.bmp',
                        '.webp',
                    )
                ):
                    file_path = os.path.join(root, file)
                    yield file_path, current_folder_id

    def upload_directory(
        self,
        source_dir,
        drive_destination_folder_id=None,
    ):
        """Main method to upload directory with structure preservation"""
        print(f'Starting upload from: {source_dir}')

        total_files = sum(
            1
            for root, dirs, files in os.walk(source_dir)
            for f in files
            if f.lower().endswith(
                (
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.gif',
                    '.bmp',
                    '.webp',
                )
            )
        )
        print(f'Found {total_files} image files')

        uploaded_count = 0

        for (
            file_path,
            folder_id,
        ) in self.recreate_directory_structure(
            source_dir,
            drive_destination_folder_id,
        ):
            self.upload_file(file_path, folder_id)
            uploaded_count += 1
            print(f'Progress: {uploaded_count}/{total_files}')

        print(f'Upload completed! {uploaded_count} files uploaded.')


def main():
    # Configuration
    SOURCE_DIR = '/sdcard/DCIM'  # Change this to your source directory
    CREDENTIALS_FILE = 'token.json'
    TOKEN_FILE = 'token.pickle'

    # For Android device access, you might need to adjust the source directory
    # or run this on a computer with the SD card mounted

    uploader = GoogleDriveUploader(CREDENTIALS_FILE, TOKEN_FILE)
    uploader.upload_directory(SOURCE_DIR)


if __name__ == '__main__':
    main()
