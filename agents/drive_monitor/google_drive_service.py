"""
google_drive_service.py

Provides Google Drive API authentication, file listing & metadata retrieval.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

def get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token_file:
            pickle.dump(creds, token_file)
    return build('drive', 'v3', credentials=creds)

def list_files(folder_id: str) -> dict:
    """
    List all non-trashed files in the given Drive folder.
    Returns a dict mapping file_id -> file_name.
    """
    service = get_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    return {f['id']: f['name'] for f in results.get('files', [])}

def get_file_metadata(file_id: str) -> dict:
    """
    Retrieve metadata including owner, createdTime, and parent folder names.
    """
    service = get_service()
    f = service.files().get(
        fileId=file_id,
        fields="id, name, owners(displayName, emailAddress), createdTime, parents"
    ).execute()
    metadata = {
        "id": f["id"],
        "name": f["name"],
        "owners": [
            {"name": o.get("displayName"), "email": o.get("emailAddress")}
            for o in f.get("owners", [])
        ],
        "createdTime": f["createdTime"],
        "parent_ids": f.get("parents", [])
    }
    # Fetch parent folder names
    folder_names = []
    for pid in metadata["parent_ids"]:
        p = service.files().get(fileId=pid, fields="name").execute()
        folder_names.append(p["name"])
    metadata["folder_names"] = folder_names
    return metadata

from io import BytesIO
from googleapiclient.http import MediaIoBaseDownload

def download_file_text(file_id: str) -> str:
    """
    Streams a text file from Drive into a Python string.
    """
    service = get_service()
    request = service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return fh.getvalue().decode('utf-8')

def download_file(file_id: str, file_name: str, dest_folder: str = 'downloads') -> str:
    """
    Downloads the raw bytes of a file (any type) into downloads/ and
    returns the local path.
    """
    os.makedirs(dest_folder, exist_ok=True)
    local_path = os.path.join(dest_folder, f"{file_id}_{file_name}")
    service = get_service()
    request = service.files().get_media(fileId=file_id)
    with open(local_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return local_path
