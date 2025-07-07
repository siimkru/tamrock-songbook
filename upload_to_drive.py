# upload_to_drive.py
import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_file(service, file_path, folder_id):
    """Uploads a file to a specific folder, updating it if it already exists."""
    file_name = os.path.basename(file_path)

    # Check if the file already exists in the folder
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    media = MediaFileUpload(file_path, mimetype='application/pdf')

    if files:
        # File exists, update it
        file_id = files[0].get('id')
        print(f"File '{file_name}' already exists. Updating it (ID: {file_id})...")
        service.files().update(fileId=file_id, media_body=media).execute()
        print("Update complete.")
    else:
        # File does not exist, create it
        print(f"File '{file_name}' not found. Creating it...")
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print("Upload complete.")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python upload_to_drive.py <file_to_upload> <gdrive_folder_id>")
        sys.exit(1)

    file_to_upload = sys.argv[1]
    folder_id = sys.argv[2]
    credentials_json = os.getenv('GDRIVE_CREDENTIALS')

    if not credentials_json:
        print("Error: GDRIVE_CREDENTIALS environment variable not set.")
        sys.exit(1)

    # The GitHub Action sets up credentials for us, but this script can also work locally
    # if you export the secret as an environment variable.
    import json

    creds_info = json.loads(credentials_json)
    creds = service_account.Credentials.from_service_account_info(creds_info)
    service = build('drive', 'v3', credentials=creds)

    upload_file(service, file_to_upload, folder_id)