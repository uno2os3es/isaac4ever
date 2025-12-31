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


if __name__ == '__main__':
    authenticate_gdrive()
