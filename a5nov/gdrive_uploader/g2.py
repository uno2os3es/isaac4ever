# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import (
    InstalledAppFlow,
)
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import (
    InstalledAppFlow,
)
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def authenticate_gdrive():
    """Authenticate and return the Drive service - Termux compatible"""
    creds = None

    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Termux-compatible flow without browser
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )

            # Use console-based authentication
            creds = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


def create_folder(service, folder_name, parent_id=None):
    """Create a folder in Google Drive and return its ID"""
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }

    if parent_id:
        folder_metadata['parents'] = [parent_id]

    folder = (
        service.files().create(body=folder_metadata, fields='id').execute()
    )
    return folder.get('id')


def folder_exists(service, folder_name, parent_id=None):
    """Check if a folder already exists in the given parent"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(q=query, fields='files(id, name)').execute()
    folders = results.get('files', [])

    return folders[0]['id'] if folders else None


def upload_file(service, file_path, parent_id=None):
    """Upload a file to Google Drive"""
    file_name = os.path.basename(file_path)

    file_metadata = {
        'name': file_name,
        'parents': ([parent_id] if parent_id else []),
    }

    media = MediaFileUpload(file_path, resumable=True)

    file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields='id',
        )
        .execute()
    )

    print(f'Uploaded: {file_name}')
    return file.get('id')


def upload_directory_recursive(
    service,
    local_path,
    drive_parent_id=None,
    base_path=None,
):
    """
    Recursively upload a directory to Google Drive preserving folder structure

    Args:
        service: Google Drive service object
        local_path: Local directory path to upload
        drive_parent_id: Parent folder ID in Google Drive (None for root)
        base_path: Base path for relative path calculation (used internally)
    """
    if base_path is None:
        base_path = local_path

    # Get all items in the current directory
    try:
        items = os.listdir(local_path)
    except PermissionError:
        print(f'Permission denied: {local_path}')
        return

    for item in items:
        item_path = os.path.join(local_path, item)

        if os.path.isdir(item_path):
            # It's a directory - create folder in Drive and recurse
            print(f'Processing folder: {item}')

            # Check if folder already exists
            folder_id = folder_exists(service, item, drive_parent_id)
            if not folder_id:
                folder_id = create_folder(service, item, drive_parent_id)
                print(f'Created folder: {item}')
            else:
                print(f'Folder already exists: {item}')

            # Recursively upload contents
            upload_directory_recursive(
                service,
                item_path,
                folder_id,
                base_path,
            )

        else:
            # It's a file - upload it
            try:
                upload_file(
                    service,
                    item_path,
                    drive_parent_id,
                )
            except Exception as e:
                print(f'Error uploading {item}: {str(e)}')


def get_root_folder_id(service, folder_name):
    """Get or create a root folder for the upload"""
    # Check if folder already exists in root
    folder_id = folder_exists(service, folder_name)
    if folder_id:
        print(f'Using existing folder: {folder_name}')
        return folder_id
    else:
        print(f'Creating new folder: {folder_name}')
        return create_folder(service, folder_name)


def main():
    """Main function to run the upload process"""

    # Configuration
    LOCAL_DIRECTORY = '/sdcard/DCIM'

    if not os.path.exists(LOCAL_DIRECTORY):
        print('Error: The specified directory does not exist.')
        return

    if not os.path.isdir(LOCAL_DIRECTORY):
        print('Error: The specified path is not a directory.')
        return

    # Get folder name for Google Drive
    folder_name = os.path.basename(os.path.abspath(LOCAL_DIRECTORY))
    use_custom_name = 'n'  # input(f"Use '{folder_name}' as folder name in Google Drive? (y/n): ").strip().lower()

    if use_custom_name != 'y':
        folder_name = (
            'YASNA'  # input("Enter folder name for Google Drive: ").strip()
        )

    try:
        # Authenticate and get Drive service
        print('Authenticating with Google Drive...')
        service = authenticate_gdrive()

        # Create root folder in Google Drive
        print('Setting up Google Drive folder...')
        root_folder_id = get_root_folder_id(service, folder_name)

        # Start recursive upload
        print(
            f"Starting upload from '{LOCAL_DIRECTORY}' to Google Drive folder '{folder_name}'..."
        )
        upload_directory_recursive(
            service,
            LOCAL_DIRECTORY,
            root_folder_id,
        )

        print('Upload completed successfully!')

    except Exception as e:
        print(f'An error occurred: {str(e)}')


if __name__ == '__main__':
    main()
