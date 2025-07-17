# upload_to_drive.py
import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# The token URI is always the same for Google's OAuth 2.0
TOKEN_URI = "https://oauth2.googleapis.com/token"


def get_credentials():
    """Constructs credentials object from environment variables."""
    client_id = os.getenv('GDRIVE_CLIENT_ID')
    client_secret = os.getenv('GDRIVE_CLIENT_SECRET')
    refresh_token = os.getenv('GDRIVE_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        print(
            "Error: Required environment variables (GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN) are not set.")
        sys.exit(1)

    return Credentials(
        token=None,  # No access token needed, it will be fetched using the refresh token
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret
    )


def upload_file(service, file_path, folder_id):
    """Uploads a file to a specific folder, updating it if it already exists."""
    file_name = os.path.basename(file_path)

    try:
        # Check if the file already exists in this folder
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        existing_files = response.get('files', [])

        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)

        if existing_files:
            # File exists, so update it
            file_id = existing_files[0].get('id')
            print(f"File '{file_name}' already exists. Updating it (ID: {file_id})...")
            service.files().update(
                fileId=file_id,
                media_body=media,
            ).execute()
            print("Update complete.")
        else:
            # File does not exist, so create it
            print(f"File '{file_name}' not found. Creating it...")
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print("Upload complete.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python upload_to_drive.py <file_to_upload> <gdrive_folder_id>")
        sys.exit(1)

    file_to_upload = sys.argv[1]
    folder_id = sys.argv[2]

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    upload_file(service, file_to_upload, folder_id)