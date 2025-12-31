# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import pickle
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def authenticate_gdrive():
    """Authenticate and return the Drive service - Manual method for Termux"""
    creds = None

    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f'Token refresh failed: {e}')
                # If refresh fails, delete token file and re-authenticate
                if os.path.exists('token.pickle'):
                    os.remove('token.pickle')
                return authenticate_gdrive()
        else:
            if not os.path.exists('credentials.json'):
                print('Error: credentials.json file not found!')
                print(
                    'Please download credentials.json from Google Cloud Console'
                )
                print('and place it in the current directory.')
                sys.exit(1)

            # Manual authentication flow for Termux
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )

            print('\n' + '=' * 50)
            print('GOOGLE OAUTH AUTHENTICATION')
            print('=' * 50)
            print('Since Termux cannot open a browser automatically,')
            print('please follow these steps:')
            print('\n1. Open the following URL in ANY web browser')
            print('   (on your phone, computer, or any device):')
            print('\n   ' + flow.authorization_url()[0])
            print(
                "\n2. If you see a 'Google hasn’t verified this app' warning:"
            )
            print("   - Click 'Advanced'")
            print("   - Click 'Go to [Your App Name] (unsafe)'")
            print('\n3. Log in with your Google account if needed')
            print('4. Grant the requested permissions')
            print('5. You will get an authorization code')
            print('6. Copy that code and paste it below')
            print('=' * 50)

            auth_code = input('\nEnter authorization code: ').strip()

            try:
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                print('✓ Authentication successful!')
            except Exception as e:
                print(f'✗ Authentication failed: {e}')
                print('Please check the authorization code and try again.')
                sys.exit(1)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print('✓ Credentials saved to token.pickle')

    return build('drive', 'v3', credentials=creds)


def create_folder(service, folder_name, parent_id=None):
    """Create a folder in Google Drive and return its ID"""
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }

    if parent_id:
        folder_metadata['parents'] = [parent_id]

    try:
        folder = (
            service.files().create(body=folder_metadata, fields='id').execute()
        )
        return folder.get('id')
    except HttpError as error:
        print(f'Error creating folder {folder_name}: {error}')
        return None


def folder_exists(service, folder_name, parent_id=None):
    """Check if a folder already exists in the given parent"""
    # Escape single quotes in folder name
    safe_folder_name = folder_name.replace("'", "\\'")
    query = f"name='{safe_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    try:
        results = (
            service.files().list(q=query, fields='files(id, name)').execute()
        )
        folders = results.get('files', [])

        return folders[0]['id'] if folders else None
    except HttpError as error:
        print(f'Error checking folder existence: {error}')
        return None


def upload_file(service, file_path, parent_id=None):
    """Upload a file to Google Drive"""
    file_name = os.path.basename(file_path)

    # Check file size and skip if too large or inaccessible
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            print(f'Skipping empty file: {file_name}')
            return None

        # Convert bytes to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if file_size < 1024.0:
                size_str = f'{file_size:.1f} {unit}'
                break
            file_size /= 1024.0
        else:
            size_str = f'{file_size:.1f} TB'

    except (OSError, IOError) as e:
        print(f'Cannot access {file_name}: {e}')
        return None

    file_metadata = {
        'name': file_name,
        'parents': [parent_id] if parent_id else [],
    }

    try:
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

        print(f'✓ Uploaded: {file_name} ({size_str})')
        return file.get('id')
    except HttpError as error:
        print(f'✗ Error uploading {file_name}: {error}')
        return None
    except Exception as e:
        print(f'✗ Unexpected error uploading {file_name}: {e}')
        return None


def upload_directory_recursive(
    service, local_path, drive_parent_id=None, base_path=None
):
    """
    Recursively upload a directory to Google Drive preserving folder structure
    """
    if base_path is None:
        base_path = local_path

    # Get all items in the current directory
    try:
        items = os.listdir(local_path)
    except PermissionError:
        print(f'✗ Permission denied: {local_path}')
        return
    except FileNotFoundError:
        print(f'✗ Directory not found: {local_path}')
        return
    except Exception as e:
        print(f'✗ Error accessing {local_path}: {e}')
        return

    file_count = 0
    folder_count = 0

    for item in items:
        item_path = os.path.join(local_path, item)

        # Skip hidden files and directories
        if item.startswith('.'):
            continue

        if os.path.isdir(item_path):
            # It's a directory - create folder in Drive and recurse
            print(f'📁 Processing folder: {item}')

            # Check if folder already exists
            folder_id = folder_exists(service, item, drive_parent_id)
            if not folder_id:
                folder_id = create_folder(service, item, drive_parent_id)
                if folder_id:
                    print(f'✓ Created folder: {item}')
                    folder_count += 1
                else:
                    print(f'✗ Failed to create folder: {item}')
                    continue
            else:
                print(f'✓ Folder already exists: {item}')

            # Recursively upload contents
            sub_file_count, sub_folder_count = upload_directory_recursive(
                service, item_path, folder_id, base_path
            )
            file_count += sub_file_count
            folder_count += sub_folder_count

        else:
            # It's a file - upload it
            if upload_file(service, item_path, drive_parent_id):
                file_count += 1

    return file_count, folder_count


def get_root_folder_id(service, folder_name):
    """Get or create a root folder for the upload"""
    # Check if folder already exists in root
    folder_id = folder_exists(service, folder_name)
    if folder_id:
        print(f'✓ Using existing folder: {folder_name}')
        return folder_id
    else:
        print(f'📁 Creating new folder: {folder_name}')
        return create_folder(service, folder_name)


def check_termux_environment():
    """Check if running in Termux environment and set up paths accordingly"""
    # Check common Termux paths
    termux_paths = ['/sdcard', '/storage/emulated/0', '/storage/self/primary']

    for path in termux_paths:
        if os.path.exists(path):
            return path
    return None


def main():
    """Main function to run the upload process"""

    print('=== Google Drive Uploader for Termux ===\n')

    # Auto-detect Termux environment
    termux_base = check_termux_environment()
    if termux_base:
        print('✓ Termux environment detected')
        # Try multiple possible DCIM locations
        possible_dcim_paths = [
            os.path.join(termux_base, 'DCIM'),
            os.path.join(termux_base, 'Pictures'),
            os.path.join(termux_base, 'Download'),
            termux_base,  # Use root as fallback
        ]

        for dcim_path in possible_dcim_paths:
            if os.path.exists(dcim_path) and os.path.isdir(dcim_path):
                LOCAL_DIRECTORY = dcim_path
                print(f'✓ Using directory: {LOCAL_DIRECTORY}')
                break
        else:
            LOCAL_DIRECTORY = possible_dcim_paths[0]  # Use first as default
            print(f'⚠  Using default directory: {LOCAL_DIRECTORY}')
    else:
        print('⚠  Running in non-Termux environment')
        LOCAL_DIRECTORY = '/sdcard/DCIM'

    # Check if directory exists
    if not os.path.exists(LOCAL_DIRECTORY):
        print(f"Error: Directory '{LOCAL_DIRECTORY}' does not exist.")
        print('\nAvailable directories:')
        try:
            current_dir = '.'
            for item in os.listdir(current_dir):
                if os.path.isdir(item):
                    print(f'  📁 {item}')
        except Exception as e:
            print(f'  (Cannot list directories: {e})')
        return

    if not os.path.isdir(LOCAL_DIRECTORY):
        print(f"Error: '{LOCAL_DIRECTORY}' is not a directory.")
        return

    print(f'Source directory: {LOCAL_DIRECTORY}')

    # Get folder name for Google Drive
    folder_name = os.path.basename(os.path.abspath(LOCAL_DIRECTORY))
    use_default = (
        input(f"Use '{folder_name}' as folder name in Google Drive? (Y/n): ")
        .strip()
        .lower()
    )

    if use_default in ['n', 'no']:
        folder_name = input('Enter folder name for Google Drive: ').strip()
        if not folder_name:
            folder_name = 'Termux_Backup'

    try:
        # Authenticate and get Drive service
        print('\n🔐 Authenticating with Google Drive...')
        service = authenticate_gdrive()

        # Create root folder in Google Drive
        print('📁 Setting up Google Drive folder...')
        root_folder_id = get_root_folder_id(service, folder_name)

        if not root_folder_id:
            print('✗ Failed to create/get root folder. Exiting.')
            return

        # Start recursive upload
        print(
            f"\n🚀 Starting upload from '{LOCAL_DIRECTORY}' to Google Drive folder '{folder_name}'...\n"
        )
        file_count, folder_count = upload_directory_recursive(
            service, LOCAL_DIRECTORY, root_folder_id
        )

        print('\n' + '=' * 50)
        print('✅ UPLOAD COMPLETED SUCCESSFULLY!')
        print(f'📁 Folders processed: {folder_count}')
        print(f'📄 Files uploaded: {file_count}')
        print('=' * 50)

    except KeyboardInterrupt:
        print('\n⚠  Upload interrupted by user')
    except Exception as e:
        print(f'\n❌ An error occurred: {str(e)}')
        import traceback

        traceback.print_exc()
        print(
            '\nIf this is an authentication error, try deleting token.pickle and re-authenticating.'
        )


if __name__ == '__main__':
    main()
