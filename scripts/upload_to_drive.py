# upload_to_drive.py
import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# The token URI is always the same for Google's OAuth 2.0
TOKEN_URI = "https://oauth2.googleapis.com/token"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


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


def escape_query_value(value):
    """Escape a value used inside a Google Drive API query string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def get_or_create_folder(service, parent_folder_id, folder_name):
    """Return the ID of a named child folder, creating it when necessary."""
    escaped_folder_name = escape_query_value(folder_name)
    escaped_parent_id = escape_query_value(parent_folder_id)
    query = (
        f"name='{escaped_folder_name}' and "
        f"mimeType='{FOLDER_MIME_TYPE}' and "
        f"'{escaped_parent_id}' in parents and trashed=false"
    )
    response = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        pageSize=1
    ).execute()
    existing_folders = response.get('files', [])

    if existing_folders:
        folder_id = existing_folders[0]['id']
        print(f"Using existing folder '{folder_name}' (ID: {folder_id}).")
        return folder_id

    print(f"Folder '{folder_name}' not found. Creating it...")
    folder = service.files().create(
        body={
            'name': folder_name,
            'mimeType': FOLDER_MIME_TYPE,
            'parents': [parent_folder_id]
        },
        fields='id'
    ).execute()
    folder_id = folder['id']
    print(f"Folder created (ID: {folder_id}).")
    return folder_id


def upload_file(service, file_path, folder_id):
    """Uploads a file to a specific folder, updating it if it already exists."""
    file_name = os.path.basename(file_path)

    try:
        # Check if the file already exists in this folder
        escaped_file_name = escape_query_value(file_name)
        escaped_folder_id = escape_query_value(folder_id)
        query = (
            f"name='{escaped_file_name}' and "
            f"'{escaped_folder_id}' in parents and trashed=false"
        )
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
    if len(sys.argv) not in (3, 4):
        print(
            "Usage: python upload_to_drive.py <file_to_upload> "
            "<gdrive_folder_id> [subfolder_name]"
        )
        sys.exit(1)

    file_to_upload = sys.argv[1]
    folder_id = sys.argv[2]
    subfolder_name = sys.argv[3] if len(sys.argv) == 4 else None

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    if subfolder_name:
        try:
            folder_id = get_or_create_folder(
                service,
                folder_id,
                subfolder_name
            )
        except HttpError as error:
            print(f"An error occurred while preparing the folder: {error}")
            sys.exit(1)

    upload_file(service, file_to_upload, folder_id)
