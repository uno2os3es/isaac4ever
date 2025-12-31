# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

from __future__ import print_function
import os.path
import base64
from email import message_from_bytes

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope: read-only Gmail access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    creds = None

    # The token.json stores user access and refresh tokens after first login.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials, ask user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Get list of messages
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])

    print(f'Found {len(messages)} emails.')

    for msg in messages:
        msg_id = msg['id']
        msg_data = (
            service.users()
            .messages()
            .get(userId='me', id=msg_id, format='raw')
            .execute()
        )

        raw_data = base64.urlsafe_b64decode(msg_data['raw'])
        email_msg = message_from_bytes(raw_data)

        filename = f'email_{msg_id}.eml'
        with open(filename, 'wb') as f:
            f.write(raw_data)

        print(f'Saved: {filename}')


if __name__ == '__main__':
    main()
